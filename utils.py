import sys
import re
import os
import html
import hashlib
import functools
import unicodedata
import warnings
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import date
import urllib3
import json
import yaml
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import seaborn as sns

# ---------------------------------------------------------------------------
# LaTeX sanitization - Claude 
# ---------------------------------------------------------------------------

# TeX specials that must be escaped in text mode.
_LATEX_SPECIALS = {
    '\\': r'\textbackslash{}',
    '&': r'\&',
    '%': r'\%',
    '$': r'\$',
    '#': r'\#',
    '_': r'\_',
    '{': r'\{',
    '}': r'\}',
    '~': r'\textasciitilde{}',
    '^': r'\textasciicircum{}',
}

# Unicode with no Latin Modern glyph, or that renders better as a TeX command.
_UNICODE_MAP = {
    '\u00a0': '~',        # no-break space
    '\u2002': r'\,', '\u2003': r'\ ', '\u2005': r'\,',
    '\u2008': r'\,', '\u2009': r'\,', '\u200a': r'\,',  # thin/hair spaces
    '\u200b': '', '\ufeff': '',                          # zero-width
    '\u2010': '-', '\u2011': '-', '\u2012': '--',
    '\u2013': '--', '\u2014': '---',
    '\u2018': '`', '\u2019': "'", '\u201c': '``', '\u201d': "''",
    '\u2026': r'\ldots{}',
    '\u2212': r'$-$', '\u00b1': r'$\pm$', '\u00d7': r'$\times$',
    '\u00b7': r'$\cdot$', '\u2248': r'$\approx$', '\u2260': r'$\neq$',
    '\u2264': r'$\leq$', '\u2265': r'$\geq$', '\u221e': r'$\infty$',
    '\u2192': r'$\to$', '\u2032': r"$'$", '\u00b0': r'$^\circ$',
    '\u00ae': r'\textregistered{}', '\u00a9': r'\copyright{}',
}

# Greek -> math mode. Latin Modern's roman faces have no Greek at all.
_GREEK = {
    'α': 'alpha', 'β': 'beta', 'γ': 'gamma', 'δ': 'delta', 'ε': 'epsilon',
    'ζ': 'zeta', 'η': 'eta', 'θ': 'theta', 'ι': 'iota', 'κ': 'kappa',
    'λ': 'lambda', 'μ': 'mu', 'ν': 'nu', 'ξ': 'xi', 'π': 'pi', 'ρ': 'rho',
    'σ': 'sigma', 'τ': 'tau', 'υ': 'upsilon', 'φ': 'phi', 'χ': 'chi',
    'ψ': 'psi', 'ω': 'omega',
    'Γ': 'Gamma', 'Δ': 'Delta', 'Θ': 'Theta', 'Λ': 'Lambda', 'Ξ': 'Xi',
    'Π': 'Pi', 'Σ': 'Sigma', 'Υ': 'Upsilon', 'Φ': 'Phi', 'Ψ': 'Psi',
    'Ω': 'Omega',
}
_UNICODE_MAP.update({k: r'$\%s$' % v for k, v in _GREEK.items()})

# Combining accents -> TeX accent commands, for the accents='tex' mode.
_COMBINING = {
    '\u0300': '`', '\u0301': "'", '\u0302': '^', '\u0303': '~',
    '\u0304': '=', '\u0306': 'u', '\u0307': '.', '\u0308': '"',
    '\u030a': 'r', '\u030b': 'H', '\u030c': 'v', '\u0327': 'c',
    '\u0328': 'k', '\u0331': 'b',
}
_STANDALONE = {
    'ł': r'\l{}', 'Ł': r'\L{}', 'ø': r'\o{}', 'Ø': r'\O{}',
    'æ': r'\ae{}', 'Æ': r'\AE{}', 'œ': r'\oe{}', 'Œ': r'\OE{}',
    'å': r'\aa{}', 'Å': r'\AA{}', 'ß': r'\ss{}', 'ı': r'\i{}',
    'đ': r'\dj{}', 'Đ': r'\DJ{}', 'ð': r'\dh{}', 'þ': r'\th{}',
}

# Codepoints Latin Modern covers, so they can be passed through to LuaLaTeX.
_SAFE_RANGES = ((0x00a1, 0x00ff), (0x0100, 0x017f), (0x0180, 0x024f))


# Greek inside a MathML fragment is already in math mode, so it needs the bare
# command without dollars. Without this, a raw beta reaches cmmi10 and vanishes.
_GREEK_MATH = {k: '\\%s ' % v for k, v in _GREEK.items()}


def _math_text(text):
    """Map non-ASCII inside a math fragment to math-mode commands."""
    return ''.join(_GREEK_MATH.get(c, c) for c in text)


def _mathml_node_to_tex(node):
    """Recursively convert one presentation-MathML node to a LaTeX fragment."""
    tag = node.tag.split('}')[-1]          # drop any XML namespace
    kids = [_mathml_node_to_tex(c) for c in node]
    text = _math_text((node.text or '').strip())

    if tag in ('math', 'mrow', 'mstyle', 'semantics'):
        return ''.join(kids) if kids else text
    if tag == 'mi':
        if node.get('mathvariant') == 'double-struck':
            return r'\mathbb{%s}' % text
        if text.startswith('\\'):
            return text            # already a math command, e.g. \beta
        return r'\mathrm{%s}' % text if len(text) > 1 else text
    if tag in ('mn', 'mo'):
        return {'=': '=', '+': '+', '-': '-'}.get(text, text)
    if tag == 'mtext':
        return r'\text{%s}' % text if text else r'\,'
    if tag == 'msub':
        return '%s_{%s}' % (kids[0], kids[1]) if len(kids) > 1 else ''.join(kids)
    if tag == 'msup':
        return '%s^{%s}' % (kids[0], kids[1]) if len(kids) > 1 else ''.join(kids)
    if tag == 'msubsup':
        return '%s_{%s}^{%s}' % tuple(kids[:3]) if len(kids) > 2 else ''.join(kids)
    if tag == 'msqrt':
        return r'\sqrt{%s}' % ''.join(kids)
    if tag == 'mfrac':
        return r'\frac{%s}{%s}' % (kids[0], kids[1]) if len(kids) > 1 else ''.join(kids)
    if tag == 'mfenced':
        return r'\left(%s\right)' % ''.join(kids)
    return ''.join(kids) if kids else text


def _convert_mathml(fragment):
    """Convert one <math>...</math> fragment to inline math, or strip it."""
    try:
        tex = _mathml_node_to_tex(ET.fromstring(fragment))
    except ET.ParseError:
        warnings.warn('Could not parse MathML, stripping tags: %s' % fragment[:60])
        return re.sub(r'<[^>]+>', '', fragment)
    tex = re.sub(r'\s+', ' ', tex).strip()
    return '$%s$' % tex if tex else ''


def _map_unicode(text, accents, context):
    out = []
    for ch in text:
        if ord(ch) < 128:
            out.append(ch)
        elif ch in _UNICODE_MAP:
            out.append(_UNICODE_MAP[ch])
        elif accents == 'tex':
            out.append(_to_tex_accent(ch, context))
        elif any(lo <= ord(ch) <= hi for lo, hi in _SAFE_RANGES):
            out.append(ch)                       # Latin Modern has this glyph
        else:
            warnings.warn(
                'No LaTeX mapping for U+%04X (%s) in %r -- it may be dropped '
                'silently from the PDF.'
                % (ord(ch), unicodedata.name(ch, 'unnamed'), context[:60]))
            out.append(ch)
    return ''.join(out)


def _to_tex_accent(ch, context):
    """Decompose an accented letter into a TeX accent command."""
    if ch in _STANDALONE:
        return _STANDALONE[ch]
    decomposed = unicodedata.normalize('NFD', ch)
    if len(decomposed) == 2 and decomposed[1] in _COMBINING:
        base, mark = decomposed
        if base in 'ij':
            base = r'\%s{}' % base           # dotless i/j under an accent
        return r'\%s{%s}' % (_COMBINING[mark], base)
    warnings.warn('No TeX accent for U+%04X (%s) in %r'
                  % (ord(ch), unicodedata.name(ch, 'unnamed'), context[:60]))
    return ch


@functools.lru_cache(maxsize=8192)
def sanitize_for_latex(text, accents='tex'):
    if text is None:
        return ''
    text = str(text)
    if text == 'nan':
        return text

    text = unicodedata.normalize('NFC', text)

    # Split off <math> blocks so their LaTeX output is not re-escaped.
    parts = re.split(r'(<math\b.*?</math\s*>)', text, flags=re.DOTALL | re.IGNORECASE)

    out = []
    for i, part in enumerate(parts):
        if i % 2:                                   # a MathML fragment
            out.append(_convert_mathml(part))
            continue
        part = re.sub(r'<[^>]+>', '', part)         # stray HTML tags
        part = html.unescape(part)                  # &amp; -> & before escaping
        part = ''.join(_LATEX_SPECIALS.get(c, c) for c in part)
        out.append(_map_unicode(part, accents, text))

    result = ''.join(out)
    result = result.replace('$$', '')      # merge adjacent math runs
    result = re.sub(r'(\\,){2,}', r'\\,', result)   # collapse repeated thin spaces
    return re.sub(r'[ \t]+', ' ', result).strip()


# ---------------------------------------------------------------------------
# Markdown sanitization - from Claude Opus 5 
# ---------------------------------------------------------------------------

_SUBSCRIPT = str.maketrans(
    '0123456789+-=()aehijklmnoprstuvx',
    '₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎ₐₑₕᵢⱼₖₗₘₙₒₚᵣₛₜᵤᵥₓ')
_SUPERSCRIPT = str.maketrans(
    '0123456789+-=()in', '⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁱⁿ')
_DOUBLE_STRUCK = {
    'C': 'ℂ', 'H': 'ℍ', 'N': 'ℕ', 'P': 'ℙ',
    'Q': 'ℚ', 'R': 'ℝ', 'Z': 'ℤ',
}
# Markdown-active characters, as numeric entities so they survive inside HTML.
_MD_ACTIVE = {'_': '&#95;', '*': '&#42;', '`': '&#96;',
              '[': '&#91;', ']': '&#93;'}


def _mathml_node_to_unicode(node):
    """Recursively convert one presentation-MathML node to plain Unicode."""
    tag = node.tag.split('}')[-1]
    kids = [_mathml_node_to_unicode(c) for c in node]
    text = (node.text or '').strip()

    if tag in ('math', 'mrow', 'mstyle', 'semantics'):
        return ''.join(kids) if kids else text
    if tag == 'mi':
        if node.get('mathvariant') == 'double-struck':
            return _DOUBLE_STRUCK.get(text, text)
        return text
    if tag == 'mn':
        return text
    if tag == 'mo':
        return ' = ' if text == '=' else text
    if tag == 'mtext':
        return text if text else ' '
    if tag in ('msub', 'msup') and len(kids) > 1:
        base, script = kids[0], kids[1]
        table = _SUBSCRIPT if tag == 'msub' else _SUPERSCRIPT
        # Use real sub/superscript glyphs only if every character has one.
        if script and all(ord(c) in table for c in script):
            return base + script.translate(table)
        return '%s%s%s' % (base, '_' if tag == 'msub' else '^', script)
    if tag == 'msqrt':
        inner = ''.join(kids)
        return '√%s' % inner if len(inner) == 1 else '√(%s)' % inner
    if tag == 'mfrac' and len(kids) > 1:
        return '%s/%s' % (kids[0], kids[1])
    if tag == 'mfenced':
        return '(%s)' % ''.join(kids)
    return ''.join(kids) if kids else text


def _convert_mathml_unicode(fragment):
    try:
        out = _mathml_node_to_unicode(ET.fromstring(fragment))
    except ET.ParseError:
        warnings.warn('Could not parse MathML, stripping tags: %s' % fragment[:60])
        return re.sub(r'<[^>]+>', '', fragment)
    return re.sub(r'\s+', ' ', out).strip()


@functools.lru_cache(maxsize=8192)
def sanitize_for_markdown(text, escape_emphasis=True):

    if text is None:
        return ''
    text = str(text)
    if text == 'nan':
        return text

    text = unicodedata.normalize('NFC', text)
    parts = re.split(r'(<math\b.*?</math\s*>)', text,
                     flags=re.DOTALL | re.IGNORECASE)

    out = []
    for i, part in enumerate(parts):
        if i % 2:
            math_text = _convert_mathml_unicode(part)
            if escape_emphasis:
                math_text = ''.join(_MD_ACTIVE.get(c, c) for c in math_text)
            out.append(math_text)
            continue
        part = re.sub(r'<[^>]+>', '', part)     # stray HTML tags
        part = html.unescape(part)              # normalize, then re-escape once
        part = (part.replace('&', '&amp;')
                    .replace('<', '&lt;')
                    .replace('>', '&gt;'))
        if escape_emphasis:
            part = ''.join(_MD_ACTIVE.get(c, c) for c in part)
        out.append(part)

    return re.sub(r'[ \t]+', ' ', ''.join(out)).strip()

# ---------------------------------------------------------------------------
# On-disk HTTP cache - Claude Opus 5 
# ---------------------------------------------------------------------------

_CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          '.inspire_cache')
_REFRESH = os.environ.get('INSPIRE_REFRESH', '') == '1'


def fetch_url(http, url):
    """GET a URL, returning the response body as text, cached on disk."""
    path = os.path.join(_CACHE_DIR,
                        hashlib.sha1(url.encode('utf-8')).hexdigest())
    if not _REFRESH and os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as handle:
            return handle.read()

    text = http.request('GET', url).data.decode('utf-8')
    os.makedirs(_CACHE_DIR, exist_ok=True)
    tmp = path + '.tmp'                       # atomic: never cache a partial read
    with open(tmp, 'w', encoding='utf-8') as handle:
        handle.write(text)
    os.replace(tmp, path)
    return text


def clear_inspire_cache():
    """Delete every cached InspireHEP response."""
    if os.path.isdir(_CACHE_DIR):
        for name in os.listdir(_CACHE_DIR):
            os.remove(os.path.join(_CACHE_DIR, name))


# ---------------------------------------------------------------------------
# Dataframe Creation and LaTeX/Markdown 
# ---------------------------------------------------------------------------
def format_pub_info(run, date_arxiv, date_doi, eprint, eprint_url, doi, doi_url):
    date_vec_arxiv = date_arxiv.split("-")
    date_vec_doi = date_doi.split("-")

    str_arxiv = ''
    str_doi = ''

    if date_arxiv != 'nan':
        # Prefix 
        if run == 'md':
            str_arxiv = "\n+ <strong>Posted on <a href=\"%s\">arXiv:%s</a>:</strong> " % (eprint_url, eprint)
        elif run == 'tex':
            str_arxiv = "\item \\textbf{Posted on arXiv:} "
        # Append Date
        if len(date_vec_arxiv) == 3:
            str_arxiv += date(int(date_vec_arxiv[0]), int(date_vec_arxiv[1]), int(date_vec_arxiv[2])).strftime("%d %B %Y")
        elif len(date_vec_arxiv) == 2:
            str_arxiv += date(int(date_vec_arxiv[0]), int(date_vec_arxiv[1]), 1).strftime("%B %Y")
        else:
            str_arxiv += date(int(date_vec_arxiv[0]), 1, 1).strftime("%Y")
    
    if date_doi != 'nan':
        # Prefix
        if run == 'md':
            str_doi = "\n+ <strong>Published in <a href=\"%s\">%s</a>:</strong> " % (doi_url, doi)
        elif run == 'tex':
            str_doi = "\item \\textbf{Published in %s:} " % (doi)
        # Append Date
        if len(date_vec_doi) == 3:
            str_doi += date(int(date_vec_doi[0]), int(date_vec_doi[1]), int(date_vec_doi[2])).strftime("%d %B %Y")
        elif len(date_vec_doi) == 2:
            str_doi += date(int(date_vec_doi[0]), int(date_vec_doi[1]), 1).strftime("%B %Y")
        else:
            str_doi += date(int(date_vec_doi[0]), 1, 1).strftime("%Y")
            
    if str_arxiv != '' and str_doi != '':
        return str_arxiv + ' ' +  str_doi
    elif str_arxiv != '' and str_doi == '':
        return str_arxiv
    elif str_arxiv == '' and str_doi != '':
        return str_doi
    else:
        return ''

def get_year(date_arxiv, date_doi):
    date_vec_arxiv = date_arxiv.split("-")
    date_vec_doi = date_doi.split("-")

    str_arxiv = ''
    str_doi = ''

    if date_arxiv != 'nan':
       # Append Date
        if len(date_vec_arxiv) == 3:
            str_arxiv += date(int(date_vec_arxiv[0]), int(date_vec_arxiv[1]), int(date_vec_arxiv[2])).strftime("%Y")
        elif len(date_vec_arxiv) == 2:
            str_arxiv += date(int(date_vec_arxiv[0]), int(date_vec_arxiv[1]), 1).strftime("%Y")
        else:
            str_arxiv += date(int(date_vec_arxiv[0]), 1, 1).strftime("%Y")

    if date_doi != 'nan':
        # Append Date
        if len(date_vec_doi) == 3:
            str_doi += date(int(date_vec_doi[0]), int(date_vec_doi[1]), int(date_vec_doi[2])).strftime("%Y")
        elif len(date_vec_doi) == 2:
            str_doi += date(int(date_vec_doi[0]), int(date_vec_doi[1]), 1).strftime("%Y")
        else:
            str_doi += date(int(date_vec_doi[0]), 1, 1).strftime("%Y")
            
    if str_arxiv != '':
        return str_arxiv
    elif str_doi != '':
        return str_doi
    else:
        return ''
    
def get_dataframe(yaml_file, categories_hep, categories_qis):
    
    # Load the YAML file
    with open(yaml_file, 'r') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)

    # Convert the YAML data to a Pandas DataFrame
    df = pd.DataFrame.from_dict(data)

    # Check if there are multiple entries with the same ID
    if df['ID'].duplicated().any():
        duplicated_ids = df[df['ID'].duplicated()]['ID'].tolist()
        print("Error: The following IDs are duplicated in the YAML file:")
        for dup_id in duplicated_ids:
            print(f"- {dup_id}")
        sys.exit(1)
    
    # Check to make sure each paper's categories are valid
    def check_categories(categories, category_list):
        for category in categories.split(', '):
            if category not in category_list:
                return False
        return True
    
    
    # Check to make sure each paper has at least one valid NUPA category and at least one valid QIS category
    exit_condition = False
    df["NUPA_Check"] = df["NUPA_Categories"].str.contains('|'.join(categories_hep), case=False)
    df["QIS_Check"] = df["QIS_Categories"].str.contains('|'.join(categories_qis), case=False)
    df["NUPA_Category_Check"] = df["NUPA_Categories"].apply(lambda x: check_categories(x, categories_hep))
    df["QIS_Category_Check"] = df["QIS_Categories"].apply(lambda x: check_categories(x, categories_qis))
    check_hep = df[~df["NUPA_Check"] | ~df["NUPA_Category_Check"]]
    check_qis = df[~df["QIS_Check"]| ~df["QIS_Category_Check"]]
    if len(check_hep) > 0:
        print("The following papers have invalid NUPA categories:")
        print(check_hep[['ID']])
        exit_condition = True
    if len(check_qis) > 0:
        print("The following papers have invalid QIS categories:")
        print(check_qis[['ID']])
        exit_condition = True

    # Stop if there are any invalid categories
    if exit_condition:
        sys.exit(1)
    
    # Parse out primary category and secondary categories
    def sort_categories(categories, primary = False):
        if primary:
            return categories.split(', ', 1)[0]
        else:
            return categories.split(', ', 1)[1] if len(categories.split(', ')) > 1 else 'N/A'
    
    df["NUPA_Primary"] = df["NUPA_Categories"].apply(lambda x: sort_categories(x, primary = True))
    df["NUPA_Secondary"] = df["NUPA_Categories"].apply(lambda x: sort_categories(x, primary = False))
    df["QIS_Primary"] = df["QIS_Categories"].apply(lambda x: sort_categories(x, primary = True))
    df["QIS_Secondary"] = df["QIS_Categories"].apply(lambda x: sort_categories(x, primary = False))

    def get_inspirehep_metadata(label, http):
        url = 'https://inspirehep.net/api/literature/' + str(label)
        metadata = json.loads(fetch_url(http, url))
        return metadata

    def get_doi_metadata(label, http):
        if label != 'nan':
            url = 'https://inspirehep.net/api/doi/' + str(label)
            metadata = json.loads(fetch_url(http, url))
            return metadata['metadata']
        else:
            return json.loads('{}')

    def get_author_list(metadata):
        author_list = ''
        if 'authors' in metadata['metadata'].keys():
            for i in metadata['metadata']['authors']:
                author_list += i['full_name'] + " and "
            author_list = author_list[:-5]
        else:
            author_list =  'nan'
        
        # Fix Formatting
        author_list = author_list.split(' and ')
        formatted_author_list = []
        for author in author_list:
            if ',' in author:
                formatted_author_list.append(author.split(',')[1].strip() + ' ' + author.split(',')[0].strip())
        fixed_author = ', '.join(formatted_author_list)
        return fixed_author

    def get_author_url_list(metadata):
        author_list = ''
        for i in metadata['metadata']['authors']:
            author_name = i['full_name']
            if ',' in author_name:
                author_name = author_name.split(',')[1].strip() + ' ' + author_name.split(',')[0].strip()
            author_list += "<a href=\"%s\"> %s</a>" % (i['record']['$ref'].replace('/api',''), author_name) + ", "
        return author_list[:-2]
    
    def get_journal_doi(doi, metadata_doi):
        if doi != 'nan':
            if 'publication_info' in metadata_doi.keys():
                if len(metadata_doi['publication_info']) != 1:
                    full_journal_name = ''
                    for i in metadata_doi['publication_info']:
                        if 'pubinfo_freetext' in i.keys():
                            full_journal_name = i['pubinfo_freetext']
                        elif 'journal_title' in i.keys():
                            full_journal_name = i['journal_title']
                        else:
                            return 'nan'
                    return full_journal_name
                elif 'pubinfo_freetext' in metadata_doi['publication_info'][0].keys():
                    return metadata_doi['publication_info'][0]['pubinfo_freetext']
                elif 'journal_title' in metadata_doi['publication_info'][0].keys():
                    return metadata_doi['publication_info'][0]['journal_title']
                elif 'journal_title' in metadata_doi['publication_info'][0].keys():
                    return metadata_doi['publication_info'][0]['journal_title']
                else:
                     return 'nan'            
            else:
                return 'nan'
        else:
            return 'nan'
    
    def get_bibtex(metadata, http):
        url = metadata["links"]["bibtex"]
        return fetch_url(http, url)
            
    # Read InspireHEP entry
    http = urllib3.PoolManager()
    df['ID'] = df['ID'].astype(str)
    df["metadata"] = df.apply(lambda x: get_inspirehep_metadata(x["ID"], http), axis=1)
    df["inspirehep_url"] = "https://inspirehep.net/literature/" + df["ID"]
    df["title"] = df["metadata"].apply(lambda x: x['metadata']['titles'][0]['title'])
    df["authors"] = df["metadata"].apply(lambda x: get_author_list(x))
    df["authors_url"] = df["metadata"].apply(lambda x: get_author_url_list(x))
    df["eprint"] = df["metadata"].apply(lambda x: x['metadata']['arxiv_eprints'][0]['value'] if 'arxiv_eprints' in x['metadata'].keys() else 'nan')
    df["doi"] = df["metadata"].apply(lambda x: x['metadata']['dois'][0]['value'] if 'dois' in x['metadata'].keys() else 'nan')
    df["eprint_url"] = df["eprint"].apply(lambda x: "https://arxiv.org/abs/" + x if x != 'nan' else 'nan')
    df["doi_url"] = df["doi"].apply(lambda x: "https://doi.org/" + x if x != 'nan' else 'nan')
    df["arxiv_date"] = df["metadata"].apply(lambda x: x['metadata']['preprint_date'] if 'preprint_date' in x['metadata'].keys() else 'nan')
    df["doi_date"] = df["metadata"].apply(lambda x: x['metadata']['imprints'][0]['date'] if 'imprints' in x['metadata'].keys() else (x['metadata']['publication_info'][0]['year'] if 'publication_info' in x['metadata'].keys() and 'journal_title' in x['metadata']['publication_info'][0] else 'nan'))
    df["metadata_doi"] = df.apply(lambda x: get_doi_metadata(x['doi'], http), axis=1)
    df["journal_name"] = df.apply(lambda x: get_journal_doi(x['doi'], x['metadata_doi']), axis=1)
    df["Publish_Info_md"] = df.apply(lambda x: format_pub_info('md', str(x['arxiv_date']), str(x['doi_date']), str(x['eprint']), str(x['eprint_url']), str(x['journal_name']), str(x['doi_url'])), axis=1)
    df["Publish_Info_latex"] = df.apply(lambda x: format_pub_info('tex', str(x['arxiv_date']), str(x['doi_date']), str(x['eprint']), str(x['eprint_url']), str(x['journal_name']), str(x['doi_url'])), axis=1)
    df["bibtex_tag"] = df["metadata"].apply(lambda x: x['metadata']['texkeys'][0])
    df["bibtex"] = df["metadata"].apply(lambda x: get_bibtex(x, http))
    df["year"] = df.apply(lambda x: get_year(str(x['arxiv_date']), str(x['doi_date'])), axis=1)
    # Compress dataframe with useful information
    df = df[["ID", "title", "authors", "authors_url", "eprint", "doi", "eprint_url", "doi_url", "inspirehep_url", "Publish_Info_md", "Publish_Info_latex",
             "NUPA_Primary", "NUPA_Secondary", "QIS_Primary", "QIS_Secondary", "bibtex_tag", "bibtex", "year"]]
    
    # Check for identical bibtex entries
    if df['bibtex'].duplicated().any():
        duplicated_bibtex = df[df['bibtex'].duplicated()]['ID'].tolist()
        print("Warning: The following IDs have identical BibTeX entries in the YAML file:")
        for dup_id in duplicated_bibtex:
            print(f"- {dup_id}")
        sys.exit(1)

    return df

def get_categories(yaml_file):
    # Read YAML file
    df_categories = {}
    list_categories = {}
    heatmap_categories = {}
    categories_description = {}
    with open(yaml_file, 'r') as file:
        data = yaml.load_all(file, Loader=yaml.FullLoader)

        # Convert the YAML data to a Pandas DataFrame
        for idx, d in enumerate(data):
            df_categories[idx] = pd.DataFrame.from_dict(d)
            list_categories[idx] = df_categories[idx]['Category'].tolist()
            heatmap_categories[idx] = df_categories[idx]['Heatmap'].tolist()
            categories_description[idx] = df_categories[idx]['Description'].tolist()
    
    return list_categories[0], categories_description[0], heatmap_categories[0], list_categories[1], categories_description[1], heatmap_categories[1] 

def plot_histogram(df, run):
    counts = df['%s_Primary' % run].value_counts()
    title = "Nuclear and Particle Physics" if run == 'NUPA' else "Quantum Information Science"
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(18, 8))
    bar_color = "skyblue" if run == 'NUPA' else "lightgreen"
    # Plot
    bars = plt.bar(counts.index, counts.values, color=bar_color)
    plt.xlabel("%s Categories" % title, fontsize=13)
    plt.ylabel("Number of Papers", fontsize=13)
    plt.title("Number of Papers in the %s Category" % title, fontsize=15, pad=20)
    plt.xticks(rotation=75, ha='right', fontsize=10)

    # Add value labels above each bar
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2,
                 height + 0.3,
                 str(int(height)),
                 ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.savefig("%s_Histogram.png" % run, dpi=300)

def plot_2D_nupaqis_heatmap(df, categories_nupa, categories_qis, heatmap_nupa, heatmap_qis):

    nupa_heatmap = ['Reviews and Whitepapers', 'Dark Matter', 'Quantum Information in Collider Physics', 'Lattice Field Theories', 'Particle Physics', 'Nuclear Physics']
    qis_heatmap = ['Reviews and Whitepapers', 'Quantum Sensors', 'Quantum Entanglement and Bell Inequalities', 'Quantum Simulations', 'Quantum Algorithms', 'Quantum Machine Learning']
    # Build the matrix
    heatmap_data = np.zeros((len(nupa_heatmap), len(qis_heatmap)))

    for i, nupa_cat in enumerate(categories_nupa):
        for j, qis_cat in enumerate(categories_qis):
            for k, nupa in enumerate(nupa_heatmap):
                for l, qis in enumerate(qis_heatmap):
                    if heatmap_nupa[i] == nupa and heatmap_qis[j] == qis:
                        count = len(df[(df['NUPA_Primary'] == nupa_cat) & 
                                       (df['QIS_Primary'] == qis_cat)])
                        heatmap_data[k, l] += count

    cmap = plt.cm.Blues
    cmap = cmap.copy()
    cmap.set_under(color='white')
    max_count = np.max(heatmap_data)
    norm = colors.Normalize(vmin=0.001, vmax=max_count)

    plt.figure(figsize=(16, 14))
    plt.imshow(heatmap_data, cmap=cmap, norm=norm, aspect='auto')

    cbar = plt.colorbar(label='Number of Papers')
    cbar.ax.tick_params(labelsize=15)

    xlabels = ["Reviews and Whitepapers", "Quantum Sensors", "Quantum Entanglement and \nBell Inequalities", "Quantum Simulations", "Quantum Algorithms", "Quantum Machine Learning"]
    # Axis labels
    plt.xticks(
        ticks=np.arange(len(qis_heatmap)),
        labels=xlabels,
        rotation=45,
        ha='right',
        rotation_mode='anchor',
        fontsize=15,
    )
    plt.yticks(
        ticks=np.arange(len(nupa_heatmap)),
        labels=nupa_heatmap,
        fontsize=15
    )
    plt.xlabel('Quantum Information Science (QIS) Topics', fontsize=20)
    plt.ylabel('Nuclear and Particle Physics (NuPa) Topics', fontsize=20)
    plt.title('NuPa vs QIS Topics in NUPAQIS Living Review', fontsize=30, pad=20)

    # Add numbers inside each cell
    for i in range(len(nupa_heatmap)):
        for j in range(len(qis_heatmap)):
            val = heatmap_data[i, j]

            # Choose text color based on background intensity
            if val > max_count * 0.5:
                text_color = "white"
            else:
                text_color = "black"

            plt.text(j, i, int(val),
                     ha='center', va='center',
                     fontsize=9, color=text_color)

    # Grid lines
    plt.gca().set_xticks(np.arange(-0.5, len(qis_heatmap), 1), minor=True)
    plt.gca().set_yticks(np.arange(-0.5, len(nupa_heatmap), 1), minor=True)
    plt.grid(which='minor', color='gray', linestyle='-', linewidth=0.2, alpha=0.4)

    plt.tight_layout()
    plt.savefig('NUPAQIS_2D_Heatmap.png', dpi=300)
    plt.close()

def histogram_by_year(df):
    years = pd.to_numeric(df['year'], errors='coerce').dropna().astype(int)
    counts = years.value_counts().sort_index()
    full_range = range(int(counts.index.min()), int(counts.index.max()) + 1)
    counts = counts.reindex(full_range, fill_value=0)

    with sns.axes_style("whitegrid"):
        fig, ax = plt.subplots(figsize=(18, 8))

        bars = ax.bar(counts.index, counts.values)
        ax.set_xlabel("Year", fontsize=20)
        ax.set_ylabel("Number of Papers", fontsize=20)
        ax.set_title("Number of Papers in NuPaQIS by Year", fontsize=25, pad=20)
        ax.set_xticks(list(counts.index))
        ax.set_xticklabels(counts.index, rotation=45, ha='right', fontsize=15)
        ax.margins(x=0.01)

        # Value labels above each bar
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width() / 2,
                        height + 0.3,
                        str(int(height)),
                        ha='center', va='bottom', fontsize=10)

        fig.tight_layout()
        fig.savefig("NUPAQIS_Year.png", dpi=300)
        plt.close(fig)

def list_subcategories_to_md(OUTPUT_FILE_MAIN, subcategories, description, run_type):
    textcolor = 'textbfcolor9bc53d' if run_type == 'NUPA' else 'textbfcolor5bc0eb'
    for category in subcategories:
        if (category != 'Reviews') and (category != 'Whitepapers and Proceedings'):
            OUTPUT_FILE_MAIN.write("<details>\n")
            OUTPUT_FILE_MAIN.write("<summary> <b>%s: </b> <a href=\"/BY_%s/README.md#%s%s\"> Link to Papers </a>  <code>Expand for Description</code> </summary>\n\n" % (category, run_type, textcolor, category.replace(" ", "-").lower()))
            OUTPUT_FILE_MAIN.write("\n\n%s\n" % (description[subcategories.index(category)]))
            OUTPUT_FILE_MAIN.write("</details>\n\n")
        elif (category == 'Reviews'):
            OUTPUT_FILE_MAIN.write("<details>\n")
            OUTPUT_FILE_MAIN.write("<summary> <b>Reviews, Whitepapers, and Proceedings: </b> <a href=\"/BY_%s/README.md#textbfreviews-and-whitepapers\"> Link to Papers </a>  <code>Expand for Description</code> </summary>\n\n" % (run_type))
            OUTPUT_FILE_MAIN.write("\n\nThe references below contain (static) reviews and whitepapers listed in applications of quantum information science to particle physics. Note that the majority of the references are from the Snowmass Community Planning Exercises.\n" )
            OUTPUT_FILE_MAIN.write("</details>\n\n")
        else:
            continue
    OUTPUT_FILE_MAIN.write("\n\n")
    
def write_papers_to_md(df, output_file, categories_main, categories_sub, main_type, sub_type):

    # Get Main Categories
    for main_category in categories_main:

        # Print Title of Main Category
        if (main_category != 'Reviews') and (main_category != 'Whitepapers and Proceedings'):
            if main_type != "NUPA":
                output_file.write("##  $\\textbf{{\color{#5BC0EB}%s}}$ \n\n" % (main_category))
            else:
                output_file.write("##  $\\textbf{{\color{#9BC53D}%s}}$ \n\n" % (main_category))
        elif (main_category == 'Reviews'):
            output_file.write("##  $\\textbf{Reviews and Whitepapers and Proceedings}$ \n\n")

        # Retrieve papers by checking for substring in categories
        df_main = df.loc[df['%s_Primary' % main_type].str.contains(main_category, case=False)]
        
        for sub_category in categories_sub:
            
            # Retrieve papers by checking for substring in categories
            df_sub = df_main.loc[df['%s_Primary' % sub_type].str.contains(sub_category, case=False)]
            papers = df_sub.values.tolist()

            if len(papers) > 0:
                # Print Title of Category
                if (main_category != 'Reviews') and (main_category != 'Whitepapers and Proceedings'):
                    if sub_type != "NUPA":
                        output_file.write("###  $\\textbf{{\color{#5BC0EB}%s}}$ \n\n" % (sub_category))
                    else:
                        output_file.write("###  $\\textbf{{\color{#9BC53D}%s}}$ \n\n" % (sub_category))

                else:
                    output_file.write("###  $\\textbf{%s}$ \n\n" % (sub_category))

                # Formatting and write to file
                for paper in papers:

                    output_file.write("<details>\n")

                    if (str(paper[4]) != 'nan') and (str(paper[5]) != 'nan'):
                        output_file.write("<summary> (%s) <b>%s</b> [<a href=\"%s\">arXiv</a>] [<a href=\"%s\">DOI</a>] [<a href=\"%s\">INSPIRE</a>] <code>Expand</code> </summary>" % (paper[17], paper[1], paper[6], paper[7], paper[8]))
                    elif str(paper[4]) != 'nan':
                        output_file.write("<summary> (%s) <b>%s</b> [<a href=\"%s\">arXiv</a>] [<a href=\"%s\">INSPIRE</a>] <code>Expand</code><br> </summary>" % (paper[17], paper[1], paper[6], paper[8]))
                    elif str(paper[5])!= 'nan':
                        output_file.write("<summary> (%s) <b>%s</b> [<a href=\"%s\">DOI</a>] [<a href=\"%s\">INSPIRE</a>] <code>Expand</code><br> </summary>" % (paper[17], paper[1], paper[7], paper[8]))
                    else:
                        output_file.write("<summary> (%s) <b>%s</b> [<a href=\"%s\">INSPIRE</a>] <code>Expand</code><br> </summary>" % (paper[17], paper[1], paper[8]))

                    # Write brief description and summary of paper
                    output_file.write("\n\n+ <strong>Authors:</strong> %s%s" % (paper[3], paper[9]))
                    output_file.write("</details>\n\n")
                
        # Crosslists Papers (Add papers from secondary categories)
        df_crosslisted = df.loc[df['%s_Secondary' % main_type].str.contains(main_category, case=False)]
        crosslisted_papers = df_crosslisted.values.tolist()
        if len(crosslisted_papers) > 0:
            if sub_type != "NUPA":
                output_file.write("###  $\\textbf{{\color{#5BC0EB}Crosslists}}$ \n\n")
            else:
                output_file.write("###  $\\textbf{{\color{#9BC53D}Crosslists}}$ \n\n")
            for paper in crosslisted_papers:
                output_file.write("<details>\n")

                if (str(paper[4]) != 'nan') and (str(paper[5]) != 'nan'):
                    output_file.write("<summary> (%s) <b>%s</b> [<a href=\"%s\">arXiv</a>] [<a href=\"%s\">DOI</a>] [<a href=\"%s\">INSPIRE</a>] <code>Expand</code> </summary>" % (paper[17], paper[1], paper[6], paper[7], paper[8]))
                elif str(paper[4]) != 'nan':
                    output_file.write("<summary> (%s) <b>%s</b> [<a href=\"%s\">arXiv</a>] [<a href=\"%s\">INSPIRE</a>] <code>Expand</code><br> </summary>" % (paper[17], paper[1], paper[6], paper[8]))
                elif str(paper[5])!= 'nan':
                    output_file.write("<summary> (%s) <b>%s</b> [<a href=\"%s\">DOI</a>] [<a href=\"%s\">INSPIRE</a>] <code>Expand</code><br> </summary>" % (paper[17], paper[1], paper[7], paper[8]))
                else:
                    output_file.write("<summary> (%s) <b>%s</b> [<a href=\"%s\">INSPIRE</a>] <code>Expand</code><br> </summary>" % (paper[17], paper[1],paper[8]))

                # Write brief description and summary of paper
                output_file.write("\n\n+ <strong>Authors:</strong> %s%s" % (paper[3], paper[9]))
                output_file.write("</details>\n\n")

                output_file.write("\n\n")

def write_papers_to_tex(df, file, categories_main, categories_sub, main_type, sub_type):
    # Get Categories and Subcategories
    if main_type == 'NUPA':
        file.write("\section{Nuclear and Particle Physics in Quantum Information Science}\n\n")
    elif main_type == 'QIS':
        file.write("\section{Quantum Information Science in Nuclear and Particle Physics}\n\n")
    
    for main_category in categories_main:
        # Print Title of Main Category
        if (main_category != 'Reviews') and (main_category != 'Whitepapers and Proceedings'):
            file.write("\subsection{%s}\n\n" % main_category)
        elif (main_category == 'Reviews'):
            file.write("\subsection{Reviews and Whitepapers and Proceedings}\n\n")

        # Retrieve papers by checking for substring in categories
        df_main = df.loc[df['%s_Primary' % main_type].str.contains(main_category, case=False)]
        
        for sub_category in categories_sub:
            
            # Retrieve papers by checking for substring in categories
            df_sub = df_main.loc[df['%s_Primary' % sub_type].str.contains(sub_category, case=False)]
            papers = df_sub.values.tolist()

            if len(papers) > 0:
                
                file.write("\subsubsection{%s}\n\n" % sub_category)

                # Formatting and write to file
                for paper in papers:

                    file.write("\paragraph{%s~\cite{%s}}\n" % (sanitize_for_latex(paper[1]), paper[15]))
                    file.write("\\begin{itemize}\n")
                    file.write("\t\item \\textbf{Authors:} %s\n\t%s\n" % (sanitize_for_latex(paper[2]), paper[10]))                    
                    file.write("\end{itemize}\n\n")
                file.write("\n\n")
        
        # Crosslists Papers (Add papers from secondary categories)
        df_crosslisted = df.loc[df['%s_Secondary' % main_type].str.contains(main_category, case=False)]
        crosslisted_papers = df_crosslisted.values.tolist()
        if len(crosslisted_papers) > 0:
            file.write("\subsubsection{Crosslists}\n\n")
            # Formatting and write to file
            for paper in crosslisted_papers:

                file.write("\paragraph{%s~\cite{%s}}\n" % (sanitize_for_latex(paper[1]), paper[15]))
                file.write("\\begin{itemize}\n")
                file.write("\t\item \\textbf{Authors:} %s\n\t%s\n" % (sanitize_for_latex(paper[2]), paper[10]))                    
                file.write("\end{itemize}\n\n")
            file.write("\n\n")

def write_bib(df, OUTPUT_FILE_BIB):
    for paper in df.values.tolist():
        OUTPUT_FILE_BIB.write("%s\n" % paper[16])