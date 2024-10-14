import os # unused import

from sqlalchemy import create_engine, text
from flask import Flask, flash, redirect, render_template, request, session # unused imports: flash
from flask_session import Session
from tempfile import mkdtemp # unused import
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from datetime import datetime

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up the database
engine = create_engine('sqlite:///flip_cards.db')
connection = engine.connect()

CATEGORIES = ["Math", "Science", "History", "Geography", "English", "Art", "Music", "Technology", "Miscellaneous"]

#helper functions
def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
@login_required
def index():
    """Show list of questions"""
    select_text = text("SELECT * FROM flipcards WHERE user_id = :uid")
    questions = connection.execute(select_text, {"uid":session["user_id"]})
    questions = questions.fetchall()

    return render_template("index.html" , questions=questions)


@app.route("/add", methods=["GET", "POST"])
@login_required
def add_question():
    if request.method == "POST":
        """Add questions to the list"""
        question = request.form.get("question")
        answer = request.form.get("answer")
        category = request.form.get("category")
        difficulty = request.form.get("difficulty")
        if not question:
            return apology("Missing a question")
        if not answer:
            return apology("Missing an answer")
        if not difficulty:
            return apology("Missing a difficulty")
        if category not in CATEGORIES:
            return apology("Invalid Category")
        #store the registration
        add_question_db = text("INSERT INTO flipcards (user_id, question, answer, category, difficulty, created_date) values(:uid, :question, :answer, :category, :difficulty, :created)")   
        connection.execute(add_question_db, [{"uid": session["user_id"], "question":question, "answer":answer, "category":category, "difficulty":difficulty, "created":datetime.now()}])
        # does this allow for sql injection?
        connection.commit()
        return redirect("/") # why not redirect to /add? i'd imagine you wouldn't add only one card at a time
    else:
        return render_template("add_question.html" , categories=CATEGORIES)


### why not have these be in the same subdomain? quiz setup could be quiz for get,
### quiz could be pretty much the same, and next question could be qui with a ?q=2 or something

@app.route("/quiz_setup", methods=["GET"])
@login_required
def quiz_setup():
    """Show quiz questions"""
    return render_template("quiz_setup.html", categories = CATEGORIES)

@app.route("/quiz", methods=["POST"])
@login_required
def quiz():
    num_questions = request.form.get("num_quest")
    category = request.form.get("category")
    difficulty_start = request.form.get("difficulty_start")
    difficulty_finish = request.form.get("difficulty_stop")
    if not num_questions:
        return apology("Missing a number of questions")
    if not difficulty_start:
        return apology("Missing a difficulty minimum")
    if not difficulty_finish:
        return apology("Missing a difficulty maximum")
    if category not in CATEGORIES:
        return apology("Invalid Category")
    select_qry = text("SELECT * FROM flipcards WHERE category = :cat AND difficulty BETWEEN :diff_start AND :diff_finish ORDER BY RANDOM() LIMIT :num")
    questions = connection.execute(select_qry, {"cat":category, "diff_start":difficulty_start, "diff_finish":difficulty_finish, "num":num_questions})
    questions = questions.fetchall()
    session["questions"] = questions
    session["quest_num"] = 0
    return render_template("quiz.html", question=questions[0])

@app.route('/next_question', methods=['POST'])
def next_question():
    session['quest_num'] += 1
    if session['quest_num'] < len(session["questions"]):
        question = session["questions"][session['quest_num']]
        return render_template("quiz.html", question=question)
    else:
        question = {"question": "No more questions", "answer": ""}
        return render_template("quiz.html", question=question)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        select_qry = text("SELECT * FROM users WHERE username = :uname")
        rows = connection.execute(select_qry, [{"uname":request.form.get("username")}]) # same question about sql injection
        rows = rows.fetchall()


        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0][2], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0][0]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

# this appears to be no longer supported (quote.html and quoted.html don't exist)
@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        stock = lookup(request.form.get("symbol").upper()) # no lookup function imported

        if not stock:
            return apology("Invalid Symbol")

        return render_template("quoted.html", stock=stock)

    else:
        return render_template("quote.html")
    #return apology("TODO")


@app.route("/register", methods=["GET", "POST"])
def register():
    # Forget any user_id
    session.clear()
    """Register user"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)
        elif request.form.get("password2") != request.form.get("password"):
            return apology("passwords must match", 403)

        # Query database for username
        insert_qry = text("INSERT INTO users (username, hash) values(:uname,:pwd)")
        ## minor nitpick but my lsp isn't happy that you're using request.form.get twice instead of storing the value in a str the first time
        result = connection.execute(insert_qry, [{"uname":request.form.get("username"), "pwd":generate_password_hash(request.form.get("password"))}])
        connection.commit()
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

    #return apology("TODO")


@app.route("/remove", methods=["POST"])
@login_required
def remove():
    """Remove questions"""
    question = request.form.get("question")
    print(question)
    if not question:
        return apology("Something went wrong")
    remove_qry = text("DELETE FROM flipcards WHERE user_id = :uid AND card_id = :qid")
    connection.execute(remove_qry, {"uid": session["user_id"], "qid":question})
    connection.commit()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
