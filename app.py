import json
import re
import ast
from datetime import datetime
from flask import Flask, request, render_template, redirect, url_for, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from src.mcqgenerator.MCQGenerator import generate_mcq_chain
from src.mcqgenerator.utils import RESPONSE_JSON

app = Flask(__name__)
app.secret_key = "supersecretkey"

# MySQL Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="mcq_game"
)
cursor = db.cursor(dictionary=True)

def clean_quiz_json(raw_text):
    """Parse LLM output safely and normalize keys."""
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
            "correct": str(v.get("correct_option", "")).strip().lower()
        }
    return normalized

def save_game_result(user_id, subject, completed, won, final_score, rounds_completed):
    """Save game result to database."""
    try:
        cursor.execute("""
            INSERT INTO game_history 
            (user_id, subject, completed, won, final_score, rounds_completed, date_played) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (user_id, subject, completed, won, final_score, rounds_completed, datetime.now()))
        db.commit()
    except Exception as e:
        print(f"Error saving game result: {e}")

def get_user_stats(user_id):
    """Get user statistics for profile page."""
    try:
        # Total games
        cursor.execute("SELECT COUNT(*) as count FROM game_history WHERE user_id = %s", (user_id,))
        total_games = cursor.fetchone()['count']
        
        # Games won
        cursor.execute("SELECT COUNT(*) as count FROM game_history WHERE user_id = %s AND won = 1", (user_id,))
        games_won = cursor.fetchone()['count']
        
        # Win rate
        win_rate = round((games_won / total_games * 100) if total_games > 0 else 0)
        
        # Average score
        cursor.execute("SELECT AVG(final_score) as avg FROM game_history WHERE user_id = %s AND completed = 1", (user_id,))
        avg_result = cursor.fetchone()['avg']
        avg_score = round(avg_result) if avg_result else 0
        
        # Recent games
        cursor.execute("""
            SELECT subject, completed, won, final_score, rounds_completed, date_played
            FROM game_history WHERE user_id = %s 
            ORDER BY date_played DESC LIMIT 5
        """, (user_id,))
        recent_games = cursor.fetchall()
        
        # Format recent games for display
        formatted_games = []
        for game in recent_games:
            formatted_games.append({
                'subject': game['subject'],
                'completed': game['completed'],
                'won': game['won'],
                'final_score': game['final_score'],
                'round': game['rounds_completed'],
                'score': game['final_score'] if game['completed'] else f"{game['rounds_completed']}/3",
                'date': game['date_played'].strftime('%b %d, %Y')
            })
        
        return {
            'total_games': total_games,
            'games_won': games_won,
            'win_rate': win_rate,
            'avg_score': avg_score,
            'recent_games': formatted_games
        }
    except Exception as e:
        print(f"Error getting user stats: {e}")
        return {
            'total_games': 0,
            'games_won': 0,
            'win_rate': 0,
            'avg_score': 0,
            'recent_games': []
        }

# Loading route
@app.route("/loading")
def loading():
    message = request.args.get("message", "Loading your experience")
    round_info = request.args.get("round_info", "")
    redirect_url = request.args.get("redirect_url", "/profile")
    delay = float(request.args.get("delay", "2"))
    
    return render_template("loading.html", 
                         message=message, 
                         round_info=round_info,
                         redirect_url=redirect_url, 
                         delay=delay)

# Authentication Routes
@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("loading", 
                               message="Welcome back!", 
                               redirect_url=url_for("profile"),
                               delay=1.5))
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
            return redirect(url_for("loading",
                                   message="Account created successfully!",
                                   redirect_url=url_for("index"),
                                   delay=2))
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
        return redirect(url_for("loading",
                               message=f"Welcome back, {user['username']}!",
                               redirect_url=url_for("profile"),
                               delay=2))
    return "Invalid credentials", 401

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("loading",
                           message="Logging you out",
                           redirect_url=url_for("index"),
                           delay=1.5))

# Profile/Lobby Route
@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("index"))
    
    # Get user info
    cursor.execute("SELECT username, created_at FROM users WHERE id = %s", (session["user_id"],))
    user = cursor.fetchone()
    
    # Get user stats
    stats = get_user_stats(session["user_id"])
    
    join_date = user['created_at'].strftime('%B %Y') if user['created_at'] else 'Recently'
    
    return render_template("profile.html", 
                         username=user['username'],
                         join_date=join_date,
                         **stats)

# Game Routes
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
    session["game_start_time"] = datetime.now().isoformat()
    
    return redirect(url_for("loading",
                           message="Loading Round 1",
                           round_info="Simple Round",
                           redirect_url=url_for("play_round"),
                           delay=3))

@app.route("/play_round", methods=["GET", "POST"])
def play_round():
    if "user_id" not in session:
        return redirect(url_for("index"))

    current_round = session.get("current_round", 1)
    subject = session.get("subject")
    difficulties = {1: "Simple", 2: "Intermediate", 3: "Advanced"}
    difficulty = difficulties.get(current_round, "Simple")

    if request.method == "POST":
        # Process answers
        answers = request.form
        round_questions = session.get(f"quiz_round_{current_round}", {})
        correct_count = 0
        
        for q_id_str, selected_opt in answers.items():
            q_id = str(q_id_str)
            if q_id in round_questions:
                correct_answer = round_questions[q_id]["correct"]
                if str(selected_opt).strip().lower() == correct_answer.lower():
                    correct_count += 1

        # Store round score
        session[f"round_{current_round}_score"] = correct_count

        if correct_count >= 5:
            if current_round == 3:
                # Game completed - calculate final score and save
                total_score = sum([
                    session.get("round_1_score", 0),
                    session.get("round_2_score", 0),
                    session.get("round_3_score", 0)
                ])
                save_game_result(session["user_id"], subject, True, True, total_score, 3)
                
                return redirect(url_for("loading",
                                       message="Congratulations!",
                                       round_info="You completed all rounds!",
                                       redirect_url=url_for("game_won"),
                                       delay=3))
            else:
                session["current_round"] = current_round + 1
                next_round = session["current_round"]
                next_difficulty = difficulties.get(next_round, "Advanced")
                return redirect(url_for("loading",
                                       message=f"Loading Round {next_round}",
                                       round_info=f"{next_difficulty} Round",
                                       redirect_url=url_for("play_round"),
                                       delay=3))
        else:
            # Game failed - save partial result
            total_score = sum([
                session.get("round_1_score", 0),
                session.get("round_2_score", 0),
                session.get("round_3_score", 0)
            ])
            save_game_result(session["user_id"], subject, False, False, total_score, current_round)
            
            return redirect(url_for("loading",
                                   message="Game Over",
                                   round_info=f"You scored {correct_count}/10",
                                   redirect_url=url_for("game_over"),
                                   delay=2.5))

    # Generate quiz
    try:
        attempts = [difficulty, "Advanced", "Intermediate"]
        quiz = None
        
        for attempt_difficulty in attempts:
            try:
                response = generate_mcq_chain.invoke({
                    "subject": subject,
                    "number": 10,
                    "tone": attempt_difficulty,
                    "response_json": json.dumps(RESPONSE_JSON)
                })
                
                raw_quiz = response.get("quiz", "")
                if len(str(raw_quiz)) > 50:
                    quiz = clean_quiz_json(raw_quiz)
                    if quiz and len(quiz) >= 10:
                        break
            except Exception:
                continue

        if not quiz:
            return redirect(url_for("loading",
                                   message="Quiz generation failed",
                                   redirect_url=url_for("game_over"),
                                   delay=2))

        session[f"quiz_round_{current_round}"] = quiz
        return render_template("round.html", round=current_round, difficulty=difficulty, quiz=quiz)
    
    except Exception as e:
        return redirect(url_for("loading",
                               message="Error occurred",
                               redirect_url=url_for("game_over"),
                               delay=2))

@app.route("/game_over")
def game_over():
    return render_template("game_over.html")

@app.route("/game_won")
def game_won():
    return render_template("game_won.html")

if __name__ == "__main__":
    app.run(debug=True)