from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from core.config import settings

class LLMFactory:

    @staticmethod
    def get_crm_llm():
        return ChatGoogleGenerativeAI(
            model=settings.CRM_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0
        )

    @staticmethod
    def get_supervisor_llm():
        return ChatGoogleGenerativeAI(
            model=settings.SUPERVISOR_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0
        )

    @staticmethod
    def get_support_llm():
        return ChatGoogleGenerativeAI(
            model=settings.SUPPORT_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.2
        )

    @staticmethod
    def get_commerce_llm():
        return ChatGoogleGenerativeAI(
            model=settings.COMMERCE_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0
        )

    @staticmethod
    def get_research_llm():
        return ChatGoogleGenerativeAI(
            model=settings.RESEARCH_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.2
        )

    @staticmethod
    def get_sales_llm():
        return ChatGoogleGenerativeAI(
            model=settings.SALES_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.3
        )

    @staticmethod
    def get_faq_llm():
        return ChatGoogleGenerativeAI(
            model=settings.FAQ_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0
        )

    @staticmethod
    def get_summarizer_llm():
        return ChatGoogleGenerativeAI(
            model=settings.SUMMARIZER_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0
        )

    @staticmethod
    def get_response_generator_llm():
        return ChatGoogleGenerativeAI(
            model=settings.RESPONSE_GENERATOR_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.2
        )