from html import escape

<<<<<<< Updated upstream:backend/app/services/report_templates.py

METRICS = ["focus", "posture", "presence", "engagement", "composure"]
=======
from analytics.config import VISUAL_METRICS


METRICS = VISUAL_METRICS
>>>>>>> Stashed changes:backend/app/reporting/templates.py
COLORS = {
    "overall": "#111827",
    "focus": "#2563eb",
    "posture": "#16a34a",
    "presence": "#9333ea",
    "engagement": "#f97316",
    "composure": "#0891b2",
}
LABELS = {
    "overall": "Overall Score",
    "focus": "Focus",
    "posture": "Posture",
    "presence": "Presence",
    "engagement": "Engagement",
    "composure": "Composure",
}


def build_email_html(report: dict) -> str:
    overall = report.get("overall_state") or {}
    metrics = report.get("metrics") or {}

    return page(
        title="Your Presence Report",
        css="body{background:#f8fafc}.wrap{max-width:640px;margin:0 auto;padding:32px 24px}",
        body=f"""
        <main class="wrap">
          {brand()}
          <h1>Your Presence Report is ready</h1>
          <p class="muted">Your full session report is attached as a PDF. Here is a quick snapshot.</p>
          <section class="card">
            <table class="wide"><tr>
              {stat("Overall", report.get("overall_score"), "#16a34a")}
              {stat("Average", overall.get("avg"), "#2563eb")}
              {stat("Trend", overall.get("trend"), "#111827")}
            </tr></table>
          </section>
          <section class="card">
            <h2>Metric Snapshot</h2>
            <table class="wide">{email_metric_rows(metrics)}</table>
          </section>
          <p class="muted small">Open the attached PDF for detailed charts, insights, and recommendations.</p>
        </main>
        """,
    )


def build_pdf_html(report: dict) -> str:
    overall = report.get("overall_state") or {}
    metrics = report.get("metrics") or {}
    timeline = report.get("timeline") or {}
    series = timeline.get("series") or {}
    times = timeline.get("timestampsSec") or []

    return page(
        title="Session Report",
        css=pdf_css(),
        body=f"""
        {brand(right="Your Performance Report")}
        <h1>Session Report</h1>
        <p class="muted">Detailed Performance Analysis</p>

        <section class="card">{kpis(report, overall)}</section>

        {section("1. Overall Score Over Time", chart({"Overall Score": series.get("overall") or []}, times, 160))}
        {section("2. Metrics Summary", metrics_summary(metrics, series), padded=False)}
        {section("3. Detailed Metrics Over Time", detailed_charts(metrics, series, times), "Below are detailed graphs for each metric throughout the session.")}
        {section("4. All Metrics Over Time", chart(all_series(series), times, 180, legend=True), "Comparison of all metrics and overall score throughout the session.")}

        <table class="two"><tr>
          <td>{section("5. Summary", paragraph(report.get("summary")))}</td>
          <td>{section("6. Recommendations", paragraph(report.get("recommendations")))}</td>
        </tr></table>
        """,
    )


def page(title: str, css: str, body: str) -> str:
    return f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>{escape(title)}</title>
    <style>
      body{{margin:0;color:#111827;font-family:Arial,sans-serif;font-size:11px}}
      h1{{margin:0 0 5px;font-size:26px}} h2{{margin:0 0 10px;font-size:13px;text-transform:uppercase}}
      .muted{{color:#64748b}} .small{{font-size:12px}} .wide{{width:100%;border-collapse:collapse}}
      .card{{background:#fff;border:1px solid #cbd5e1;border-radius:6px;padding:12px;margin:14px 0}}
      .label{{color:#475569;font-size:10px;font-weight:700;text-transform:uppercase}}
      .value{{display:block;margin-top:6px;font-size:23px;font-weight:700}}
      {css}
    </style>
  </head>
  <body>{body}</body>
</html>"""


def pdf_css() -> str:
    return """
      @page{size:A4;margin:18mm 16mm}
      .note{margin:0 0 10px;color:#64748b;font-size:10px}
      .metrics th{background:#f8fafc;color:#475569;text-align:left;font-size:10px;padding:8px;border-bottom:1px solid #e2e8f0}
      .metrics td{padding:9px 8px;border-bottom:1px solid #e2e8f0}
      .dot{display:inline-block;width:7px;height:7px;border-radius:50%;margin-right:7px;vertical-align:middle}
      .insight{border:1px solid #d1fae5;background:#f0fdf4;border-radius:6px;padding:13px;min-height:150px}
      .chart-row{width:100%;border-collapse:collapse;margin-bottom:7px;page-break-inside:avoid}
      .stat-card{border:1px solid #dbeafe;background:#f8fbff;border-radius:5px;padding:8px;width:70px}
      .stat-line{margin:0 0 5px;font-size:9px;color:#334155}.stat-label{display:inline-block;min-width:34px;color:#64748b;font-weight:700}
      .legend{margin-bottom:7px;font-size:9px;color:#475569}.legend span{margin-right:13px;white-space:nowrap}
      .two{width:100%;border-collapse:collapse}.two td{width:50%;vertical-align:top;padding-right:8px}
    """


def brand(right: str = "") -> str:
    return f"""
    <table class="wide" style="margin-bottom:22px">
      <tr>
        <td style="font-size:18px;font-weight:700;letter-spacing:5px">YARDEN</td>
        <td style="text-align:right" class="muted">{escape(right)}</td>
      </tr>
    </table>
    """


def section(title: str, content: str, note: str = "", padded: bool = True) -> str:
    style = "" if padded else ' style="padding:0"'
    note_html = f'<p class="note">{escape(note)}</p>' if note else ""
    return f"<h2>{escape(title)}</h2>{note_html}<section class=\"card\"{style}>{content}</section>"


def kpis(report: dict, overall: dict) -> str:
    items = [
        ("Overall Score", report.get("overall_score"), "/100", "#16a34a"),
        ("Average", overall.get("avg"), "", "#16a34a"),
        ("Max", overall.get("max"), "", "#2563eb"),
        ("Min", overall.get("min"), "", "#dc2626"),
        ("Trend", overall.get("trend"), "", "#111827"),
    ]
    cells = "".join(stat(label, value, color, suffix) for label, value, suffix, color in items)
    return f'<table class="wide"><tr>{cells}</tr></table>'


def stat(label: str, value: object, color: str, suffix: str = "") -> str:
    return f"""
    <td style="padding-right:16px;border-right:1px solid #e2e8f0">
      <span class="label">{escape(label)}</span>
      <span class="value" style="color:{color}">{value_text(value)} <small style="font-size:12px;color:#111827">{escape(suffix)}</small></span>
    </td>
    """


def metrics_summary(metrics: dict, series: dict) -> str:
    return f"""
    <table class="wide"><tr>
      <td style="width:78%;padding:0">
        <table class="wide metrics">
          <thead><tr><th>Metric</th><th>Average</th><th>Max</th><th>Min</th><th>Trend</th></tr></thead>
          <tbody>{metric_rows(metrics, series)}</tbody>
        </table>
      </td>
      <td style="width:22%;padding:12px">
        <div class="insight"><h2 style="color:#059669">Key Insight</h2><p style="line-height:1.55">{insight(metrics, series)}</p></div>
      </td>
    </tr></table>
    """


def metric_rows(metrics: dict, series: dict) -> str:
    if not metrics:
        return '<tr><td colspan="5" style="text-align:center;color:#64748b">N/A</td></tr>'

    rows = []
    for name in METRICS:
        if name not in metrics:
            continue
        values = metrics[name] or {}
        avg = values.get("avg")
        trend = trend_for(series.get(name) or [])
        rows.append(
            f"""
            <tr>
              <td style="font-weight:700">{dot(name)}{label(name)}</td>
              <td>{value_text(avg)} {bar(avg, COLORS[name])}</td>
              <td>{value_text(values.get("max"))}</td>
              <td>{value_text(values.get("min"))}</td>
              <td style="font-weight:700;color:{trend_color(trend)}">{trend_label(trend)}</td>
            </tr>
            """
        )
    return "".join(rows)


def email_metric_rows(metrics: dict) -> str:
    if not metrics:
        return '<tr><td style="padding:10px 0;color:#64748b">No metrics available</td></tr>'

    return "".join(
        f"""
        <tr>
          <td style="padding:9px 0;border-top:1px solid #e2e8f0;font-weight:700">{label(name)}</td>
          <td style="padding:9px 0;border-top:1px solid #e2e8f0;text-align:right;color:#475569">
            Avg {value_text(values.get("avg"))} / Max {value_text(values.get("max"))} / Min {value_text(values.get("min"))}
          </td>
        </tr>
        """
        for name, values in metrics.items()
    )


def detailed_charts(metrics: dict, series: dict, times: list) -> str:
    rows = []
    for name in METRICS:
        if name not in metrics:
            continue
        values = metrics[name] or {}
        rows.append(
            f"""
            <table class="chart-row"><tr>
              <td style="width:84%;padding-right:10px">
                <div style="font-weight:700;color:{COLORS[name]};margin-bottom:2px">{dot(name)}{label(name)}</div>
                {chart({label(name): series.get(name) or []}, times, 92, width=560)}
              </td>
              <td style="width:16%"><div class="stat-card">
                {stat_line("Average", values.get("avg"))}
                {stat_line("Max", values.get("max"))}
                {stat_line("Min", values.get("min"))}
              </div></td>
            </tr></table>
            """
        )
    return "".join(rows) or empty_chart(680, 160)


def chart(data: dict[str, list], times: list, height: int, width: int = 680, legend: bool = False) -> str:
    left, right, top, bottom = 32, 14, 8, 24
    paths, labels = [], []

    for index, (name, values) in enumerate(data.items()):
        points = chart_points(values, width, height, left, right, top, bottom)
        if len(points) < 2:
            continue
        color = color_for(name, index)
        path = " ".join(f"{'M' if i == 0 else 'L'} {x:.1f} {y:.1f}" for i, (x, y) in enumerate(points))
        paths.append(f'<path d="{path}" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>')
        labels.append(f"<span>{dot(name, color)}{escape(name)}</span>")

    if not paths:
        return empty_chart(width, height)

    grid = "".join(line(left, width - right, y_at(t, height, top, bottom)) for t in [0, 25, 50, 75, 100])
    y_labels = "".join(f'<text x="5" y="{y_at(t, height, top, bottom) + 3:.1f}" font-size="8" fill="#64748b">{t}</text>' for t in [0, 25, 50, 75, 100])
    x_labels = time_labels(times, width, height, left, right)
    legend_html = f'<div class="legend">{"".join(labels)}</div>' if legend else ""
    return f'{legend_html}<svg width="100%" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">{grid}{y_labels}{x_labels}{"".join(paths)}</svg>'


def chart_points(values: list, width: int, height: int, left: int, right: int, top: int, bottom: int) -> list[tuple[float, float]]:
    count = max(1, len(values) - 1)
    points = []
    for index, value in enumerate(values):
        if not isinstance(value, (int, float)):
            continue
        x = left + index * (width - left - right) / count
        y = height - bottom - max(0, min(100, value)) / 100 * (height - top - bottom)
        points.append((x, y))
    return points


def all_series(series: dict) -> dict[str, list]:
    return {label(name): series[name] for name in [*METRICS, "overall"] if series.get(name)}


def insight(metrics: dict, series: dict) -> str:
    scored = [(name, values.get("avg")) for name, values in metrics.items() if isinstance(values.get("avg"), (int, float))]
    if not scored:
        return "Not enough metric data is available for a reliable insight."

    best = max(scored, key=lambda item: item[1])
    low = min(scored, key=lambda item: item[1])
    declining = [label(name) for name, _ in scored if trend_for(series.get(name) or []) == "down"]
    if declining:
        return f"{label(best[0])} is strongest at {value_text(best[1])}. Watch {', '.join(declining[:2])}, which declined toward the end."
    return f"{label(best[0])} is strongest at {value_text(best[1])}. {label(low[0])} has the most room to improve at {value_text(low[1])}."


def trend_for(values: list) -> str:
    nums = [value for value in values if isinstance(value, (int, float))]
    if len(nums) < 2:
        return "stable"
    if nums[-1] - nums[0] > 2:
        return "up"
    if nums[-1] - nums[0] < -2:
        return "down"
    return "stable"


def value_text(value: object) -> str:
    if value is None or value == "":
        return "N/A"
    if isinstance(value, (int, float)):
        return str(round(value))
    return escape(str(value))


def label(name: str) -> str:
    return escape(LABELS.get(name, name.capitalize()))


def color_for(name: str, index: int) -> str:
    key = name.lower().replace(" score", "")
    return COLORS.get(key, list(COLORS.values())[index % len(COLORS)])


def dot(name: str, color: str | None = None) -> str:
    return f'<span class="dot" style="background:{color or COLORS.get(name, "#2563eb")}"></span>'


def bar(value: object, color: str) -> str:
    if not isinstance(value, (int, float)):
        return ""
    return f'<span style="display:inline-block;width:88px;height:5px;background:#e2e8f0;border-radius:99px;margin-left:8px"><span style="display:block;width:{max(0, min(100, round(value)))}%;height:5px;background:{color};border-radius:99px"></span></span>'


def stat_line(name: str, value: object) -> str:
    return f'<p class="stat-line"><span class="stat-label">{escape(name)}</span>{value_text(value)}</p>'


def paragraph(value: object) -> str:
    return f'<p style="line-height:1.6;margin:0">{value_text(value)}</p>'


def trend_label(value: str) -> str:
    return {"up": "Improving", "down": "Declining"}.get(value, "Stable")


def trend_color(value: str) -> str:
    return {"up": "#10b981", "down": "#ef4444"}.get(value, "#64748b")


def y_at(tick: int, height: int, top: int, bottom: int) -> float:
    return height - bottom - tick / 100 * (height - top - bottom)


def line(x1: int, x2: int, y: float) -> str:
    return f'<line x1="{x1}" x2="{x2}" y1="{y:.1f}" y2="{y:.1f}" stroke="#e2e8f0" stroke-width="1"/>'


def time_labels(times: list, width: int, height: int, left: int, right: int) -> str:
    nums = [value for value in times if isinstance(value, (int, float))]
    if len(nums) < 2:
        return ""
    indexes = sorted({0, len(nums) // 3, len(nums) * 2 // 3, len(nums) - 1})
    count = max(1, len(nums) - 1)
    return "".join(
        f'<text x="{left + index * (width - left - right) / count:.1f}" y="{height - 5}" font-size="8" text-anchor="middle" fill="#64748b">{time_text(nums[index])}</text>'
        for index in indexes
    )


def time_text(seconds: float) -> str:
    total = max(0, int(round(seconds)))
    return f"{total // 60:02d}:{total % 60:02d}"


def empty_chart(width: int, height: int) -> str:
    return f'<svg width="100%" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg"><rect width="{width}" height="{height}" fill="#f8fafc"/><text x="{width / 2}" y="{height / 2}" text-anchor="middle" fill="#64748b">N/A</text></svg>'
