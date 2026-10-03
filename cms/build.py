"""Build the CMS Body for each eBus page:  python3 build.py

The US CMS ("Landing" content type) has a single Body field (text format: Master HTML),
so each page ships as one file:  <style> + markup + <script>.

  src/<page>/content.html   markup (asset URLs point straight at the CDN)
  src/<page>/style.css      page CSS, scoped to #vf-ebus-scope
  src/ebus.js               shared JS (carousel / fade slider / EB12-EB8 tabs)

  dist/<page>.html          -> paste into Body (style + markup + script in one file)
  <page>/body.html          -> markup + inline src/ebus.js, loads style.css next to it
  <page>/style.css          -> page CSS (loads Mulish with @import)
  preview/<page>.html       -> local preview (Bootstrap 4 + Mulish like the theme)
"""
import os

PAGES = ['home', 'about-us', 'our-buses', 'contact-us']

HERE = os.path.dirname(os.path.abspath(__file__))
BOOTSTRAP = 'https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.6.2/css/bootstrap.min.css'
MULISH = 'https://fonts.googleapis.com/css2?family=Mulish:wght@200..900&display=swap'
MULISH_PAGE = 'https://fonts.googleapis.com/css2?family=Mulish:wght@200;400;600;700&display=swap'


def read(*parts):
    with open(os.path.join(HERE, *parts), encoding='utf-8') as f:
        return f.read()


def write(text, *parts):
    path = os.path.join(HERE, *parts)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    return path


js = read('src', 'ebus.js').strip()
for page in PAGES:
    css = read('src', page, 'style.css').strip()
    markup = read('src', page, 'content.html').strip()
    body = f"<style>\n{css}\n</style>\n\n{markup}\n\n<script>\n{js}\n</script>\n"
    print(write(body, 'dist', page + '.html'))

    write('<link rel="stylesheet" href="style.css">\n'
          + markup.replace('Markup only — build.py wraps it with style.css + ebus.js',
                           'Markup + JS. CSS: style.css')
          + f'\n\n<script>\n{js}\n</script>\n', page, 'body.html')
    write(f"@import url('{MULISH_PAGE}');\n\n{css}\n", page, 'style.css')

    preview = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Preview — {page}</title>
<link rel="stylesheet" href="{BOOTSTRAP}">
<link rel="stylesheet" href="{MULISH}">
<style>body {{ font-family: Mulish, sans-serif; color: #3c3c3c; }}</style>
</head>
<body>
{body}
</body>
</html>
"""
    write(preview, 'preview', page + '.html')
