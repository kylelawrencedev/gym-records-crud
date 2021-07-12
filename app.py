import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/home")
def home():
    return render_template("base.html")


@app.route("/get_overview")
def get_overview():
    sessions = list(mongo.db.sessions.find())
    return render_template("overview.html", sessions=sessions)


@app.route("/account", methods=["GET", "POST"])
def account():
    return render_template("account.html")


@app.route("/create_account", methods=["GET", "POST"])
def create_account():
    if request.method == "POST":
        # check if username already exists in database
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already taken")
            return redirect(url_for("create_account"))

        create_account = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(
                request.form.get("password"), salt_length=128)
        }
        mongo.db.users.insert_one(create_account)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Account Created Successfully!")
        return redirect(url_for("profile", username=session["user"]))
    return render_template("account.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username already exists in database
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches users input
            if check_password_hash(
               existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(
                    request.form.get("username")))
                return redirect(url_for(
                    "profile", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("account.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # grab the session user's username from database
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("profile.html", username=username)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # remove user from session cookies
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/add_workout", methods=["GET", "POST"])
def add_workout():
    if request.method == "POST":
        session = {
            "exercise_heading": request.form.get("exercise_heading"),
            "exercise_name": request.form.get("exercise_name"),
            "exercise_reps": request.form.get("exercise_reps"),
            "exercise_sets": request.form.get("exercise_sets"),
            "exercise_weight": request.form.get("exercise_weight"),
            "exercise_date": request.form.get("exercise_date"),
        }
        mongo.db.sessions.insert_one(session)
        flash("Workout Session Successfully Added")
        return redirect(url_for("get_overview"))
        
    return render_template("add_workout.html")


@app.route("/edit_workout/<exercise_id>", methods=["GET", "POST"])
def edit_workout(exercise_id):
    session = mongo.db.sessions.find_one({"_id": ObjectId(exercise_id)})
    return render_template("edit_workout.html", session=session)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
