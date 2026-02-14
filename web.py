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

    # Only non-empty values in filters; "All" is in the template, no dash option
    status_options = "".join(f'<option value="{_esc(x)}">{_esc(x)}</option>' for x in statuses)
    country_options = "".join(f'<option value="{_esc(x)}">{_esc(x)}</option>' for x in countries)
    entry_options = "".join(f'<option value="{_esc(x)}">{_esc(x)}</option>' for x in entries)

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
      background: #0f172a;
      color: #e2e8f0;
      padding: clamp(0.75rem, 4vw, 2rem);
      font-size: clamp(14px, 2vw, 15px);
      line-height: 1.5;
    }}
    .wrap {{ max-width: 1200px; margin: 0 auto; width: 100%; }}
    h1 {{
      font-weight: 700;
      font-size: clamp(1.4rem, 4vw, 1.9rem);
      letter-spacing: -0.02em;
      color: #38bdf8;
      margin: 0 0 1rem 0;
    }}
    .filters {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.75rem;
      align-items: center;
      margin-bottom: 1.25rem;
      padding: 0.85rem 1rem;
      background: #1e293b;
      border-radius: 10px;
      border: 1px solid #334155;
    }}
    .filters label {{
      font-weight: 600;
      font-size: 0.8rem;
      color: #94a3b8;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}
    .filters select {{
      padding: 0.45rem 0.65rem;
      border-radius: 6px;
      border: 1px solid #475569;
      background: #1e293b;
      color: #e2e8f0;
      font-family: inherit;
      font-size: 0.9rem;
      min-width: 140px;
    }}
    .filters select:focus {{ outline: none; border-color: #38bdf8; }}
    .table-wrap {{
      background: #1e293b;
      border-radius: 12px;
      overflow-x: auto;
      overflow-y: visible;
      -webkit-overflow-scrolling: touch;
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
      border: 1px solid #334155;
    }}
    table {{ width: 100%; min-width: 900px; border-collapse: collapse; font-weight: 500; table-layout: auto; }}
    th {{
      font-weight: 600;
      font-size: 0.7rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #38bdf8;
      background: #0f172a;
      padding: 0.75rem 0.6rem;
      text-align: left;
      border-bottom: 1px solid #334155;
      white-space: nowrap;
    }}
    td {{ padding: 0.7rem 0.6rem; border-bottom: 1px solid #334155; }}
    td:nth-child(4), td:nth-child(5), td:nth-child(9) {{ white-space: nowrap; }}
    tr:last-child td {{ border-bottom: none; }}
    tr:hover td {{ background: #334155; }}
    tr.hidden {{ display: none; }}
    tr:nth-child(even) td {{ background: #1e293b; }}
    tr:nth-child(even):hover td {{ background: #334155; }}
    tr.rejected td {{
      background: #7f1d1d !important;
      color: #fecaca;
      border-bottom-color: #991b1b;
    }}
    tr.rejected:hover td {{ background: #991b1b !important; }}
    a {{ color: #38bdf8; text-decoration: none; font-weight: 500; }}
    a:hover {{ color: #7dd3fc; text-decoration: underline; }}
    .count {{ color: #94a3b8; font-size: 0.85rem; margin-left: auto; }}
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
