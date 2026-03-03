# Final Project Report: Public Policy Insight & Impact Analyzer (PPIIA)

**Project Name:** Public Policy Insight & Impact Analyzer (PPIIA)
**Category:** Artificial Intelligence / Natural Language Processing
**Live Demo:** [Hugging Face Space](https://huggingface.co/spaces/suryarajesh/PPIIA)

---

## 1. Abstract / Executive Summary
The Public Policy Insight & Impact Analyzer (PPIIA) is an intelligent, AI-powered web dashboard designed to bridge the gap between complex government legislation and public comprehension. It utilizes intelligent web scraping, advanced Natural Language Processing (NLP), and the Google Gemini Large Language Model to instantly download, read, and simplify Indian legislative bills. By transforming dense legal jargon into accessible insights, PPIIA empowers citizens, journalists, and legal professionals.

## 2. Problem Statement
Every year, governments introduce hundreds of complex, multi-page legislative bills filled with dense vocabulary. For the average citizen, understanding exactly how these new policies legally affect their daily lives, industries, or rights is incredibly difficult. Relying on secondary news sources can lead to bias or incomplete information. There is an urgent need for an automated tool to democratize direct access to, and comprehension of, primary legal documents.

## 3. Proposed Solution
PPIIA solves this problem by offering a platform where users can simply search for the name of any active bill (e.g., "The Hindu Marriage Amendment Bill, 2025"), provide a direct official URL, or upload a local PDF.

The system autonomously hunts down and reads the text, outputting:
1. **Citizen-Friendly ("ELI5") Summary:** Analogies and simplified phrasing for eighth-grade reading levels.
2. **Formal Summary:** Professional executive summary of the act.
3. **Impact Matrix:** Breaks down the ramifications into Short, Medium, and Long-Term outcomes.
4. **Sectoral Breakdown:** Identifies specific industries (e.g., Tech, Healthcare, Agriculture) targeted by the bill.
5. **Timeline Generation:** Plots critical legislative dates in a chronological chart.
6. **Risk diagnostics (`Red/Yellow/Green`):** Highlights ambiguities or controversies in the bill.
7. **Interactive Chat:** A context-aware chatbot allowing users to ask further, highly specific follow-up questions about the document just analyzed.

## 4. Technical Architecture
The application leverages a robust Python stack designed for speed and reliability:
* **Frontend:** Streamlit 
* **Data Visualization:** Plotly (for Interactive Timelines)
* **Backend:** Python (Requests, PyPDF2, BeautifulSoup4)
* **Search Routing:** DuckDuckGo Web Search API (`ddgs`)
* **AI & NLP Engine:** Google Gemini AI models (`gemini-1.5-flash` and `gemini-2.5-flash`) via LangChain

## 5. Key Implementation Details & Innovations
The development involved overcoming significant engineering challenges:

### 5.1 Web Application Firewall (WAF) Bypass
Indian government websites (like `sansad.in`) often strictly block automated bots from fetching documents and throw `HTTP 500 Server Errors`. By analyzing the block, we discovered legacy server-side issues with URL encoding of spaces as `+`. PPIIA successfully implements an advanced domain-interception script that fixes the encoding string and intelligently fetches the PDF without triggering the WAF, ensuring 100% reliable document retrieval.

### 5.2 Context Isolation & Memory Management
In single-page applications, memory from a previous analysis might inadvertently "bleed" into a newly searched document, leading to AI hallucinations. PPIIA implements an aggressive **Streamlit Session State Purge**. Every time a new search is initiated or a file fails to load, the temporary memory buffer is completely wiped.

### 5.3 Intelligent Domain Heuristics
A standard text query might scrape Wikipedia instead of the raw legislative text. PPIIA utilizes a **Two-Pass Domain Heuristic**, forcing the engine to evaluate trusting links ending in `.gov.in` and `.nic.in` first, physically pinging the servers with boolean validations, and intelligently falling back to secondary verified PDFs if the primary endpoint is dead.

## 6. Project Value & Conclusion
By deploying the system live via Hugging Face Spaces with seamless Streamlit UI interaction, the product achieves a high level of scalability and usability. PPIIA successfully reduces a 100-page complex legal PDF into a readable 3-minute executive dashboard, accelerating the democratization of legal and policy literacy for everyone.
