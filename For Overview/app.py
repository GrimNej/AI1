import json
import re
import ast
from flask import Flask, request, render_template, redirect, url_for, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from src.mcqgenerator.MCQGenerator import generate_mcq_chain
from src.mcqgenerator.utils import RESPONSE_JSON

app = Flask(__name__)
app.secret_key = "supersecretkey"

# -------------------- MySQL --------------------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="mcq_game"
)
cursor = db.cursor(dictionary=True)

# -------------------- Helpers --------------------
def clean_quiz_json(raw_text):
    """Parse LLM output safely and normalize keys to strings and correct letters to lowercase."""
    if not raw_text:
        return None
    cleaned = re.sub(r"^```json\s*|\s*```$", "", raw_text.strip())
    try:
        data = json.loads(cleaned)
    except Exception:
        try:
            data = ast.literal_eval(cleaned)
        except Exception:
            return None

    normalized = {}
    for k, v in data.items():
        normalized[str(k)] = {
            "mcq": v.get("mcq", ""),
            "options": v.get("options", {}),
            "correct": str(v.get("correct", "")).strip().lower()
        }
    return normalized

# -------------------- Authentication --------------------
@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("home"))
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        pw_hash = generate_password_hash(password)
        try:
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                (username, email, pw_hash)
            )
            db.commit()
            return redirect(url_for("index"))
        except mysql.connector.IntegrityError:
            return "Username or Email already exists", 400
    return render_template("signup.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    user = cursor.fetchone()
    if user and check_password_hash(user["password_hash"], password):
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        return redirect(url_for("home"))
    return "Invalid credentials", 401

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# -------------------- Home --------------------
@app.route("/home")
def home():
    if "user_id" not in session:
        return redirect(url_for("index"))
    return render_template("home.html", username=session["username"])

@app.route("/start_game", methods=["POST"])
def start_game():
    if "user_id" not in session:
        return redirect(url_for("index"))
    subject = request.form["subject"].strip()
    if not subject:
        return redirect(url_for("home"))
    session["subject"] = subject
    session["current_round"] = 1
    session["score"] = 0
    return redirect(url_for("play_round"))

# -------------------- Game Rounds --------------------
@app.route("/play_round", methods=["GET", "POST"])
def play_round():
    if "user_id" not in session:
        return redirect(url_for("index"))

    current_round = session.get("current_round", 1)
    subject = session.get("subject")
    difficulties = {1: "Simple", 2: "Intermediate", 3: "Hard"}
    difficulty = difficulties.get(current_round, "Simple")

    # POST: process answers
    if request.method == "POST":
        answers = request.form
        round_questions = session.get(f"quiz_round_{current_round}", {})

        correct_count = 0
        for q_id_str, selected_opt in answers.items():
            q_id = str(q_id_str)
            if q_id in round_questions:
                correct_answer = round_questions[q_id]["correct"]
                if str(selected_opt).strip().lower() == correct_answer:
                    correct_count += 1

        session["score"] = correct_count

        if correct_count >= 5:
            if current_round == 3:
                return redirect(url_for("game_won"))
            else:
                session["current_round"] += 1
                return redirect(url_for("play_round"))
        else:
            return redirect(url_for("game_over"))

    # GET: generate quiz
    response = generate_mcq_chain.invoke({
        "subject": subject,
        "number": 10,
        "tone": difficulty,
        "response_json": json.dumps(RESPONSE_JSON)
    })
    raw_quiz = response.get("quiz", "")
    quiz = clean_quiz_json(raw_quiz)

    if not quiz:
        return render_template("game_over.html", message="Failed to generate quiz. Please try again.")

    session[f"quiz_round_{current_round}"] = quiz
    return render_template("round.html", round=current_round, difficulty=difficulty, quiz=quiz)

# -------------------- End Pages --------------------
@app.route("/game_over")
def game_over():
    return render_template("game_over.html")

@app.route("/game_won")
def game_won():
    return render_template("game_won.html")

# -------------------- Run --------------------
if __name__ == "__main__":
    app.run(debug=True)
