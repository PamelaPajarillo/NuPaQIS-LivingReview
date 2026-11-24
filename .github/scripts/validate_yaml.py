"""Check NUPAQIS.yaml and NUPAQIS_CATEGORIES.yaml without contacting INSPIRE."""
import sys
from collections import Counter

import yaml

errors = []

# The categories file has two YAML documents: NuPa categories, then QIS categories.
docs = [d for d in yaml.safe_load_all(open('NUPAQIS_CATEGORIES.yaml')) if d]
if len(docs) != 2:
    sys.exit('NUPAQIS_CATEGORIES.yaml: expected 2 documents (NuPa, QIS), found %d' % len(docs))
valid = {'NUPA_Categories': {c['Category'] for c in docs[0]},
         'QIS_Categories': {c['Category'] for c in docs[1]}}

papers = yaml.safe_load(open('NUPAQIS.yaml'))
if not isinstance(papers, list) or not papers:
    sys.exit('NUPAQIS.yaml: expected a non-empty list of papers')

for dup, n in Counter(p.get('ID') for p in papers).items():
    if n > 1:
        errors.append('ID %s appears %d times' % (dup, n))

for p in papers:
    pid = p.get('ID')
    if not isinstance(pid, int):
        errors.append('entry %r: ID must be an INSPIRE record number' % (pid,))
    for field, allowed in valid.items():
        cats = [c.strip() for c in str(p.get(field) or '').split(';') if c.strip()]
        if not cats:
            errors.append('ID %s: no %s' % (pid, field))
        for c in cats:
            if c not in allowed:
                errors.append('ID %s: unknown %s entry "%s"' % (pid, field, c))

if errors:
    print('\n'.join(errors))
    sys.exit('%d problem(s) found' % len(errors))
print('OK: %d papers, %d NuPa and %d QIS categories'
      % (len(papers), len(valid['NUPA_Categories']), len(valid['QIS_Categories'])))