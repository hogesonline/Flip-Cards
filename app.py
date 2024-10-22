from datetime import datetime
from functools import wraps

from flask import Flask, redirect, render_template, request, session
from sqlalchemy import create_engine, text
from werkzeug.security import check_password_hash, generate_password_hash

from flask_session import Session

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
    pass


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
    pass


@app.route("/add", methods=["GET", "POST"])
@login_required
def add_question():
    if request.method == "POST":
        """Add questions to the list"""
        pass
    else:
        """Show add question form"""
        pass

@app.route("/quiz", methods=["GET", "POST"])
@login_required
def quiz():
    if request.method == "GET":
        """Show quiz setup"""
        pass
    else:
        """Show quiz questions"""
        pass

@app.route('/next_question', methods=['POST'])
def next_question():
    """
    If there is a next question, redirect the user to complete it.
    If there is not, inform the user
    """
    pass

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted

        # Ensure password was submitted

        # Query database for username

        # Ensure username exists and password is correct

        # Remember which user has logged in

        # Redirect user to home page
        pass

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        pass


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id

    # Redirect user to login form
    pass


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted

        # Ensure password was submitted

        # Query database for username

        # Redirect user to home page
        pass

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        pass


@app.route("/remove", methods=["POST"])
@login_required
def remove():
    """Remove questions"""
    pass


if __name__ == "__main__":
    app.run(debug=True)
