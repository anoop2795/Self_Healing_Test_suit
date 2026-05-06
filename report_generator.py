import json
import os
from datetime import datetime


def generate_report(json_path="healing_report.json", output_path="healing_report.html"):
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

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("<html><body>" + rows + "</body></html>")

    print(f"✅ Report generated: {output_path}")


if __name__ == "__main__":
    generate_report()