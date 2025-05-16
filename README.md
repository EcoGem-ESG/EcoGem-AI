♻️ EcoGem Waste Oil Report Generator – Overall Workflow

A system that generates automated PDF reports based on restaurants’ waste cooking oil collection data. It integrates chart visualizations and AI-driven summaries/interpretations via the Gemini API.

## 📦 1. Load CSV Data

* Load `waste_collection_realistic_final.csv` using pandas
* Parse the `collectedAt` column as dates

## 📍 2. Gather User Inputs

* Store name (`store_name`)
* Analysis start date (`start_date`)
* Analysis end date (`end_date`)

## 📊 3. Filter Data & Compute Statistics

* In `analyze_store_range_summary()`:

  * Filter records for the selected store and date range
  * Calculate:

    * Total number of collections
    * Average volume collected
    * Average interval between collections (in days)
    * Total revenue

## 🤖 4. Generate Gemini Prompts

* **Executive Summary Prompt** for overall insights
* **Chart Interpretation Prompts** for volume and revenue trends

## 🔑 5. Call Gemini API

* `call_gemini(prompt, api_key)`
* Uses the `gemini-1.5-pro` model
* Extract main text from the response
* Deterministic outputs for identical prompts (default temperature)

## 📈 6. Create Charts

* Generate two time-series line charts (volume & revenue) with matplotlib
* Save each chart into a `BytesIO` buffer for PDF embedding

## 📄 7. Generate PDF Report (ReportLab)

* Include ECOGEM-branded title, store name, and date range
* Wrap Gemini’s text responses into readable paragraphs
* Insert charts at a generous size, followed by their AI‑driven insights
* Organize content across pages with consistent margins and spacing

✅ **Output**

* Saves as `storeName_startDate_to_endDate_report.pdf`

---

## 📂 Dummy Dataset Details

The `waste_collection_realistic_final.csv` is a synthetic dataset simulating two years of cooking oil collections. Key characteristics:

| Column Name       | Description                            |
| ----------------- | -------------------------------------- |
| Store Name        | Restaurant name                        |
| Address           | Restaurant address                     |
| Phone Number      | Contact phone                          |
| Delivery Type     | Emission category (SMALL/MEDIUM/LARGE) |
| Collected At      | Collection date                        |
| Volume (L)        | Volume collected (liters)              |
| Unit Price (KRW)  | Price per liter                        |
| Total Price (KRW) | Total collection amount                |
| Collector         | Name of collection agent               |

* **Period:** May 1, 2023 – April 30, 2025 (2 years)
* **Stores:** 20 unique names (e.g., Tony’s Pizza, Mama’s Kimbap)
* **Records:** \~1,300 entries
* **Collections per Store:** 20–112 times (varies by type/size)

### 📌 Static Attributes

* Address, phone, and emission type remain consistent per store
* Collector names use full English names (e.g., Park Ji Hye, Lee Jeong Hwa)

### 🚚 Delivery Type Guide

| Type   | Expected Weekly Output | Typical Single Pickup Range | Example Establishments     |
| ------ | ---------------------- | --------------------------- | -------------------------- |
| SMALL  | 1–5 L                  | 4–10 L                      | Cafés, snack bars          |
| MEDIUM | 6–20 L                 | 10–25 L                     | Chicken shops, restaurants |
| LARGE  | 20 L+                  | 25–50 L                     | Franchises, large kitchens |
