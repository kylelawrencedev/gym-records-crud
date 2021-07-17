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
    return render_template("index.html")


@app.route("/get_overview")
def get_overview():
    workouts = list(mongo.db.workouts.find().sort("exercise_date", -1))
    return render_template("overview.html", workouts=workouts)


@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    workouts = list(mongo.db.workouts.find({"$text": {"$search": query}}))
    return render_template("overview.html", workouts=workouts)


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
    records = list(mongo.db.records.find())
    # grab the session user's username from database
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("profile.html", 
            username=username, records=records)

    return redirect(url_for("login"))


@app.route("/add_record", methods=["GET", "POST"])
def add_record():
    if request.method == "POST":
        record = {
            "user_fullName": request.form.get("user_fullName"),
            "user_height": request.form.get("user_height"),
            "user_weight": request.form.get("user_weight"),
            "date_added": request.form.get("date_added"),
            "created_by": session["user"],
        }
        mongo.db.records.insert_one(record)
        flash("Profile Records Successfully Added")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("add_record.html")


@app.route("/edit_record/<record_id>", methods=["GET", "POST"])
def edit_record(record_id):
    if request.method == "POST":
        update = {
            "user_fullName": request.form.get("user_fullName"),
            "user_height": request.form.get("user_height"),
            "user_weight": request.form.get("user_weight"),
            "date_added": request.form.get("date_added"),
            "created_by": session["user"],
        }
        mongo.db.records.update({"_id": ObjectId(record_id)}, update)
        flash("Record Successfully Updated")
        return redirect(url_for("profile", username=session["user"]))

    record = mongo.db.records.find_one({"_id": ObjectId(record_id)})
    return render_template("edit_record.html", record=record)


@app.route("/delete_record/<record_id>")
def delete_record(record_id):
    mongo.db.records.remove({"_id": ObjectId(record_id)})
    flash("Record Deleted")
    return redirect(url_for("profile", username=session["user"]))



@app.route("/logout")
def logout():
    # remove user from session cookies
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/add_workout", methods=["GET", "POST"])
def add_workout():
    if request.method == "POST":
        workout = [{
            "exercise_heading": request.form.getlist("exercise_heading"),
            "exercise_name": request.form.getlist("exercise_name"),
            "exercise_reps": request.form.getlist("exercise_reps"),
            "exercise_sets": request.form.getlist("exercise_sets"),
            "exercise_weight": request.form.getlist("exercise_weight"),
            "exercise_date": request.form.getlist("exercise_date"),
            "created_by": session["user"],
        }]
        mongo.db.workouts.insert_many(workout)
        flash("Workout Session Successfully Added")
        return redirect(url_for("get_overview"))
        
    return render_template("add_workout.html")


@app.route("/edit_workout/<exercise_id>", methods=["GET", "POST"])
def edit_workout(exercise_id):
    if request.method == "POST":
        submit = {
            "exercise_heading": request.form.getlist("exercise_heading"),
            "exercise_name": request.form.getlist("exercise_name"),
            "exercise_reps": request.form.getlist("exercise_reps"),
            "exercise_sets": request.form.getlist("exercise_sets"),
            "exercise_weight": request.form.getlist("exercise_weight"),
            "exercise_date": request.form.getlist("exercise_date"),
            "created_by": session["user"],
        }
        mongo.db.workouts.update({"_id": ObjectId(exercise_id)}, submit)
        flash("Workout Session Successfully Updated")
        return redirect(url_for("get_overview"))
    workout = mongo.db.workouts.find_one({"_id": ObjectId(exercise_id)})
    return render_template("edit_workout.html", workout=workout)


@app.route("/delete_workout/<exercise_id>")
def delete_workout(exercise_id):
    mongo.db.workouts.remove({"_id": ObjectId(exercise_id)})
    flash("Workout Deleted")
    return redirect(url_for("get_overview"))


# Error Handling
@app.errorhandler(403)
def forbidden(e):

    return render_template('403.html'), 403


@app.errorhandler(404)
def page_not_found(e):

    return render_template('404.html'), 404


# Error 500 handler route
@app.errorhandler(500)
def server_error(e):

    return render_template('500.html'), 500


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)


