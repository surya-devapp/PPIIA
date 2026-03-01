import streamlit as st
import os
from src.ingestion import extract_text_from_pdf, extract_text_from_url, search_bill_url
from src.preprocessing import clean_text
from src.analysis import analyze_bill
from src.visualizer import create_timeline
import pandas as pd

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Public Policy Insight & Impact Analyzer", layout="wide")

def display_analysis_results(analysis_result):
    # 1. Summary Section
    st.markdown("---")
    
    updated_date = analysis_result.get("updated_date", "Unknown")
    if updated_date and updated_date != "Unknown":
        st.info(f"📅 **Document Updated:** {updated_date}")
        
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏛️ Formal Summary")
        st.info(analysis_result.get("summary", "N/A"))
        
    with col2:
        st.subheader("🗣️ Citizen-Friendly Explanation")
        st.success(analysis_result.get("simple_summary", "N/A"))
    
    # 2. Detailed Tabs
    st.markdown("### Deep Dive")
    tab1, tab2, tab3, tab4 = st.tabs(["Impact Analysis", "Sector Breakdown", "Timeline", "Risks & Benefits"])
    
    with tab1:
        st.markdown("#### Impact Over Time")
        impact = analysis_result.get("impact", {})
        st.write(f"**Short Term:** {impact.get('short_term', '-')}")
        st.write(f"**Medium Term:** {impact.get('medium_term', '-')}")
        st.write(f"**Long Term:** {impact.get('long_term', '-')}")
        
    with tab2:
        st.markdown("#### Affected Sectors")
        sectors = analysis_result.get("sectors", {})
        if isinstance(sectors, dict) and sectors:
            for sector, impact_desc in sectors.items():
                st.markdown(f"**{sector}**")
                st.info(impact_desc)
        else:
            st.write("No specific sector impact identified.")
        
    with tab3:
        st.markdown("#### Legislative History")
        timeline_events = analysis_result.get("timeline", [])
        if timeline_events:
            fig = create_timeline(timeline_events)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("No timeline data available.")
            
    with tab4:
        col_risk, col_benefit = st.columns(2)
        
        with col_risk:
            st.markdown("#### Potential Risks")
            risks = analysis_result.get("risks", [])
            for risk in risks:
                if isinstance(risk, dict):
                    level = risk.get("level", "normal").lower()
                    desc = risk.get("description", "")
                    if level == "large":
                        st.error(f"🔴 **High Risk**: {desc}")
                    elif level == "normal":
                        st.warning(f"🟡 **Medium Risk**: {desc}")
                    else:
                        st.success(f"🟢 **Low Risk**: {desc}")
                else:
                    st.warning(f"⚠️ {risk}")
                    
        with col_benefit:
            st.markdown("#### Advantages & Benefits")
            benefits = analysis_result.get("benefits", [])
            if benefits:
                for benefit in benefits:
                    st.info(f"✅ {benefit}")
            else:
                st.write("No specific benefits identified.")

def main():
    st.title("📜 Public Policy Insight & Impact Analyzer (PPIIA)")
    st.markdown("### Simplifying Government Bills for Every Citizen")
    
    # Sidebar Configuration
    st.sidebar.header("Configuration")
    
    # Hide API Key and Disable Copy
    st.markdown("""
    <style>
    /* Disable text selection */
    body {
        -webkit-user-select: none; /* Safari */
        -ms-user-select: none; /* IE 10 and IE 11 */
        user-select: none; /* Standard syntax */
    }
    
    /* Hide the password visibility toggle button */
    button[aria-label="Show password"] {
        display: none !important;
    }
    
    /* Hide the input value if it's the API key */
    input[type="password"] {
        color: transparent;
        text-shadow: 0 0 0 #000; /* Mask characters with dots/discs */
    }
    </style>
    """, unsafe_allow_html=True)

    # Get default key from environment
    env_api_key = os.getenv("GOOGLE_API_KEY")
    
    # If key exists in env, we can use it as default but NOT show it in the box to keep it hidden
    # Or strict mode: if env key exists, don't even show the input unless user wants to override
    
    if env_api_key:
        use_own_key = st.sidebar.checkbox("Use my own API Key", value=False)
        if use_own_key:
            api_key = st.sidebar.text_input("Enter Google Gemini API Key", type="password")
        else:
            api_key = env_api_key
            st.sidebar.success("Using API Key from environment.")
    else:
        api_key = st.sidebar.text_input("Enter Google Gemini API Key", type="password")

    model_name = st.sidebar.selectbox("Choose Gemini Model", ["gemini-2.5-flash"])
    
    # Mode Selection
    mode = st.sidebar.radio("Mode", ["Document Analyzer", "Chat Assistant"])

    if mode == "Document Analyzer":
        st.sidebar.header("Input Source")
        input_type = st.sidebar.radio("Choose Input Type", ["Upload PDF", "Paste URL"])
        
        text_content = ""
        
        if input_type == "Upload PDF":
            uploaded_file = st.sidebar.file_uploader("Upload Bill (PDF)", type=["pdf"])
            if uploaded_file:
                with st.spinner("Extracting text..."):
                    text_content = extract_text_from_pdf(uploaded_file)
                    st.sidebar.success(f"Loaded {len(text_content)} characters.")
                    
        elif input_type == "Paste URL":
            url = st.sidebar.text_input("Enter Bill URL")
            if url:
                 with st.spinner("Fetching content..."):
                    text_content = extract_text_from_url(url)
                    st.sidebar.success(f"Loaded {len(text_content)} characters.")

        # Initialize session state for Document Analyzer chat if needed
        if "doc_messages" not in st.session_state:
            st.session_state.doc_messages = []
        if "doc_active_text" not in st.session_state:
            st.session_state.doc_active_text = None

        if st.sidebar.button("Analyze Bill"):
            if text_content:
                cleaned_text = clean_text(text_content)
                with st.spinner("Analyzing legislative content... (This uses AI)"):
                    analysis_result = analyze_bill(cleaned_text, api_key=api_key, model_name=model_name)
                    
                if "error" in analysis_result:
                    st.error(f"Analysis Failed: {analysis_result['error']}")
                else:
                    display_analysis_results(analysis_result)
                    
                    # Store for chat context
                    st.session_state.doc_active_text = cleaned_text
                    st.session_state.doc_messages = [] # Reset chat on new analysis
                    st.success("You can now ask follow-up questions about this document below!")
            else:
                st.warning("Please upload a file or enter a URL first.")

        # Chat Interface for Document Analyzer
        if st.session_state.doc_active_text:
            st.markdown("### 💬 Chat with this Document")
            
            # Display Chat History
            for message in st.session_state.doc_messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
            
            # Chat Input
            if user_query := st.chat_input("Ask a question about the analyzed bill..."):
                # Add user message
                st.session_state.doc_messages.append({"role": "user", "content": user_query})
                with st.chat_message("user"):
                    st.markdown(user_query)
                
                # Q&A Logic
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        from src.analysis import ask_bill_question
                        response = ask_bill_question(
                            st.session_state.doc_active_text, 
                            user_query, 
                            api_key=api_key,
                            model_name=model_name
                        )
                        st.markdown(response)
                
                st.session_state.doc_messages.append({"role": "assistant", "content": response})

    elif mode == "Chat Assistant":
        st.markdown("#### 💬 Chat with Laws")
        
        # Initialize session state for chat
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "active_bill_text" not in st.session_state:
            st.session_state.active_bill_text = None
        if "active_bill_title" not in st.session_state:
            st.session_state.active_bill_title = None

        # Display Chat History
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Reset Button (in sidebar or main area?)
        if st.session_state.active_bill_text:
            st.info(f"files: {st.session_state.active_bill_title}")
            if st.button("Start New Search"):
                st.session_state.active_bill_text = None
                st.session_state.active_bill_title = None
                st.session_state.messages = []
                st.rerun()

        # Chat Input
        if user_query := st.chat_input("Ask about a bill..."):
            # Add user message to history
            st.session_state.messages.append({"role": "user", "content": user_query})
            with st.chat_message("user"):
                st.markdown(user_query)

            # Decision Logic: Search vs Q&A
            if not st.session_state.active_bill_text:
                # 1. SEARCH MODE
                with st.chat_message("assistant"):
                    with st.status("Searching for bill...") as status:
                        search_result = search_bill_url(user_query)
                        
                        if search_result:
                            status.write(f"Found: {search_result['title']}")
                            status.update(label="Analyzing...", state="running")
                            
                            text_content = extract_text_from_url(search_result['url'])
                            
                            if text_content and not text_content.startswith("Error"):
                                cleaned_text = clean_text(text_content)
                                
                                # Perform Full Analysis
                                analysis_result = analyze_bill(cleaned_text, api_key=api_key, model_name=model_name)
                                
                                status.update(label="Analysis Ready!", state="complete", expanded=False)
                                
                                if "error" in analysis_result:
                                    response = f"Analysis Failed: {analysis_result['error']}"
                                    st.error(response)
                                else:
                                    # Formulate initial response
                                    summary = analysis_result.get("summary", "No summary.")
                                    simple = analysis_result.get("simple_summary", "")
                                    response = f"**I found the [{search_result['title']}]({search_result['url']}).**\n\n### Summary\n{summary}\n\n### Simplified\n{simple}\n\n*You can now ask follow-up questions about this bill!*"
                                    
                                    # Save context
                                    st.session_state.active_bill_text = cleaned_text
                                    st.session_state.active_bill_title = search_result['title']
                                    
                                    # We could also display the full interactive results, but in chat maybe just text?
                                    # Let's show text response in chat.
                                    st.markdown(response)
                            else:
                                response = f"Could not download content from {search_result['url']}"
                                status.update(label="Failed", state="error")
                                st.error(response)
                                # CRITICAL FIX: The downloaded failed, erase the previous context buffer
                                st.session_state.active_bill_text = None
                                st.session_state.active_bill_title = None
                        else:
                            response = "I couldn't find any bill matching that query. Please try different keywords."
                            status.update(label="No results", state="error")
                            st.warning(response)
                            # CRITICAL FIX: Erase the previous context buffer
                            st.session_state.active_bill_text = None
                            st.session_state.active_bill_title = None
                            
                st.session_state.messages.append({"role": "assistant", "content": response})
            
            else:
                # 2. Q&A MODE (Follow-up)
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        # Use the new ask_bill_question function
                        from src.analysis import ask_bill_question
                        response = ask_bill_question(
                            st.session_state.active_bill_text, 
                            user_query, 
                            api_key=api_key,
                            model_name=model_name
                        )
                        st.markdown(response)
                
                st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
