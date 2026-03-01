import os
import json

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException

def analyze_bill(text, api_key=None, provider="gemini", model_name="gemini-1.5-flash"):
    """
    Analyzes the bill text using an LLM.
    Returns a dictionary with structured analysis.
    """
    
    # MOCK RESPONSE if no API key
    if not api_key:
        return get_mock_analysis()

    if provider == "gemini":
        try:
            # cutting text to avoid token limits if necessary
            processed_text = text[:100000] 

            # Helper to create LLM and invoke
            def run_llm(model_val):
                llm = ChatGoogleGenerativeAI(
                    model=model_val,
                    google_api_key=api_key,
                    temperature=0.3
                )
                
                parser = JsonOutputParser()
                prompt_template_str = """
                You are an expert Public Policy Analyst and Legal Simplifier. 
                Your task is to analyze the following government bill text and provide a structured report.
                
                Target Audience: Common citizens (8th-grade reading level) for the summary, and industry professionals for the impact analysis.

                Please extract the following information and format it as a valid JSON object with the exact keys below:
                
                1. "summary": A formal 2-3 sentence summary of the bill's core purpose.
                2. "simple_summary": A "Citizen-Friendly" explanation (like ELI5) using analogies if helpful.
                3. "impact": A dictionary with keys "short_term", "medium_term", "long_term" describing the consequences.
                4. "sectors": A dictionary where keys are Sector Names (e.g., "Technology", "Agriculture") and values are a short description of the impact (e.g., "High Impact - compliance costs").
                5. "timeline": A list of objects with "date" (YYYY-MM-DD if possible, or string) and "event" (description) based on dates found in the text or general legislative process inference.
                6. "risks": A list of objects detailing potential risks, controversies, or challenges. Each object MUST have "level" ("large", "normal", or "small") and "description" (the risk text).
                7. "benefits": A list of strings detailing the advantages, benefits, or positive outcomes of this bill.
                8. "updated_date": A string representing the most recent date of the bill's status, introduction, amendment, or publication as explicitly stated in the text. Return "Unknown" if not found.

                Bill Text:
                {text}
                
                Return ONLY the JSON.
                """
                
                prompt = PromptTemplate(
                    template=prompt_template_str,
                    input_variables=["text"],
                )
                
                chain = prompt | llm | parser
                return chain.invoke({"text": processed_text})

            try:
                result = run_llm(model_name)
                if not result:
                    return {"error": "AI returned an empty response."}
                if not isinstance(result, dict):
                    return {"error": "AI returned an invalid format instead of JSON."}
                return result
            except Exception as e:
                raise e

        except OutputParserException as e:
            return {"error": f"Failed to parse AI response: {str(e)}"}
        except Exception as e:
            return {"error": f"AI Analysis Error: {str(e)}"}
    
    # Fallback or other providers
    return get_mock_analysis()

def ask_bill_question(text, question, api_key, model_name="gemini-2.5-flash"):
    """
    Answers a specific user question based on the provided bill text.
    """
    if not api_key:
        return "Please provide an API Key to ask questions."

    try:
        # Truncate for context window if needed, though Gemini 1.5/2.0 has huge context
        processed_text = text[:100000]

        llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0.3
        )
        
        # Simple string output parser
        from langchain_core.output_parsers import StrOutputParser
        parser = StrOutputParser()

        prompt_template = """
        You are a helpful Public Policy Assistant.
        You have analyzed the following bill/document:
        
        ---
        {text}
        ---

        User Question: {question}

        Answer the question clearly and concisely based ONLY on the provided text.
        """

        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["text", "question"],
        )

        chain = prompt | llm | parser
        return chain.invoke({"text": processed_text, "question": question})

    except Exception as e:
        return f"Error analyzing question: {str(e)}"

def get_mock_analysis():
    """
    Returns a dummy analysis result for testing the UI.
    """
    return {
        "summary": "This bill proposes amendments to the existing Digital Data Protection Act. It aims to strengthen user privacy by mandating stricter consent protocols for data processors. Specifically, it introduces 'right to be forgotten' as a fundamental digital right and increases penalties for data breaches.",
        "simple_summary": "Think of this bill like a new set of rules for how companies handle your personal secrets. It says companies must ask you very clearly before using your info, and if they lose your secrets, they have to pay a big fine. You also get the power to tell them to delete everything they know about you.",
        "impact": {
            "short_term": "Immediate compliance costs for tech companies. Updates to privacy policies required.",
            "medium_term": "Shift in data processing architectures. Growth in legal and compliance job market.",
            "long_term": "Enhanced user trust in digital ecosystems. Potential slow-down in AI training due to data scarcity."
        },
        "sectors": {
            "Technology": "High Impact - New compliance layers.",
            "Legal": "Positive - Increased demand for advisory.",
            "Marketing": "Negative - Restricted data access for targeting.",
            "Healthcare": "Medium - Stricter patient data handling."
        },
        "timeline": [
            {"date": "2023-08-01", "event": "Bill introduced in Lok Sabha"},
            {"date": "2023-12-10", "event": "Committee Report Submitted"},
            {"date": "2024-02-15", "event": "Passed by Rajya Sabha"},
            {"date": "2024-05-01", "event": "Presidential Assent"}
        ],
        "risks": [
            {"level": "large", "description": "High implementation cost for small startups."},
            {"level": "normal", "description": "Ambiguity in 'legitimate use' exceptions."},
            {"level": "small", "description": "Potential friction with international data transfer norms."}
        ],
        "benefits": [
            "Significantly strengthens citizen data privacy rights.",
            "Establishes a clear legal framework for data fiduciaries."
        ],
        "updated_date": "August 1st, 2023"
    }
