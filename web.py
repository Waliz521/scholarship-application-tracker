"""Web view: build HTML for Scholarship Application Tracker with filters."""

import html

from sheet_loader import load_scholarships


def _esc(s: str) -> str:
    return html.escape(str(s or "").strip())


def _unique_sorted(values: set[str]) -> list[str]:
    return sorted((v for v in values if v), key=str.lower)


def build_html(scholarships: list[dict] | None = None) -> str:
    if scholarships is None:
        scholarships = load_scholarships(use_local_fallback=True)

    statuses = _unique_sorted({s.get("application_status") or "" for s in scholarships})
    countries = _unique_sorted({s.get("country") or "" for s in scholarships})
    entries = _unique_sorted({s.get("point_of_entry") or "" for s in scholarships})

    rows = []
    for s in scholarships:
        uni = _esc(s.get("university"))
        program = _esc(s.get("program"))
        scholarship = _esc(s.get("scholarship"))
        deadline = _esc(s.get("deadline"))
        app_date = _esc(s.get("application_date"))
        status = _esc(s.get("application_status"))
        entry = _esc(s.get("point_of_entry"))
        country = _esc(s.get("country"))
        link = (s.get("link") or "").strip()
        link_cell = f'<a href="{_esc(link)}" target="_blank" rel="noopener">Link</a>' if link else "—"
        is_rejected = status.lower() == "rejected"
        row_class = ' class="rejected"' if is_rejected else ""
        data_attr = f' data-status="{_esc(status)}" data-country="{_esc(country)}" data-entry="{_esc(entry)}"'
        rows.append(
            f'<tr{row_class}{data_attr}><td>{uni}</td><td>{program}</td><td>{scholarship}</td>'
            f'<td>{deadline}</td><td>{app_date}</td><td>{status}</td><td>{entry}</td><td>{country}</td><td>{link_cell}</td></tr>'
        )

    body = "\n".join(rows) if rows else '<tr><td colspan="9">No scholarships yet. Share the sheet as &quot;Anyone with the link can view&quot;.</td></tr>'

    status_options = "".join(f'<option value="{_esc(x)}">{_esc(x) or "—"}</option>' for x in ["", *statuses])
    country_options = "".join(f'<option value="{_esc(x)}">{_esc(x) or "—"}</option>' for x in ["", *countries])
    entry_options = "".join(f'<option value="{_esc(x)}">{_esc(x) or "—"}</option>' for x in ["", *entries])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Scholarship Application Tracker</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      font-family: 'DM Sans', system-ui, sans-serif;
      margin: 0;
      min-height: 100vh;
      background: linear-gradient(160deg, #0c1445 0%, #1a237e 35%, #283593 100%);
      color: #e8eaf6;
      padding: clamp(0.75rem, 4vw, 2rem);
      font-size: clamp(14px, 2vw, 15px);
      line-height: 1.5;
    }}
    .wrap {{ max-width: 1200px; margin: 0 auto; width: 100%; }}
    h1 {{
      font-weight: 700;
      font-size: clamp(1.4rem, 4vw, 1.9rem);
      letter-spacing: -0.02em;
      color: #ffc107;
      margin: 0 0 1rem 0;
      text-shadow: 0 0 32px rgba(255, 193, 7, 0.35);
    }}
    .filters {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.75rem;
      align-items: center;
      margin-bottom: 1.25rem;
      padding: 0.85rem 1rem;
      background: rgba(13, 20, 70, 0.6);
      border-radius: 10px;
      border: 1px solid rgba(255, 193, 7, 0.15);
    }}
    .filters label {{
      font-weight: 600;
      font-size: 0.8rem;
      color: #ffc107;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}
    .filters select {{
      padding: 0.45rem 0.65rem;
      border-radius: 6px;
      border: 1px solid rgba(255, 193, 7, 0.3);
      background: rgba(13, 20, 70, 0.9);
      color: #e8eaf6;
      font-family: inherit;
      font-size: 0.9rem;
      min-width: 140px;
    }}
    .filters select:focus {{ outline: none; border-color: #ffc107; }}
    .table-wrap {{
      background: rgba(13, 20, 70, 0.5);
      border-radius: 12px;
      overflow-x: auto;
      -webkit-overflow-scrolling: touch;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
      border: 1px solid rgba(255, 193, 7, 0.12);
    }}
    table {{ width: 100%; min-width: 900px; border-collapse: collapse; font-weight: 500; }}
    th {{
      font-weight: 600;
      font-size: 0.7rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #ffc107;
      background: rgba(13, 20, 70, 0.95);
      padding: 0.75rem 0.6rem;
      text-align: left;
      border-bottom: 1px solid rgba(255, 193, 7, 0.25);
      white-space: nowrap;
    }}
    td {{ padding: 0.7rem 0.6rem; border-bottom: 1px solid rgba(255, 255, 255, 0.06); }}
    td:nth-child(4), td:nth-child(5), td:nth-child(9) {{ white-space: nowrap; }}
    tr:last-child td {{ border-bottom: none; }}
    tr:hover td {{ background: rgba(255, 193, 7, 0.06); }}
    tr.hidden {{ display: none; }}
    tr:nth-child(even) td {{ background: rgba(0, 0, 0, 0.12); }}
    tr:nth-child(even):hover td {{ background: rgba(255, 193, 7, 0.08); }}
    tr.rejected td {{
      background: rgba(180, 60, 60, 0.22) !important;
      color: rgba(255, 220, 220, 0.95);
    }}
    tr.rejected:hover td {{ background: rgba(180, 60, 60, 0.32) !important; }}
    a {{ color: #81d4fa; text-decoration: none; font-weight: 500; }}
    a:hover {{ color: #b3e5fc; text-decoration: underline; }}
    .count {{ color: #9fa8da; font-size: 0.85rem; margin-left: auto; }}
    @media (max-width: 768px) {{
      body {{ padding: 0.75rem; }}
      .filters {{ flex-direction: column; align-items: stretch; }}
      .filters select {{ min-width: 0; }}
      th, td {{ padding: 0.6rem 0.5rem; font-size: 0.9rem; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <h1>Scholarship Application Tracker</h1>
    <div class="filters">
      <div>
        <label for="filter-status">Status</label>
        <select id="filter-status"><option value="">All</option>{status_options}</select>
      </div>
      <div>
        <label for="filter-country">Country</label>
        <select id="filter-country"><option value="">All</option>{country_options}</select>
      </div>
      <div>
        <label for="filter-entry">Point of Entry</label>
        <select id="filter-entry"><option value="">All</option>{entry_options}</select>
      </div>
      <span class="count" id="visible-count"></span>
    </div>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>University</th><th>Program</th><th>Scholarship</th><th>Deadline</th>
            <th>Application date</th><th>Status</th><th>Point of Entry</th><th>Country</th><th>Link</th>
          </tr>
        </thead>
        <tbody>{body}</tbody>
      </table>
    </div>
  </div>
  <script>
    (function() {{
      var rows = document.querySelectorAll('tbody tr[data-status]');
      var statusSel = document.getElementById('filter-status');
      var countrySel = document.getElementById('filter-country');
      var entrySel = document.getElementById('filter-entry');
      var countEl = document.getElementById('visible-count');

      function update() {{
        var status = (statusSel && statusSel.value) || '';
        var country = (countrySel && countrySel.value) || '';
        var entry = (entrySel && entrySel.value) || '';
        var visible = 0;
        for (var i = 0; i < rows.length; i++) {{
          var r = rows[i];
          var match = (!status || r.getAttribute('data-status') === status) &&
                      (!country || r.getAttribute('data-country') === country) &&
                      (!entry || r.getAttribute('data-entry') === entry);
          r.classList.toggle('hidden', !match);
          if (match) visible++;
        }}
        if (countEl) countEl.textContent = visible + ' of ' + rows.length + ' shown';
      }}

      if (statusSel) statusSel.addEventListener('change', update);
      if (countrySel) countrySel.addEventListener('change', update);
      if (entrySel) entrySel.addEventListener('change', update);
      update();
    }})();
  </script>
</body>
</html>"""
