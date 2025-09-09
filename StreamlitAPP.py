# # StreamlitAPP.py
# import json
# import re
# import ast
# import streamlit as st
# import pandas as pd
# from src.mcqgenerator.MCQGenerator import generate_mcq_chain
# from src.mcqgenerator.utils import RESPONSE_JSON, get_table_data

# st.title("MCQ Generator App")

# # Input for topic/subject
# subject = st.text_input("Enter a topic/subject")

# # Input for number of MCQs (min 3, max 10)
# mcq_count = st.number_input("Number of MCQs", min_value=3, max_value=10, value=5, step=1)

# # Button to generate MCQs
# if st.button("Generate MCQs") and subject:
#     with st.spinner("Generating MCQs..."):
#         # Call the MCQ generation chain (always simple tone)
#         response = generate_mcq_chain.invoke({
#             "subject": subject,
#             "number": mcq_count,
#             "tone": "Intermidiate",
#             "response_json": json.dumps(RESPONSE_JSON)
#         })
        
#         quiz_json = response.get("quiz")

#         if not quiz_json or quiz_json.strip() == "":
#             st.error("No quiz generated. Please wait 30 seconds and try again.")
#             quiz = None
#         else:
#             # Remove code fences and clean string
#             quiz_json = re.sub(r"^```json\s*", "", quiz_json.strip())
#             quiz_json = re.sub(r"```$", "", quiz_json.strip())
#             quiz_json = ' '.join(quiz_json.split())

#             # Attempt parsing JSON first, fallback to ast.literal_eval
#             try:
#                 quiz = json.loads(quiz_json)
#             except Exception:
#                 try:
#                     quiz = ast.literal_eval(quiz_json)
#                 except Exception as e:
#                     st.error(f"Error while parsing quiz: {e}")
#                     quiz = None

#         # Display MCQs as a table
#         if quiz:
#             table_data = get_table_data(quiz)
#             if table_data:
#                 df = pd.DataFrame(table_data)
#                 df.index = df.index + 1
#                 st.table(df)
