"""Web view: build HTML for Scholarship Application Tracker with filters."""

import html

from sheet_loader import load_scholarships


def _esc(s: str) -> str:
    return html.escape(str(s or "").strip())


def _unique_sorted(values: set[str]) -> list[str]:
    return sorted((v for v in values if v), key=str.lower)


def _status_to_row_class(status: str) -> str:
    """Map application status to a CSS class. Statuses: Accepted, Admissions Review, Application Submitted, Rejected, In Progress."""
    s = (status or "").strip().lower()
    if not s:
        return ""
    if "rejected" in s:
        return "rejected"
    if "accepted" in s:
        return "status-accepted"
    if "in progress" in s:
        return "status-pending"
    if "admissions review" in s or "admission review" in s:
        return "status-admissions-review"
    if "application submitted" in s or "submitted" in s:
        return "status-applied"
    return ""


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
        status_class = _status_to_row_class(s.get("application_status") or "")
        row_class = f' class="{status_class}"' if status_class else ""
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
  <link rel="icon" type="image/png" href="/favicon.png">
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
      background: #f1f5f9;
      color: #1e293b;
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
      color: #0284c7;
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
      background: #ffffff;
      border-radius: 10px;
      border: 1px solid #e2e8f0;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
    }}
    .filters > div {{
      flex: 1 1 auto;
      min-width: 0;
    }}
    .filter-dropdown {{
      position: relative;
      width: 100%;
      min-width: 0;
    }}
    .filters label {{
      display: block;
      font-weight: 600;
      font-size: 0.75rem;
      color: #64748b;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      margin-bottom: 0.35rem;
    }}
    .filter-dropdown select {{
      position: absolute;
      width: 1px;
      height: 1px;
      padding: 0;
      margin: -1px;
      overflow: hidden;
      clip: rect(0, 0, 0, 0);
      border: 0;
      opacity: 0;
      pointer-events: none;
    }}
    .filter-dropdown__trigger {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      width: 100%;
      min-height: 44px;
      padding: 0.6rem 0.75rem;
      border-radius: 12px;
      border: 1px solid #cbd5e1;
      background: #ffffff;
      color: #1e293b;
      font-family: inherit;
      font-size: 1rem;
      text-align: left;
      cursor: pointer;
      transition: border-color 0.2s, box-shadow 0.2s;
      -webkit-tap-highlight-color: transparent;
    }}
    .filter-dropdown__trigger:hover {{
      border-color: #94a3b8;
    }}
    .filter-dropdown__trigger:focus {{
      outline: none;
      border-color: #0284c7;
      box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.2);
    }}
    .filter-dropdown__trigger[aria-expanded="true"] {{
      border-color: #0284c7;
      box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.2);
    }}
    .filter-dropdown__trigger .filter-dropdown__arrow {{
      flex-shrink: 0;
      margin-left: 0.5rem;
      transition: transform 0.2s;
    }}
    .filter-dropdown__trigger[aria-expanded="true"] .filter-dropdown__arrow {{
      transform: rotate(180deg);
    }}
    .filter-dropdown__list {{
      position: absolute;
      top: calc(100% + 4px);
      left: 0;
      right: 0;
      z-index: 50;
      max-height: min(280px, 60vh);
      overflow-y: auto;
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 12px;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.05);
      padding: 6px;
    }}
    .filter-dropdown__list[hidden] {{
      display: none;
    }}
    .filter-dropdown__option {{
      display: block;
      width: 100%;
      padding: 0.5rem 0.75rem;
      border: none;
      border-radius: 8px;
      background: transparent;
      color: #1e293b;
      font-family: inherit;
      font-size: 0.9375rem;
      text-align: left;
      cursor: pointer;
      transition: background 0.15s;
    }}
    .filter-dropdown__option:hover {{
      background: #f1f5f9;
    }}
    .filter-dropdown__option[aria-selected="true"] {{
      background: #e0f2fe;
      color: #0284c7;
      font-weight: 500;
    }}
    .filter-dropdown__list::-webkit-scrollbar {{
      width: 6px;
    }}
    .filter-dropdown__list::-webkit-scrollbar-thumb {{
      background: #cbd5e1;
      border-radius: 3px;
    }}
    .count {{
      color: #64748b;
      font-size: clamp(0.8rem, 2vw, 0.85rem);
      margin-left: auto;
      flex-basis: 100%;
      text-align: right;
      padding-top: 0.25rem;
    }}
    .table-wrap {{
      background: #ffffff;
      border-radius: 12px;
      overflow-x: auto;
      overflow-y: visible;
      -webkit-overflow-scrolling: touch;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
      border: 1px solid #e2e8f0;
    }}
    .table-wrap::-webkit-scrollbar {{ height: 8px; }}
    .table-wrap::-webkit-scrollbar-thumb {{ background: #cbd5e1; border-radius: 4px; }}
    table {{ width: 100%; min-width: 900px; border-collapse: collapse; font-weight: 500; table-layout: auto; }}
    th {{
      font-weight: 600;
      font-size: 0.7rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #0284c7;
      background: #f8fafc;
      padding: 0.75rem 0.6rem;
      text-align: left;
      border-bottom: 1px solid #e2e8f0;
      white-space: nowrap;
    }}
    td {{ padding: 0.7rem 0.6rem; border-bottom: 1px solid #e2e8f0; }}
    th:nth-child(4), td:nth-child(4), th:nth-child(5), td:nth-child(5) {{ width: 1%; white-space: nowrap; }}
    th:nth-child(9), td:nth-child(9) {{ width: 1%; white-space: nowrap; }}
    tr:last-child td {{ border-bottom: none; }}
    tr:hover td {{ background: #f8fafc; }}
    tr.hidden {{ display: none; }}
    tr:nth-child(even) td {{ background: #f8fafc; }}
    tr:nth-child(even):hover td {{ background: #f1f5f9; }}
    tr.rejected td {{
      background: #fef2f2 !important;
      color: #b91c1c;
      border-bottom-color: #fecaca;
    }}
    tr.rejected:hover td {{ background: #fee2e2 !important; }}
    tr.status-accepted td {{
      background: #f0fdf4 !important;
      color: #166534;
      border-bottom-color: #bbf7d0;
    }}
    tr.status-accepted:hover td {{ background: #dcfce7 !important; }}
    tr.status-pending td {{
      background: #fffbeb !important;
      color: #b45309;
      border-bottom-color: #fde68a;
    }}
    tr.status-pending:hover td {{ background: #fef3c7 !important; }}
    tr.status-admissions-review td {{
      background: #f5f3ff !important;
      color: #5b21b6;
      border-bottom-color: #ddd6fe;
    }}
    tr.status-admissions-review:hover td {{ background: #ede9fe !important; }}
    tr.status-applied td {{
      background: #eff6ff !important;
      color: #1e40af;
      border-bottom-color: #bfdbfe;
    }}
    tr.status-applied:hover td {{ background: #dbeafe !important; }}
    a {{ color: #0284c7; text-decoration: none; font-weight: 500; }}
    a:hover {{ color: #0369a1; text-decoration: underline; }}
    a:focus-visible {{ outline: 2px solid #0284c7; outline-offset: 2px; }}

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
      .filter-dropdown__trigger {{ min-height: 48px; font-size: 16px; }}
      .filter-dropdown__option {{ padding: 0.65rem 0.75rem; min-height: 44px; }}
      .filter-dropdown__list {{ max-height: min(260px, 50vh); }}
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
        background: #ffffff;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
      }}
      .table-wrap tr:last-child {{ margin-bottom: 0; }}
      .table-wrap tr.hidden {{ display: none; }}
      .table-wrap tr:nth-child(even) {{ background: #f8fafc; }}
      .table-wrap tr.rejected {{
        background: #fef2f2 !important;
        border-color: #fecaca;
      }}
      .table-wrap tr.status-accepted {{
        background: #f0fdf4 !important;
        border-color: #bbf7d0;
      }}
      .table-wrap tr.status-pending {{
        background: #fffbeb !important;
        border-color: #fde68a;
      }}
      .table-wrap tr.status-admissions-review {{
        background: #f5f3ff !important;
        border-color: #ddd6fe;
      }}
      .table-wrap tr.status-applied {{
        background: #eff6ff !important;
        border-color: #bfdbfe;
      }}
      .table-wrap td {{
        display: flex;
        align-items: flex-start;
        gap: 0.5rem;
        padding: 0.4rem 0;
        border-bottom: 1px solid rgba(226, 232, 240, 0.8);
      }}
      .table-wrap td:last-child {{ border-bottom: none; }}
      .table-wrap td::before {{
        content: attr(data-label);
        font-weight: 600;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: #0284c7;
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
      <div class="filter-dropdown">
        <label for="filter-status-trigger">Status</label>
        <select id="filter-status" aria-hidden="true" tabindex="-1"><option value="">All</option>{status_options}</select>
        <button type="button" id="filter-status-trigger" class="filter-dropdown__trigger" aria-haspopup="listbox" aria-expanded="false"><span class="filter-dropdown__label">All</span><span class="filter-dropdown__arrow" aria-hidden="true"><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="currentColor" viewBox="0 0 16 16"><path d="M8 11L3 6h10l-5 5z"/></svg></span></button>
        <div id="filter-status-list" class="filter-dropdown__list" role="listbox" hidden></div>
      </div>
      <div class="filter-dropdown">
        <label for="filter-country-trigger">Country</label>
        <select id="filter-country" aria-hidden="true" tabindex="-1"><option value="">All</option>{country_options}</select>
        <button type="button" id="filter-country-trigger" class="filter-dropdown__trigger" aria-haspopup="listbox" aria-expanded="false"><span class="filter-dropdown__label">All</span><span class="filter-dropdown__arrow" aria-hidden="true"><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="currentColor" viewBox="0 0 16 16"><path d="M8 11L3 6h10l-5 5z"/></svg></span></button>
        <div id="filter-country-list" class="filter-dropdown__list" role="listbox" hidden></div>
      </div>
      <div class="filter-dropdown">
        <label for="filter-entry-trigger">Point of Entry</label>
        <select id="filter-entry" aria-hidden="true" tabindex="-1"><option value="">All</option>{entry_options}</select>
        <button type="button" id="filter-entry-trigger" class="filter-dropdown__trigger" aria-haspopup="listbox" aria-expanded="false"><span class="filter-dropdown__label">All</span><span class="filter-dropdown__arrow" aria-hidden="true"><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="currentColor" viewBox="0 0 16 16"><path d="M8 11L3 6h10l-5 5z"/></svg></span></button>
        <div id="filter-entry-list" class="filter-dropdown__list" role="listbox" hidden></div>
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

      var dropdowns = [
        {{ sel: statusSel, trigger: document.getElementById('filter-status-trigger'), list: document.getElementById('filter-status-list') }},
        {{ sel: countrySel, trigger: document.getElementById('filter-country-trigger'), list: document.getElementById('filter-country-list') }},
        {{ sel: entrySel, trigger: document.getElementById('filter-entry-trigger'), list: document.getElementById('filter-entry-list') }}
      ];

      function setTriggerText(d) {{
        if (!d || !d.sel || !d.trigger) return;
        var opt = d.sel.options[d.sel.selectedIndex];
        var label = d.trigger.querySelector('.filter-dropdown__label');
        if (label) label.textContent = opt ? opt.text : 'All';
      }}

      function closeAll() {{
        dropdowns.forEach(function(d) {{
          if (d.trigger) d.trigger.setAttribute('aria-expanded', 'false');
          if (d.list) d.list.setAttribute('hidden', '');
        }});
      }}

      function buildList(d) {{
        if (!d.sel || !d.list) return;
        d.list.innerHTML = '';
        for (var i = 0; i < d.sel.options.length; i++) {{
          var opt = d.sel.options[i];
          var item = document.createElement('div');
          item.setAttribute('role', 'option');
          item.setAttribute('aria-selected', d.sel.value === opt.value ? 'true' : 'false');
          item.setAttribute('data-value', opt.value);
          item.className = 'filter-dropdown__option';
          item.textContent = opt.text || 'All';
          (function(sel, listEl, val) {{
            item.addEventListener('click', function() {{
              sel.value = val;
              sel.dispatchEvent(new Event('change', {{ bubbles: true }}));
              setTriggerText(d);
              closeAll();
            }});
          }})(d.sel, d.list, opt.value);
          d.list.appendChild(item);
        }}
      }}

      dropdowns.forEach(function(d) {{
        buildList(d);
        setTriggerText(d);
        if (d.trigger && d.list) {{
          d.trigger.addEventListener('click', function(e) {{
            e.preventDefault();
            var open = d.trigger.getAttribute('aria-expanded') === 'true';
            closeAll();
            if (!open) {{
              d.trigger.setAttribute('aria-expanded', 'true');
              d.list.removeAttribute('hidden');
              buildList(d);
              var opts = d.list.querySelectorAll('.filter-dropdown__option');
              for (var j = 0; j < opts.length; j++) {{
                opts[j].setAttribute('aria-selected', d.sel.value === opts[j].getAttribute('data-value') ? 'true' : 'false');
              }}
            }}
          }});
        }}
      }});

      document.addEventListener('click', function(e) {{
        if (!e.target.closest('.filter-dropdown')) closeAll();
      }});

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
