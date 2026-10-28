#!/usr/bin/env python3
"""Regenerate the publication list of public/research/publications.html from HAL.

Only the block between <!-- hal:start --> and <!-- hal:end --> is replaced; the rest
of the page is edited by hand. Standard library only:

    python3 scripts/update_publications.py
"""

import html
import json
import re
import sys
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

HAL_ID = "mlefranc"
PAGE = Path(__file__).resolve().parent.parent / "public" / "research" / "publications.html"
FIELDS = ("halId_s,uri_s,docType_s,title_s,authFullName_s,producedDateY_i,journalTitle_s,"
          "conferenceTitle_s,bookTitle_s,city_s,volume_s,issue_s,page_s,doiId_s,fileMain_s")

# HAL document type -> (group key, label shown on each entry).
TYPES = {
    "ART": ("journal", "Journal"),
    "COMM": ("conference", "Conference"),
    "COUV": ("chapter", "Chapter"),
    "OUV": ("chapter", "Book"),
    "PROCEEDINGS": ("edited", "Proceedings"),
    "ISSUE": ("edited", "Special issue"),
    "REPORT": ("report", "Report"),
    "UNDEFINED": ("report", "Preprint"),
    "THESE": ("other", "PhD thesis"),
    "POSTER": ("other", "Poster"),
    "SOFTWARE": ("other", "Software"),
    "BLOG": ("other", "Outreach"),
}
# Group key -> heading when the list is grouped by type, in display order.
FILTERS = {"journal": "Journals", "conference": "Conferences", "chapter": "Books and chapters",
           "edited": "Edited volumes", "report": "Reports and preprints", "other": "Other"}


def fetch():
    query = urllib.parse.urlencode({
        "q": f"authIdHal_s:{HAL_ID}", "fl": FIELDS, "rows": 1000, "wt": "json",
        "sort": "producedDateY_i desc,docType_s asc",
    })
    with urllib.request.urlopen(f"https://api.archives-ouvertes.fr/search/?{query}", timeout=60) as r:
        return json.load(r)["response"]["docs"]


def esc(s):
    return html.escape(str(s), quote=True)


def authors(names):
    out = [f"<b>{esc(n)}</b>" if "Lefran" in n else esc(n) for n in names]
    if len(out) > 8:
        out = out[:6] + ["…"] + out[-1:]
    return ", ".join(out)


def venue(d):
    parts = [d.get("journalTitle_s") or d.get("conferenceTitle_s") or d.get("bookTitle_s") or ""]
    if d.get("volume_s"):
        parts.append(f"vol. {d['volume_s']}" + (f"({d['issue_s'][0]})" if d.get("issue_s") else ""))
    if d.get("page_s"):
        parts.append(f"pp. {d['page_s']}")
    if d.get("city_s") and d.get("conferenceTitle_s"):
        parts.append(d["city_s"])
    return ", ".join(esc(p) for p in parts if p)


def entry(d):
    key, label = TYPES.get(d["docType_s"], ("other", "Other"))
    title = d["title_s"][0]
    acts = [f'<a href="{esc(d["uri_s"])}">HAL</a>']
    if d.get("fileMain_s"):
        acts.append(f'<a href="{esc(d["fileMain_s"])}">PDF</a>')
    if d.get("doiId_s"):
        acts.append(f'<a href="https://doi.org/{esc(d["doiId_s"])}">DOI</a>')
    v = venue(d)
    y = d.get("producedDateY_i", "n.d.")
    return (f'      <li data-type="{key}" data-group="{FILTERS[key]}" data-year="{y}">\n'
            f'        <span class="title">{esc(title)}</span>\n'
            f'        <span class="authors">{authors(d.get("authFullName_s", []))}</span>\n'
            f'        <span class="venue"><span class="tag">{label}</span><span class="tag pub-y">{y}</span>{v}</span>\n'
            f'        <span class="acts">{" ".join(acts)}</span>\n'
            f'      </li>')


def render(docs):
    lines = [f'<p class="muted">{len(docs)} documents in HAL, retrieved on {date.today():%d %B %Y}.</p>',
             '<fieldset class="filters" id="pub-sort" hidden>',
             '  <legend>Group by</legend>',
             '  <button type="button" data-sort="year" aria-pressed="true">Year</button>',
             '  <button type="button" data-sort="type" aria-pressed="false">Type</button>',
             '</fieldset>',
             f'<div id="pub-list" data-types="{" ".join(FILTERS)}">']
    year = None
    for d in docs:
        y = d.get("producedDateY_i", "n.d.")
        if y != year:
            if year is not None:
                lines.append('    </ol>\n  </div>')
            lines.append(f'  <div class="pub-group">\n    <h3 class="pub-year">{y}</h3>\n    <ol class="pubs">')
            year = y
        lines.append(entry(d))
    if year is not None:
        lines.append('    </ol>\n  </div>')
    lines.append('</div>')
    return "\n".join(lines)


def main():
    docs = fetch()
    page = PAGE.read_text(encoding="utf-8")
    new, n = re.subn(r"(<!-- hal:start -->).*?(<!-- hal:end -->)",
                     lambda m: f"{m.group(1)}\n{render(docs)}\n{m.group(2)}", page, flags=re.S)
    if n != 1:
        sys.exit(f"Markers not found in {PAGE}")
    PAGE.write_text(new, encoding="utf-8")
    print(f"{len(docs)} publications written to {PAGE}")


if __name__ == "__main__":
    main()
