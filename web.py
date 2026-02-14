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
            f'<tr{row_class}{data_attr}>'
            f'<td data-label="University">{uni}</td><td data-label="Program">{program}</td><td data-label="Scholarship">{scholarship}</td>'
            f'<td data-label="Deadline">{deadline}</td><td data-label="Application date">{app_date}</td><td data-label="Status">{status}</td>'
            f'<td data-label="Point of Entry">{entry}</td><td data-label="Country">{country}</td><td data-label="Link">{link_cell}</td></tr>'
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
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>Scholarship Application Tracker</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    * {{ box-sizing: border-box; }}
    html {{ -webkit-text-size-adjust: 100%; }}
    body {{
      font-family: 'DM Sans', system-ui, sans-serif;
      margin: 0;
      min-height: 100vh;
      min-height: 100dvh;
      background: #0f172a;
      color: #e2e8f0;
      padding: clamp(0.75rem, 4vw, 2rem);
      padding-left: max(clamp(0.75rem, 4vw, 2rem), env(safe-area-inset-left));
      padding-right: max(clamp(0.75rem, 4vw, 2rem), env(safe-area-inset-right));
      padding-bottom: max(clamp(0.75rem, 4vw, 2rem), env(safe-area-inset-bottom));
      font-size: clamp(14px, 2vw, 15px);
      line-height: 1.5;
    }}
    .wrap {{ max-width: 1200px; margin: 0 auto; width: 100%; }}
    h1 {{
      font-weight: 700;
      font-size: clamp(1.25rem, 4vw, 1.9rem);
      letter-spacing: -0.02em;
      color: #38bdf8;
      margin: 0 0 clamp(0.75rem, 3vw, 1rem) 0;
      padding-right: env(safe-area-inset-right);
    }}
    .filters {{
      display: flex;
      flex-wrap: wrap;
      gap: clamp(0.5rem, 2vw, 0.75rem);
      align-items: flex-end;
      margin-bottom: clamp(1rem, 3vw, 1.25rem);
      padding: clamp(0.75rem, 2.5vw, 1rem);
      background: #1e293b;
      border-radius: 10px;
      border: 1px solid #334155;
    }}
    .filters > div {{
      flex: 1 1 auto;
      min-width: 0;
    }}
    .filters label {{
      display: block;
      font-weight: 600;
      font-size: 0.75rem;
      color: #94a3b8;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      margin-bottom: 0.35rem;
    }}
    .filters select {{
      width: 100%;
      min-height: 44px;
      padding: 0.6rem 0.75rem;
      border-radius: 8px;
      border: 1px solid #475569;
      background: #1e293b;
      color: #e2e8f0;
      font-family: inherit;
      font-size: 1rem;
      min-width: 0;
      -webkit-appearance: none;
      appearance: none;
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' fill='%2394a3b8' viewBox='0 0 16 16'%3E%3Cpath d='M8 11L3 6h10l-5 5z'/%3E%3C/svg%3E");
      background-repeat: no-repeat;
      background-position: right 0.6rem center;
      padding-right: 2rem;
    }}
    .filters select:focus {{ outline: none; border-color: #38bdf8; }}
    .count {{
      color: #94a3b8;
      font-size: clamp(0.8rem, 2vw, 0.85rem);
      margin-left: auto;
      flex-basis: 100%;
      text-align: right;
      padding-top: 0.25rem;
    }}
    .table-wrap {{
      background: #1e293b;
      border-radius: 12px;
      overflow-x: auto;
      overflow-y: visible;
      -webkit-overflow-scrolling: touch;
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
      border: 1px solid #334155;
    }}
    .table-wrap::-webkit-scrollbar {{ height: 8px; }}
    .table-wrap::-webkit-scrollbar-thumb {{ background: #475569; border-radius: 4px; }}
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
    th:nth-child(4), td:nth-child(4), th:nth-child(5), td:nth-child(5) {{ width: 1%; white-space: nowrap; }}
    th:nth-child(9), td:nth-child(9) {{ width: 1%; white-space: nowrap; }}
    tr:last-child td {{ border-bottom: none; }}
    tr:hover td {{ background: #334355; }}
    tr.hidden {{ display: none; }}
    tr:nth-child(even) td {{ background: #1e293b; }}
    tr:nth-child(even):hover td {{ background: #334355; }}
    tr.rejected td {{
      background: #7f1d1d !important;
      color: #fecaca;
      border-bottom-color: #991b1b;
    }}
    tr.rejected:hover td {{ background: #991b1b !important; }}
    a {{ color: #38bdf8; text-decoration: none; font-weight: 500; }}
    a:hover {{ color: #7dd3fc; text-decoration: underline; }}
    a:focus-visible {{ outline: 2px solid #38bdf8; outline-offset: 2px; }}

    /* Tablet: tighter filters */
    @media (max-width: 900px) {{
      .filters > div {{ min-width: 120px; }}
      .count {{ flex-basis: auto; }}
    }}

    /* Mobile: stacked filters, larger touch targets */
    @media (max-width: 640px) {{
      body {{ padding: 0.75rem; }}
      .filters {{ flex-direction: column; align-items: stretch; gap: 0.75rem; }}
      .filters > div {{ min-width: 0; }}
      .filters select {{ min-height: 48px; font-size: 16px; }}
      .count {{ flex-basis: auto; padding-top: 0; }}
    }}

    /* Mobile: card layout instead of table */
    @media (max-width: 640px) {{
      .table-wrap {{ overflow: visible; padding: 0.5rem; }}
      .table-wrap table {{ min-width: 0; display: block; }}
      .table-wrap thead {{ display: none; }}
      .table-wrap tbody {{ display: block; }}
      .table-wrap tr {{
        display: block;
        margin-bottom: 1rem;
        padding: 1rem;
        background: #0f172a;
        border-radius: 10px;
        border: 1px solid #334155;
      }}
      .table-wrap tr:last-child {{ margin-bottom: 0; }}
      .table-wrap tr.hidden {{ display: none; }}
      .table-wrap tr:nth-child(even) {{ background: #172033; }}
      .table-wrap tr.rejected {{
        background: #7f1d1d !important;
        border-color: #991b1b;
      }}
      .table-wrap td {{
        display: flex;
        align-items: flex-start;
        gap: 0.5rem;
        padding: 0.4rem 0;
        border-bottom: 1px solid rgba(51, 65, 85, 0.5);
      }}
      .table-wrap td:last-child {{ border-bottom: none; }}
      .table-wrap td::before {{
        content: attr(data-label);
        font-weight: 600;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: #38bdf8;
        flex: 0 0 7rem;
        min-width: 7rem;
      }}
      .table-wrap td[colspan] {{ display: block; padding: 1rem; text-align: center; }}
      .table-wrap td[colspan]::before {{ display: none; }}
    }}

    /* Small phones */
    @media (max-width: 380px) {{
      body {{ padding: 0.5rem; }}
      .filters {{ padding: 0.6rem; }}
      .table-wrap {{ padding: 0.35rem; }}
      .table-wrap tr {{ padding: 0.75rem; }}
      .table-wrap td::before {{ flex: 0 0 6rem; min-width: 6rem; font-size: 0.65rem; }}
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
