#MCQGenerator.py
import os
import json
import traceback
import pandas as pd
import langchain
from dotenv import load_dotenv
from src.mcqgenerator.utils import read_file,get_table_data

#importing necesary packages
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains import SequentialChain

#loading environment variables from the .env file
load_dotenv()

KEY=os.getenv("GOOGLE_API_KEY")

llm=ChatGoogleGenerativeAI(google_api_key=KEY,model="gemini-2.5-flash",temperature=0.5, max_output_tokens=1500)



TEMPLATE="""
Text:{text}
You are an expert MCQ maker. Given the above text, it is your job to \
create a quiz of {number} multiple choice questions for {subject} students in {tone} tone.
Make sure the questions are not repeated and check all the questions to be conforming the text as well.
Make sure to format your response like RESPONSE_JSON below and use it as a guide.\
Ensure to make {number} MCQs
### RESPONSE_JSON
{response_json}

"""

quiz_generation_prompt = PromptTemplate(
    input_variables=["text","number","subject","tone","response_json"],
    template=TEMPLATE
)

quiz_chain=LLMChain(llm=llm, prompt=quiz_generation_prompt, output_key="quiz",verbose=True)

TEMPLATE2="""
You are an expert english grammarian and writer. Given a Multiple Choice Quiz for {subject} students.\
You need to evaluate the complexity of the question and give a complete analysis of the quiz. Only use at max 50 words for complexity
and if the quiz is not at per with the cognitive and analytical abilities of the students,\
update the quiz questions which needs to be changed and change the tone such that it perfectly fits
the students ability.
Quiz_MCQs:
{quiz}

Check from an expert English Writer of the above quiz:
"""


quiz_evaluation_prompt=PromptTemplate(input_variables=["subject","quiz"], template=TEMPLATE)



review_chain=LLMChain(llm=llm, prompt=quiz_evaluation_prompt, output_key="review", verbose=True)



generate_evaluate_chains=SequentialChain(chains=[quiz_chain, review_chain], input_variables=["text","number","subject","tone","response_json"],
                                         output_variables=["quiz","review"], verbose=True,)

