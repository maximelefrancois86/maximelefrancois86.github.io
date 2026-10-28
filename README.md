# maxime-lefrancois.info

Personal academic website of Maxime Lefrançois, served by GitHub Pages at
<https://maxime-lefrancois.info/>.

## Layout

| Path | Content |
|---|---|
| `public/` | **Everything that is published**, and nothing else |
| `public/index.html`, `research/`, `teaching/` | The pages, plain HTML |
| `public/assets/site.css`, `assets/fonts/` | One stylesheet; self-hosted fonts (IBM Plex, Source Serif 4, SIL OFL) |
| `public/me.ttl` | FOAF profile in Turtle; the home page shows an excerpt of it |
| `public/docs/`, `common/`, `research/seas/`, `research/positions/`, `teaching/*` | Older files, kept at their URLs |
| `scripts/update_publications.py` | Regenerates the full publication list from HAL |
| `.github/workflows/pages.yml` | Deploys `public/` on every push to `master` |
| `notes/` | Working notes, not tracked by git |

## Editing

The pages are plain HTML without a build step. Header, navigation and footer are
repeated in each page: change them everywhere.

To update the publication list (the block between `<!-- hal:start -->` and
`<!-- hal:end -->` in `public/research/publications.html`):

```sh
python3 scripts/update_publications.py
```

The selected publications and standards above that block are edited by hand.

To preview locally:

```sh
python3 -m http.server -d public 8000
```

## Deployment

GitHub Pages must use **Settings → Pages → Source: GitHub Actions**. The custom
domain is set in the same settings page; `public/CNAME` is kept for reference.
