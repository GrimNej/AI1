import json
import traceback

# Desired format for the LLM output
RESPONSE_JSON = {
    str(i): {
        "mcq": "multiple choice question",
        "options": {
            "a": "choice here",
            "b": "choice here",
            "c": "choice here",
            "d": "choice here"
        },
        "correct_option": "a"  # always include correct_option key
    } for i in range(1, 11)
}

# Turn model output into table format (optional for admin/debug)
def get_table_data(quiz_input):
    try:
        if isinstance(quiz_input, str):
            quiz_dict = json.loads(quiz_input)
        elif isinstance(quiz_input, dict):
            quiz_dict = quiz_input
        else:
            raise ValueError("quiz_input must be str or dict")

        quiz_table_data = []
        for key, value in quiz_dict.items():
            mcq = value.get("mcq", "")
            options = " || ".join([f"{opt}->{val}" for opt, val in value.get("options", {}).items()])
            correct = value.get("correct_option", "")
            quiz_table_data.append(
                {"MCQ": mcq, "Choices": options, "Correct": correct}
            )
        return quiz_table_data
    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__)
        return None
