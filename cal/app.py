from flask import Flask, request, render_template, jsonify, session, redirect, url_for
from flask_cors import CORS
from random import randint

app = Flask(__name__)
CORS(app)
app.secret_key = 'your_secret_key_here'  # Required for session management

# User class to store user information and results
class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.results = {
            "correct": 0,
            "attempt": 0,
            "incorrect": 0,
            "question_count": 0
        }
        self.current_question = ""  # Store the current question for the user

    def check_answer(self, question, answer):
        self.results["attempt"] += 1
        if int(answer) == eval(question):  # Evaluate the question to check the answer
            self.results["correct"] += 1
            return True
        else:
            self.results["incorrect"] += 1
            return False

# In-memory storage for users (replace with a database in production)
users = {}

# Helper function to get the current user
def get_current_user():
    if 'username' in session:
        return users.get(session['username'])
    return None

# Routes
@app.route("/")
def entrance():
    if get_current_user():
        return render_template("math.html")
    return redirect(url_for('login'))

@app.route("/get_user")
def get_user():
    user = get_current_user()
    return jsonify({"username" : user.username})

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = users.get(username)
        if user and user.password == password:
            session['username'] = username
            return redirect(url_for('entrance'))
        return "Invalid username or password"
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username in users:
            return "Username already exists"
        users[username] = User(username, password)
        session['username'] = username
        return redirect(url_for('entrance'))
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route("/get_question")
def generate_question():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Not logged in"}), 401

    try:
        first = randint(0, 100)
        second = randint(0, 100)
        first, second = max(first, second), min(first, second)
        op = "+-"[randint(0, 1)]
        user.current_question = f'{first}{op}{second}'  # Store the question in the user's session
        user.results["question_count"] += 1
        return jsonify({"question": user.current_question})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/check_result', methods=["POST"])
def check_result():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Not logged in"}), 401

    try:
        data = request.get_json()
        question = data.get("question")
        answer = data.get("answer")

        if not question or not answer:
            return jsonify({"error": "Question or answer missing"}), 400

        # Check the answer using the User class method
        is_correct = user.check_answer(question, answer)
        return jsonify({
            "correct": is_correct,
            "results": user.results
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)