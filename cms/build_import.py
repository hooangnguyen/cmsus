"""Build Single Content Sync import zips for the eBus pages:  python3 build_import.py [prod|dev] [--publish]

Import each zip at /admin/content/import (module single_content_sync),
or on the server:  drush content:import /path/to/file.zip

Every zip contains:
  <page>.yml                             one "Landing" node per page (Body = style + markup + script, Master HTML)
  assets/gs/statics/fields/images/...    part of the images -> gs://statics/fields/images/ebus-*.webp on import

All 4 page .yml are repeated in every zip because the importer refuses a zip without a .yml.
Node UUIDs are fixed, so re-importing updates the same nodes (new revision) instead of duplicating.
Images are split so each zip stays under MAX_ZIP bytes (upload limit on the CMS).

stg-cms-v2.vinfastauto.us is the "dev" environment (static-cms-dev CDN).
"""
import os
import re
import sys
import time
import uuid
import zipfile

import yaml

ENV = 'dev' if 'dev' in sys.argv[1:] else 'prod'
PUBLISH = '--publish' in sys.argv[1:]

# Images go into a folder that already exists on the bucket: gcsfs fails to create new
# folders on the server ("destination directory ... is not properly configured").
# The "ebus-" prefix keeps them from overwriting files already in that folder.
GS_PATH = 'statics/fields/images'
PREFIX = 'ebus-'
CDN = f'https://static-cms-{ENV}.vinfastauto.us/{GS_PATH}'
GS_DIR = f'assets/gs/{GS_PATH}'
MAX_ZIP = 1_800_000

# page -> (title, url alias)
PAGES = {
    'home': ('VinFast eBus', '/ebus'),
    'about-us': ('VinFast eBus - About Us', '/ebus/about-us'),
    'our-buses': ('VinFast eBus - Our Buses', '/ebus/our-buses'),
    'contact-us': ('VinFast eBus - Contact Us', '/ebus/contact-us'),
}

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'import')
UUID_NS = uuid.uuid5(uuid.NAMESPACE_URL, 'https://vinfastauto.us/ebus')


def read(*parts):
    with open(os.path.join(HERE, *parts), encoding='utf-8') as f:
        return f.read()


class LiteralStr(str):
    pass


yaml.add_representer(LiteralStr, lambda d, s: d.represent_scalar('tag:yaml.org,2002:str', s, style='|'))


def page_body(page):
    # Same assembly as build.py.
    return (f"<style>\n{read('src', page, 'style.css').strip()}\n</style>\n\n"
            f"{read('src', page, 'content.html').strip()}\n\n"
            f"<script>\n{read('src', 'ebus.js').strip()}\n</script>\n").replace('{{CDN}}/', f'{CDN}/{PREFIX}')


def node_yml(page, body):
    title, alias = PAGES[page]
    node = {
        'uuid': str(uuid.uuid5(UUID_NS, page)),
        'entity_type': 'node',
        'bundle': 'landing',
        'base_fields': {
            'title': title,
            'status': PUBLISH,
            'langcode': 'en',
            'created': int(time.time()),
            'author': None,
            'revision_log_message': 'eBus static cut import',
            'url': alias,
        },
        'custom_fields': {
            'body': [{'value': LiteralStr(body), 'summary': '', 'format': 'master_html'}],
        },
    }
    return yaml.dump(node, allow_unicode=True, sort_keys=False, width=1000)


ymls = {}
images = set()
for page in PAGES:
    body = page_body(page)
    images.update(re.findall(re.escape(f'{CDN}/{PREFIX}') + r'([A-Za-z0-9@._-]+)', body))
    ymls[page] = node_yml(page, body)

missing = [f for f in images if not os.path.isfile(os.path.join(HERE, 'cdn', 'ebus', f))]
if missing:
    sys.exit(f'Missing in cdn/ebus/: {missing}')

# Pack images (largest first) into zips under MAX_ZIP, leaving room for the compressed .yml files.
yml_budget = sum(len(y.encode()) for y in ymls.values()) // 3
bins = []
for f in sorted(images, key=lambda f: -os.path.getsize(os.path.join(HERE, 'cdn', 'ebus', f))):
    size = os.path.getsize(os.path.join(HERE, 'cdn', 'ebus', f))
    for b in bins:
        if b['size'] + size + yml_budget <= MAX_ZIP:
            b['files'].append(f)
            b['size'] += size
            break
    else:
        bins.append({'files': [f], 'size': size})

os.makedirs(OUT, exist_ok=True)
for old in os.listdir(OUT):
    if old.endswith('.zip'):
        os.remove(os.path.join(OUT, old))

for i, b in enumerate(bins, 1):
    path = os.path.join(OUT, f'ebus-import-{ENV}-part{i}.zip')
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        for page, y in ymls.items():
            z.writestr(f'ebus-{page}.yml', y)
        for f in sorted(b['files']):
            z.write(os.path.join(HERE, 'cdn', 'ebus', f), f'{GS_DIR}/{PREFIX}{f}')
    print(f'{path}  {os.path.getsize(path):,} bytes  {len(b["files"])} images')

# Pages only (no images): use when the images are uploaded to GCS another way.
path = os.path.join(OUT, f'ebus-import-{ENV}-pages-only.zip')
with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
    for page, y in ymls.items():
        z.writestr(f'ebus-{page}.yml', y)
print(f'{path}  {os.path.getsize(path):,} bytes  0 images')

# Small test: contact page + 1 image, to check that writing to gs:// works on the server.
path = os.path.join(OUT, f'ebus-import-{ENV}-test.zip')
with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
    z.writestr('ebus-contact-us.yml', ymls['contact-us'])
    z.write(os.path.join(HERE, 'cdn', 'ebus', 'contact-map.webp'), f'{GS_DIR}/{PREFIX}contact-map.webp')
print(f'{path}  {os.path.getsize(path):,} bytes  1 image')

print(f'\nCDN: {CDN}  |  status: {"published" if PUBLISH else "unpublished"}')
