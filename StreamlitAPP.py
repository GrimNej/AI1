import os
import json
import traceback
import ast

# remove code fences
import re
import pandas as pd
import langchain
from dotenv import load_dotenv
import streamlit as st
from src.mcqgenerator.utils import read_file,get_table_data
from src.mcqgenerator.MCQGenerator import generate_evaluate_chains
# from src.mcqgenerator.logger import logging


#loading json file
with open('E:\AI\Response.json','r') as file:
    RESPONSE_JSON = json.load(file)

#creating a title for the app
st.title("MCQs Creator")

#Create a form using st.form
with st.form("user_inputs"):
    #File uploaded
    uploaded_file=st.file_uploader("Upload a PDF or text file")

    #Input Fields
    mcq_count=st.number_input("No. of MCQs", min_value=3, max_value=10)

    #Subject
    subject=st.text_input("Insert Subject", max_chars=20)

    #Quiz Tone
    tone=st.text_input("Complexity level of Questions", max_chars=20, placeholder="Simple")

    #Add Button
    button=st.form_submit_button("Create MCQs")

    #Check if the button is clicked and all fields have input

    if button and uploaded_file is not None and mcq_count and subject and tone:
        with st.spinner("loading..."):
            try:
                text=read_file(uploaded_file)
                response=generate_evaluate_chains(
                    {
                        "text": text,
                        "number": mcq_count,
                        "subject": subject,
                        "tone": tone,
                        "response_json": json.dumps(RESPONSE_JSON)
                    }
                )
                # st.write(response)
            except Exception as e:
                traceback.print_exception(type(e),e,e.__traceback__)
                st.error("Error")

            else:
                if isinstance(response, dict):
                    #Extract quiz from the response
                    quiz=response.get("quiz",None)


                    cleaned = re.sub(r"^```json\n", "", quiz)
                    cleaned = re.sub(r"\n```$", "", cleaned)

                    data = ast.literal_eval(cleaned)   # handles single quotes, dict-style
                    quiz=data

                    if quiz is not None:
                        table_data=get_table_data(quiz)
                        if table_data is not None:
                            df=pd.DataFrame(table_data)
                            df.index=df.index+1
                            st.table(df)
                            #Display the review in a text box as well
                            st.text_area(label="Review", value=response["review"])
                        else:
                            st.error("Error in the table data")
                    else:
                        st.write(response)