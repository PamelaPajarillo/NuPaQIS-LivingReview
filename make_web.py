"""Build the data files the NuPaQIS website renders from.

This is the "content" half of the content/rendering split: it reuses the same
INSPIRE-backed dataframe that make_nupaqis.py uses for the READMEs, the PDF
and the .bib, and writes it out as JSON.  Nothing here knows anything about
HTML; nothing in web/assets knows anything about INSPIRE.

Run after (or instead of) make_nupaqis.py:

    python3 make_web.py

Output:
    web/data/papers.json      one record per paper
    web/data/categories.json  category names, groups and descriptions
"""

import html as html_module
import json
import os
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
from datetime import date, timezone, datetime

from utils import get_categories, get_dataframe

YAML_FILE = 'NUPAQIS.yaml'
CATEGORIES_YAML = 'NUPAQIS_CATEGORIES.yaml'
OUT_DIR = os.path.join('web', 'data')
WEB_DIR = 'web'
PDF_FILE = 'NUPAQIS.pdf'

PDF_DATE_RE = re.compile(rb'/CreationDate\s*\(D:(\d{8})')


AUTHOR_RE = re.compile(r'<a href="(?P<url>[^"]+)">\s*(?P<name>[^<]+)</a>')

# INSPIRE titles occasionally carry LaTeX text macros that are not maths and
# would otherwise be shown raw, e.g. "D-Wave's {\\tt Advantage} Quantum Annealer".
TEX_FONT_RE = re.compile(r'\{\s*\\(?:tt|it|bf|rm|sf|sc|em)\s+([^{}]*)\}')
TEX_CMD_RE = re.compile(r'\\(?:text|textbf|textit|texttt|emph|mathrm)\{([^{}]*)\}')


# A few INSPIRE titles carry MathML lifted from the journal's own metadata,
# e.g. "ADMX Axion Dark Matter Bounds around <math ...>3.3 μeV</math>". Shown as
# text it reads as tag soup, so it is kept as markup for MathJax to typeset and
# flattened separately for searching and sorting.
MATHML_TAGS = {
    'math', 'mrow', 'mi', 'mo', 'mn', 'ms', 'mtext', 'mspace',
    'msup', 'msub', 'msubsup', 'mover', 'munder', 'munderover',
    'mfrac', 'msqrt', 'mroot', 'mstyle', 'mpadded', 'mphantom',
    'menclose', 'mfenced', 'mtable', 'mtr', 'mtd',
    'mmultiscripts', 'mprescripts', 'none', 'semantics', 'annotation',
}
MATHML_ATTRS = {
    'display', 'displaystyle', 'mathvariant', 'stretchy', 'separator',
    'accent', 'accentunder', 'notation', 'scriptlevel', 'encoding',
    'columnalign', 'rowalign', 'open', 'close', 'width',
}
MATH_RE = re.compile(r'<math\b.*?</math>', re.DOTALL)


def sanitize_mathml(fragment):
    """Return the fragment with only MathML elements and attributes kept."""
    try:
        root = ET.fromstring(fragment)
    except ET.ParseError:
        return None
    if root.tag.split('}')[-1] != 'math':
        return None

    def strip(element):
        element.tag = element.tag.split('}')[-1]
        element.attrib = {name: value for name, value in element.attrib.items()
                          if name.split('}')[-1] in MATHML_ATTRS}
        for child in list(element):
            if child.tag.split('}')[-1] in MATHML_TAGS:
                strip(child)
            else:
                element.remove(child)

    strip(root)
    return ET.tostring(root, encoding='unicode')


def split_mathml(title):
    """Return (plain text, HTML or None) for a title that may contain MathML."""
    if '<math' not in title:
        return title, None

    plain, markup, cursor, usable = [], [], 0, False
    for match in MATH_RE.finditer(title):
        before = title[cursor:match.start()]
        plain.append(before)
        markup.append(html_module.escape(before))

        cleaned = sanitize_mathml(match.group(0))
        try:
            text = ''.join(ET.fromstring(match.group(0)).itertext())
        except ET.ParseError:
            text = ''
        text = re.sub(r'\s+', ' ', text).strip()
        plain.append(text)
        if cleaned:
            markup.append(cleaned)
            usable = True
        else:
            markup.append(html_module.escape(text))
        cursor = match.end()

    plain.append(title[cursor:])
    markup.append(html_module.escape(title[cursor:]))

    flat = re.sub(r'\s+', ' ', ''.join(plain)).strip()
    return flat, (''.join(markup) if usable else None)


def clean_title(title):
    """Strip non-mathematical TeX markup, leaving $...$ untouched."""
    parts = re.split(r'(\$[^$]*\$)', title)
    for position, part in enumerate(parts):
        if part.startswith('$'):
            continue
        part = TEX_FONT_RE.sub(r'\1', part)
        part = TEX_CMD_RE.sub(r'\1', part)
        parts[position] = part
    return ''.join(parts)
POSTED_RE = re.compile(
    r'Posted on <a href="[^"]*">arXiv:[^<]*</a>:</strong>\s*(?P<date>[^\n+]+)')
PUBLISHED_RE = re.compile(
    r'Published in <a href="[^"]*">(?P<journal>[^<]*)</a>:</strong>'
    r'\s*(?P<date>[^\n+]*)')


def split_categories(primary, secondary):
    """Return (primary, [all categories]) from the dataframe's two columns."""
    everything = [primary]
    if secondary and secondary != 'N/A':
        everything += [c.strip() for c in secondary.split(';') if c.strip()]
    # Preserve order, drop repeats.
    return primary, list(dict.fromkeys(everything))


def parse_authors(authors_html, authors_plain):
    authors = [{'name': m.group('name').strip(), 'url': m.group('url')}
               for m in AUTHOR_RE.finditer(authors_html or '')]
    if authors:
        return authors
    # Fall back to the plain-text list if INSPIRE gave us no author records.
    return [{'name': name.strip(), 'url': None}
            for name in (authors_plain or '').split(',') if name.strip()]


def parse_publication(pub_html):
    posted = POSTED_RE.search(pub_html or '')
    published = PUBLISHED_RE.search(pub_html or '')
    return {
        'posted': posted.group('date').strip() if posted else None,
        'journal': published.group('journal').strip() if published else None,
        'published': published.group('date').strip() if published else None,
    }


def paper_types(found):
    """utils.get_dataframe derives these now, so every output agrees."""
    return list(found) if found else ['Research paper']


def build_papers(df):
    papers = []
    for row in df.to_dict('records'):
        nupa_primary, nupa_all = split_categories(row['NUPA_Primary'],
                                                  row['NUPA_Secondary'])
        qis_primary, qis_all = split_categories(row['QIS_Primary'],
                                                row['QIS_Secondary'])
        publication = parse_publication(row['Publish_Info_md'])
        title_text, title_html = split_mathml(clean_title(row['title']))
        arxiv = row['eprint'] if row['eprint'] != 'nan' else None
        doi = row['doi'] if row['doi'] != 'nan' else None
        papers.append({
            'id': row['ID'],
            'key': row['bibtex_tag'],
            'title': title_text,
            'title_html': title_html,
            'year': int(row['year']) if str(row['year']).isdigit() else None,
            'authors': parse_authors(row['authors_url'], row['authors']),
            'arxiv': arxiv,
            'arxiv_url': row['eprint_url'] if arxiv else None,
            'doi': doi,
            'doi_url': row['doi_url'] if doi else None,
            'inspire_url': row['inspirehep_url'],
            'journal': publication['journal'],
            'posted': publication['posted'],
            'published': publication['published'],
            'nupa': nupa_all,
            'nupa_primary': nupa_primary,
            'qis': qis_all,
            'qis_primary': qis_primary,
            'types': paper_types(row.get('Paper_Types')),
            'bibtex': row['bibtex'].strip(),
        })
    papers.sort(key=lambda p: (-(p['year'] or 0), p['title'].lower()))
    return papers


STUB_LENGTH = 200


def build_categories(names, descriptions, groups):
    """Category records for the site.

    `status` marks categories whose description is still a placeholder, so the
    site can show what is written and what is outstanding rather than
    presenting "TBW" as if it were prose.
    """
    records = []
    for position, name in enumerate(names):
        description = descriptions[position].strip()
        stub = len(description) < STUB_LENGTH
        records.append({
            'name': name,
            'group': groups[position],
            'description': '' if stub else description,
            'status': 'stub' if stub else 'written',
            'words': 0 if stub else len(description.split()),
        })
    return records


def publish_pdf():
    """Copy the compiled PDF beside the site and describe it.

    The PDF is built locally by `make`, not by the website workflow, so its
    own compile date is reported rather than today's: the listings update
    nightly and the document does not, and the site should not hide that.
    """
    if not os.path.exists(PDF_FILE):
        print('note: %s not found, the site will omit it' % PDF_FILE)
        return None

    os.makedirs(WEB_DIR, exist_ok=True)
    shutil.copyfile(PDF_FILE, os.path.join(WEB_DIR, PDF_FILE))

    info = {'file': PDF_FILE, 'bytes': os.path.getsize(PDF_FILE)}

    match = PDF_DATE_RE.search(open(PDF_FILE, 'rb').read())
    if match:
        stamp = match.group(1).decode('ascii')
        compiled = date(int(stamp[0:4]), int(stamp[4:6]), int(stamp[6:8]))
        info['compiled'] = compiled.strftime('%d %B %Y').lstrip('0')

    # Page count needs a PDF parser; poppler is usually there, and the site
    # simply leaves the number out when it is not.
    try:
        output = subprocess.run(['pdfinfo', PDF_FILE], capture_output=True,
                                text=True, timeout=30).stdout
        pages = re.search(r'Pages:\s+(\d+)', output)
        if pages:
            info['pages'] = int(pages.group(1))
    except (OSError, subprocess.SubprocessError):
        pass

    print('%s -> %s (%.1f MB)' % (PDF_FILE, WEB_DIR, info['bytes'] / 1e6))
    return info


def main():
    nupa, nupa_desc, nupa_group, qis, qis_desc, qis_group = get_categories(
        CATEGORIES_YAML)
    df = get_dataframe(YAML_FILE, nupa, qis)

    papers = build_papers(df)
    categories = {
        'nupa': build_categories(nupa, nupa_desc, nupa_group),
        'qis': build_categories(qis, qis_desc, qis_group),
    }

    os.makedirs(OUT_DIR, exist_ok=True)
    meta = {
        'generated': datetime.now(timezone.utc).strftime('%d %B %Y'),
        'count': len(papers),
        'pdf': publish_pdf(),
        'papers': papers,
    }
    with open(os.path.join(OUT_DIR, 'papers.json'), 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, separators=(',', ':'))
    with open(os.path.join(OUT_DIR, 'categories.json'), 'w',
              encoding='utf-8') as f:
        json.dump(categories, f, ensure_ascii=False, indent=1)

    print('%d papers -> %s' % (len(papers), OUT_DIR))
    missing = [p['key'] for p in papers if not p['authors']]
    if missing:
        print('warning: no authors found for %s' % ', '.join(missing))


if __name__ == '__main__':
    main()