---
title: PPIIA Project
emoji: 📜
colorFrom: blue
colorTo: indigo
sdk: streamlit
sdk_version: 1.25.0
app_file: app.py
pinned: false
---

# Public Policy Insight & Impact Analyzer (PPIIA)

**Simplifying Government Bills for Every Citizen**

The Public Policy Insight & Impact Analyzer (PPIIA) is an intelligent, AI-powered Streamlit dashboard designed to help citizens, legal professionals, and journalists seamlessly understand complex Indian legislative bills and policies. By combining web scraping, NLP extraction, and Gemini AI analysis, PPIIA transforms dense legal jargon into accessible insights.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.25+-red.svg)
![Gemini AI](https://img.shields.io/badge/Gemini%20AI-Powered-orange.svg)

---

## � Live Demo

The application is officially deployed and hosted live on Hugging Face Spaces. You can access and test the live application here:

👉 **[PPIIA - Hugging Face Space](https://huggingface.co/spaces/suryarajesh/PPIIA)**

*(Note: To use the live demo, you will need to generate and paste your own **Google Gemini API Key** into the sidebar of the application. The container build logs can be viewed [here](https://huggingface.co/spaces/suryarajesh/PPIIA?logs=container)).*

---

## �🌟 Key Features

### 1. Advanced Data Ingestion & Search
- **Official Domain Priority:** Natively searches for and prioritizes government PDFs from domains like `sansad.in`, `india.gov.in`, `prsindia.org`, and `nic.in`.
- **Intelligent Fallback:** Gracefully falls back to secondary PDFs or Wikipedia summaries if primary official links are unavailable.
- **Robust WAF Bypass:** Handles specific web application firewall quirks (handling `+` encoding issues to resolve `HTTP 500` server errors).

### 2. Comprehensive AI LLM Analysis
- **Formal & Citizen-Friendly Summaries:** Provides both an executive formal summary and an ELI5 (Explain Like I'm 5) analogy-based simple summary.
- **Impact Analysis Matrix:** Breaks down the bill's predicted impacts into **Short-Term**, **Medium-Term**, and **Long-Term** consequences.
- **Sector Breakdown:** Identifies and analyzes the specific industries (Technology, Agriculture, Healthcare, Legal) affected by the legislation.
- **Dynamic Chronology Generation:** Automatically extracts key dates from the text and plots a dynamic timeline using Plotly.
- **Categorized Risk Diagnostics:** Scans the text for controversies and potential risks, color-coding them by severity:
  - 🔴 **High Risk / Large**
  - 🟡 **Medium Risk / Normal**
  - 🟢 **Low Risk / Small**
- **Advantages & Benefits:** Extracts and highlights the positive outcomes of the bill.
- **Updated Status:** Extracts the most recent relevant date/status for the introduced bill or amendment.

### 3. Interactive Web UI & Chat
- **Streamlit Dashboard:** A clean, multi-tabbed user interface built for easy navigation.
- **Chat with Laws:** An interactive AI memory buffer allows you to ask targeted, follow-up context-aware questions directly against the loaded legislation document. Seamlessly resets on new queries to prevent memory hallucinations.

---

## 🛠️ Technology Stack

- **Frontend:** Streamlit, Plotly (for Timeline visualization).
- **Backend/Scripts:** Python.
- **AI Engine:** Google Gemini (`gemini-1.5-flash` / `gemini-2.5-flash`).
- **Scraping & Parsing:** DuckDuckGo Search API (`ddgs`), PyPDF2, BeautifulSoup4, Requests.

---

## 🚀 Setup & Installation (Local Development)

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd PPIIA_Project
   ```

2. **Create a Virtual Environment (Optional but Recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Create a `.env` file in the root directory and add your Google Gemini API Key:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```
   *(Note: You can also choose to paste the key directly into the Streamlit sidebar during runtime instead of using a `.env` file).*

5. **Run the Application:**
   ```bash
   streamlit run app.py
   ```
   Open `http://localhost:8501` in your browser.

---

## ☁️ Deployment Guide (Hugging Face Spaces)

The application is designed to be easily hosted on Hugging Face Spaces.

1. Create a new Space on [Hugging Face](https://huggingface.co/spaces) and choose **Streamlit** as the space SDK.
2. Upload the project files (`app.py`, `src/`, `requirements.txt`, `README.md`).
3. Navigate to the **Settings** tab of your HF Space.
4. Scroll down to **Variables and secrets** and click **New secret**.
5. Add your API Key:
   - **Name:** `GOOGLE_API_KEY`
   - **Value:** `your-gemini-api-key-here`
6. The Streamlit app will automatically build and deploy!

---

## 🧩 Usage Guide

1. Enter your **Google API Key** in the sidebar.
2. Choose your **Analysis Mode**:
   - **Upload PDF:** Manually upload a local bill document.
   - **Paste URL:** Provide a direct URL (Webpage or PDF).
   - **Search Web/Chat:** Type the name of the bill (e.g., *"the hindu marriage (amendment) bill, 2025"*) and let the DuckDuckGo agent automatically find, download, verify, and parse the official document.
3. Click **Analyze Bill**.
4. Review the generated insights across the distinct tabs.
5. Ask follow-up questions securely in the "Chat with Laws" section!
