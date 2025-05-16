import sys
import pandas as pd
import matplotlib.pyplot as plt
import requests
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
import textwrap

# Handle command-line arguments: csv_path, store_name, start_date, end_date
if len(sys.argv) < 5:
    print("Usage: report_generator.py <csv_path> <store_name> <start_date> <end_date>", file=sys.stderr)
    sys.exit(1)

CSV_PATH   = sys.argv[1]
STORE_NAME = sys.argv[2]
START_DATE = sys.argv[3]
END_DATE   = sys.argv[4]
API_KEY    = ""  # Insert your API key here

# Load CSV data (headers must match these column names)
df = pd.read_csv(CSV_PATH, parse_dates=["collectedAt"])

# Analyze and summarize collection records for a given store and date range
def analyze_store_range_summary(store_name, start_date, end_date, df):
    start    = pd.to_datetime(start_date)
    end      = pd.to_datetime(end_date)
    store_df = df[df["storeName"] == store_name]
    filtered = store_df[(store_df["collectedAt"] >= start) & (store_df["collectedAt"] <= end)]
    if filtered.empty:
        return None, None

    # Calculate average days between collections
    interval = filtered["collectedAt"].diff().dt.days.mean()
    summary = {
        "store_name":   store_name,
        "start":        start_date,
        "end":          end_date,
        "total_count":  len(filtered),
        "avg_volume":   round(filtered["volumeLiter"].mean(), 1),
        "avg_interval": round(interval, 1) if not pd.isna(interval) else 0,
        "total_price":  int(filtered["totalPrice"].sum())
    }
    return summary, filtered

# Generate executive summary prompt for AI model
def generate_prompt(summary):
    return f"""
Write a business-style executive summary for waste oil collection.

Store: {summary['store_name']}
Period: {summary['start']} ~ {summary['end']}

- Total collections: {summary['total_count']}
- Avg volume: {summary['avg_volume']} L
- Avg interval: {summary['avg_interval']} days
- Total price: {summary['total_price']} KRW

Summarize this with clear insights.
"""

# Generate prompt describing chart data for AI insights
def generate_chart_prompt(store_name, dates, values, ylabel):
    date_str  = dates.dt.strftime("%Y-%m-%d").tolist()
    value_str = values.round(2).tolist()
    return f"""
The following graph represents {ylabel} trend for {store_name}:

X-axis (date): {date_str}
Y-axis ({ylabel}): {value_str}

Write 3–5 business insights about this graph.
"""

# Call Google Gemini API with given prompt
def call_gemini(prompt, api_key):
    url     = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent"
    headers = {"Content-Type": "application/json"}
    body    = {"contents": [{"role": "user", "parts": [{"text": prompt}]}]}
    resp    = requests.post(f"{url}?key={api_key}", headers=headers, json=body)
    resp.raise_for_status()
    return resp.json()["candidates"][0]["content"]["parts"][0]["text"]

# Create a line chart buffer for the specified DataFrame column
def create_plot(df, y_column, title, ylabel):
    plt.figure(figsize=(7, 4))
    plt.plot(df["collectedAt"], df[y_column], marker="o")
    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel(ylabel)
    plt.xticks(rotation=45)
    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close()
    return buf

# Assemble the report PDF with text and charts
def create_final_pdf(report_text, chart_texts, charts, filename, summary):
    c      = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    # Header
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(colors.HexColor("#2E5C87"))
    c.drawString(2*cm, height-2.5*cm, "■ ECOGEM Waste Oil Collection Report")
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 11)
    c.drawString(2*cm, height-3.2*cm, f"Store: {summary['store_name']}")
    c.drawString(2*cm, height-3.8*cm, f"Period: {summary['start']} ~ {summary['end']}")
    # Executive Summary Section
    y = height - 5*cm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, y, "Executive Summary")
    y -= 0.6*cm
    c.setFont("Helvetica", 10)
    for line in textwrap.wrap(report_text, 100):
        c.drawString(2*cm, y, line)
        y -= 0.45*cm
    # Charts and their insights
    for buf, text, title in zip(charts, chart_texts, ["Volume Trend", "Revenue Trend"]):
        y -= cm
        c.drawImage(ImageReader(buf), 2*cm, y-5*cm, width=16*cm, height=5*cm)
        y -= 5.5*cm
        c.setFont("Helvetica-Bold", 11)
        c.drawString(2*cm, y, f"■ {title} Insights")
        y -= 0.5*cm
        c.setFont("Helvetica", 9)
        for para in text.split("\n"):
            for ln in textwrap.wrap(para, 100):
                c.drawString(2*cm, y, ln)
                y -= 0.4*cm
        c.showPage()
        y = height - 2.5*cm
    # Footer
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.grey)
    c.drawString(2*cm, 1.5*cm, "© 2025 ECOGEM")
    c.save()

# Main execution
if __name__ == "__main__":
    summary, filtered_df = analyze_store_range_summary(
        STORE_NAME, START_DATE, END_DATE, df
    )
    if summary:
        rpt   = call_gemini(generate_prompt(summary), API_KEY)
        vol   = call_gemini(
            generate_chart_prompt(
                STORE_NAME, filtered_df["collectedAt"], filtered_df["volumeLiter"], "Volume (L)"
            ),
            API_KEY
        )
        rev   = call_gemini(
            generate_chart_prompt(
                STORE_NAME, filtered_df["collectedAt"], filtered_df["totalPrice"],  "Revenue (KRW)"
            ),
            API_KEY
        )
        charts = [create_plot(filtered_df, "volumeLiter", "Volume Trend", "Volume (L)"),
                  create_plot(filtered_df, "totalPrice",  "Revenue Trend", "Revenue (KRW)")]
        filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        create_final_pdf(rpt, [vol, rev], charts, filename, summary)
        print(filename)
    else:
        print("No data found for given criteria.")
