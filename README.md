# SALT Systems Lab website

A static site for https://github.com/saltsystemslab. It uses plain HTML and CSS with no build step.

- `index.html`: lab home page and the four research areas
- `projects.html`: all projects, grouped by area (`#filters`, `#hashtables`, `#gpu`, `#ai`)
- `projects/<name>.html`: one detail page per project
- `assets/style.css`: shared styles, with light and dark mode
- `assets/logo-mark.svg`: the logo mark, also used as the favicon. `assets/logo.svg` and `assets/logo-dark.svg` are the full logo for light and dark backgrounds.

## Preview locally

    python3 -m http.server 8000   # then open http://localhost:8000

## Deploy (GitHub Pages)

1. Create the repo `saltsystemslab/saltsystemslab.github.io`.
2. Push these files to `main`.
3. The site is served at https://saltsystemslab.github.io.

## Adding or editing a project

The project pages, `projects.html`, and the area tiles on the home page are all generated from the data in `tools/generate.py`:

1. Edit or add an entry in `P`. Then add its slug to `ORDER` under the right area, and add a one-line card summary to `SUMMARY`.
2. Run `python3 tools/generate.py .` from the repo root.

When a project's repo gets its own GitHub Pages site, add it to `SITES` in `tools/generate.py` and regenerate. Its card and the "More in …" links then point to that site, and `projects/<slug>.html` becomes a redirect to it.

The People section in `index.html` is edited by hand.

The output is plain static HTML, so GitHub Pages needs no build step.
