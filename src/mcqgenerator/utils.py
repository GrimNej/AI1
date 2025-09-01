import os
import PyPDF2
import json
import traceback

def read_file(file):
    if file.name.endswith(".pdf"):
        try:
            pdf_reader=PyPDF2.PdfFileReader(file)
            text=""
            for page in pdf_reader.pages:
                text+=page.extract_text()
            return text
        except Exception as e:
            raise Exception("error reading the PDF file")
        
    elif file.name.endswith(".txt"):
        return file.read().decode("utf-8")
    
    else:
        raise Exception(
            "unsupported file format only pdf and text file supported"
        )
    


# def get_table_data(quiz_str):
#     try:
#         #convert the quiz from a str to dict
#         quiz_dict=json.loads(quiz_str)
#         quiz_table_data=[]

#         for key,value in quiz_dict.items():
#             mcq=value["mcq"]
#             options="||".join(
#                 [
#                     f"{option}->{option_value}" for option, option_value in value["options"].items()

#                 ]
#             )

#             correct = value["correct"]
#             quiz_table_data.append({"MCQ":mcq,"Choices": options,"Correct": correct})

#         return quiz_table_data

#     except Exception as e:
#         traceback.print_exception(type(e), e, e.__traceback__)
#         return False
def get_table_data(quiz_input):
    try:
        # Handle string input
        if isinstance(quiz_input, str):
            quiz_dict = json.loads(quiz_input)
        elif isinstance(quiz_input, dict):
            quiz_dict = quiz_input
        else:
            raise ValueError("quiz_input must be a str or dict")

        quiz_table_data = []

        for key, value in quiz_dict.items():
            mcq = value.get("mcq", "")
            options = " || ".join(
                [f"{opt}->{val}" for opt, val in value.get("options", {}).items()]
            )
            correct = value.get("correct", "")

            quiz_table_data.append(
                {"MCQ": mcq, "Choices": options, "Correct": correct}
            )

        return quiz_table_data

    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__)
        return None
