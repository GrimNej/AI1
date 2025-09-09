import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain
from src.mcqgenerator.utils import RESPONSE_JSON

# Load API key
load_dotenv()
KEY = os.getenv("GOOGLE_API_KEY")

llm = ChatGoogleGenerativeAI(
    google_api_key=KEY,
    model="gemini-2.5-flash",
    temperature=0.7,
    max_output_tokens=2500
)

# -------------------- Background text --------------------
BACKGROUND_TEMPLATE = """
Write about {subject} in about 500 words. 
Do not mention that this text will be used later. 
Just write a clear, informative piece.
"""

background_prompt = PromptTemplate(
    input_variables=["subject"],
    template=BACKGROUND_TEMPLATE
)

background_chain = LLMChain(
    llm=llm,
    prompt=background_prompt,
    output_key="text"
)

# -------------------- MCQ Generation --------------------
MCQ_TEMPLATE = """
Text: {text}

You are an expert MCQ maker. Create {number} multiple choice questions 
for {subject} students in {tone} tone. 
Each question and its options should be short (1–2 lines). 
Do not use phrases like "According to the text". 
Only make standalone questions.

Return ONLY valid JSON exactly like this format:
{response_json}

Important:
- Use double quotes for all keys and values.
- Include "correct_option" as the key for the correct answer.
- No single quotes.
- No trailing commas.
- Escape quotes inside questions/options.
- Keep each question concise to avoid truncation.
"""

quiz_prompt = PromptTemplate(
    input_variables=["text", "number", "subject", "tone", "response_json"],
    template=MCQ_TEMPLATE
)

quiz_chain = LLMChain(
    llm=llm,
    prompt=quiz_prompt,
    output_key="quiz"
)

# -------------------- Combine Both Steps --------------------
generate_mcq_chain = SequentialChain(
    chains=[background_chain, quiz_chain],
    input_variables=["subject", "number", "tone", "response_json"],
    output_variables=["text", "quiz"],
    verbose=False
)
