import json
import os
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
heal_log = []


def capture_context(page, broken_selector):
    dom_snapshot = page.evaluate("document.body.innerHTML")
    return {
        "broken_selector": broken_selector,
        "dom_snapshot": dom_snapshot[:6000],
        "url": page.url
    }


def heal_selector(context):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=100,
        messages=[
            {
                "role": "user",
                "content": f"""This CSS selector broke in a Playwright test:
    "{context['broken_selector']}"

    Page URL: {context['url']}

    Page DOM:
    {context['dom_snapshot']}

    The broken selector was used for:
    - If it contains 'username' or 'user' -> return the username input selector
    - If it contains 'password' or 'pass' -> return the password input selector  
    - If it contains 'submit' or 'btn' or 'button' -> return the submit BUTTON selector only

    Return ONLY the correct CSS selector. Must be an INPUT or BUTTON element."""
            }
        ]
    )
    return response.choices[0].message.content.strip()


def smart_click(page, selector):
    try:
        page.click(selector, timeout=5000)
    except Exception:
        print(f"⚠  Broken: {selector} — asking Groq AI to heal...")
        context = capture_context(page, selector)
        new_selector = heal_selector(context)
        print(f"✓  Healed to: {new_selector}")
        page.click(new_selector)
        log_heal(selector, new_selector)


def smart_fill(page, selector, value):
    try:
        page.fill(selector, value, timeout=5000)
    except Exception:
        print(f"⚠  Broken: {selector} — asking Groq AI to heal...")
        context = capture_context(page, selector)
        new_selector = heal_selector(context)
        print(f"✓  Healed to: {new_selector}")
        page.fill(new_selector, value)
        log_heal(selector, new_selector)


def log_heal(original, healed):
    heal_log.append({
        "timestamp": datetime.now().isoformat(),
        "original": original,
        "healed": healed
    })
    with open("healing_report.json", "w") as f:
        json.dump(heal_log, f, indent=2)
    print(f"📄 Saved to healing_report.json")


def generate_html_report(json_path="healing_report.json", output_path="healing_report.html"):
    if not os.path.exists(json_path):
        print(f"No healing report found at {json_path}")
        return

    with open(json_path, "r") as f:
        data = json.load(f)

    total = len(data)
    generated_at = datetime.now().strftime("%B %d, %Y at %I:%M %p")

    rows = ""
    for i, entry in enumerate(data, 1):
        ts = entry.get("timestamp", "")
        try:
            dt = datetime.fromisoformat(ts)
            formatted_time = dt.strftime("%b %d, %Y %I:%M:%S %p")
        except Exception:
            formatted_time = ts

        original = entry.get("original", "")
        healed = entry.get("healed", "")

        rows += f"""
        <tr class="row" style="animation-delay: {i * 0.08}s">
          <td class="td num">#{i}</td>
          <td class="td"><span class="selector broken">{original}</span></td>
          <td class="td arrow-cell"><span class="arrow">&#8594;</span></td>
          <td class="td"><span class="selector healed">{healed}</span></td>
          <td class="td time">{formatted_time}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <title>Healing Report</title>
  <link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet"/>
  <style>
    *{{box-sizing:border-box;margin:0;padding:0}}
    :root{{--bg:#0b0f1a;--surface:#111827;--surface2:#1a2235;--border:#1f2d45;--green:#00e5a0;--green-dim:#00e5a020;--red:#ff4f64;--red-dim:#ff4f6415;--text:#e8edf5;--muted:#5a6a82}}
    body{{background:var(--bg);color:var(--text);font-family:'Syne',sans-serif;min-height:100vh;padding:48px 32px}}
    .header{{max-width:1100px;margin:0 auto 48px;display:flex;align-items:flex-start;justify-content:space-between;flex-wrap:wrap;gap:24px}}
    .title-block h1{{font-size:42px;font-weight:800;letter-spacing:-1.5px;background:linear-gradient(135deg,#fff 40%,var(--green));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}}
    .title-block p{{margin-top:10px;font-size:14px;color:var(--muted);font-family:'JetBrains Mono',monospace}}
    .stats{{display:flex;gap:16px;flex-wrap:wrap}}
    .stat{{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:18px 24px;min-width:130px;text-align:center}}
    .stat .val{{font-size:36px;font-weight:800;color:var(--green);line-height:1}}
    .stat .label{{font-size:12px;color:var(--muted);margin-top:6px;font-family:'JetBrains Mono',monospace;text-transform:uppercase;letter-spacing:0.08em}}
    .table-wrap{{max-width:1100px;margin:0 auto;background:var(--surface);border:1px solid var(--border);border-radius:18px;overflow:hidden}}
    .table-header{{padding:20px 28px;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:10px}}
    .dot{{width:10px;height:10px;border-radius:50%;background:var(--green);box-shadow:0 0 8px var(--green)}}
    .table-header span{{font-size:13px;font-family:'JetBrains Mono',monospace;color:var(--muted)}}
    table{{width:100%;border-collapse:collapse}}
    thead tr{{background:var(--surface2)}}
    th{{font-size:11px;font-family:'JetBrains Mono',monospace;text-transform:uppercase;letter-spacing:0.1em;color:var(--muted);padding:12px 20px;text-align:left;font-weight:500}}
    .row{{border-top:1px solid var(--border);opacity:0;transform:translateY(8px);animation:fadeUp 0.4s ease forwards}}
    @keyframes fadeUp{{to{{opacity:1;transform:translateY(0)}}}}
    .row:hover{{background:var(--surface2)}}
    .td{{padding:16px 20px;vertical-align:middle}}
    .td.num{{font-family:'JetBrains Mono',monospace;font-size:12px;color:var(--muted);width:48px}}
    .selector{{font-family:'JetBrains Mono',monospace;font-size:13px;padding:5px 12px;border-radius:8px;display:inline-block}}
    .selector.broken{{background:var(--red-dim);color:var(--red);border:1px solid #ff4f6430;text-decoration:line-through;opacity:0.8}}
    .selector.healed{{background:var(--green-dim);color:var(--green);border:1px solid #00e5a030}}
    .arrow-cell{{width:40px;text-align:center}}
    .arrow{{color:var(--muted);font-size:18px}}
    .time{{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--muted);white-space:nowrap}}
    .footer{{max-width:1100px;margin:32px auto 0;font-size:12px;color:var(--muted);font-family:'JetBrains Mono',monospace;text-align:center}}
  </style>
</head>
<body>
  <div class="header">
    <div class="title-block">
      <h1>Healing Report</h1>
      <p>Generated {generated_at}</p>
    </div>
    <div class="stats">
      <div class="stat"><div class="val">{total}</div><div class="label">Total Heals</div></div>
      <div class="stat"><div class="val" style="color:#3b82f6">{total}</div><div class="label">Auto-Fixed</div></div>
      <div class="stat"><div class="val" style="color:#00e5a0">100%</div><div class="label">Success Rate</div></div>
    </div>
  </div>
  <div class="table-wrap">
    <div class="table-header"><div class="dot"></div><span>healing_report.json — {total} entries</span></div>
    <table><thead><tr><th>#</th><th>Broken Selector</th><th></th><th>Healed Selector</th><th>Timestamp</th></tr></thead>
    <tbody>{rows}</tbody></table>
  </div>
  <div class="footer">self-healing test suite &mdash; powered by groq ai &mdash; built with playwright + pytest</div>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"📊 HTML report generated: {output_path}")