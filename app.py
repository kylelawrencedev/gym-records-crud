import os
from functools import wraps
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


def login_required(f):
    '''
Checks if user is in session
If user not in session, redirected to login

@login_required used all all relevant functions
    '''
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'user' in session:
            return f(*args, **kwargs)
        else:
            flash("You Need to Login First")
            return redirect(url_for('login', next=request.url))

    return wrap


@app.route("/")
@app.route("/home")
def home():
    '''
The landing page for the whole site. All users can see
this page, whether they are signed in or not

Args:
Renders Template : index.html
    '''
    return render_template("index.html")


@app.route("/get_overview")
@login_required
def get_overview():
    '''
Displays all the workouts from the workouts Collection
Overview.html page will show all relevant results from
the workouts collection

Args:
Renders Template : overview.html
    '''
    workouts = list(mongo.db.workouts.find().sort("exercise_date", -1))
    return render_template("overview.html", workouts=workouts)


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    '''
Allows the user to search the workouts collection

Args:
Retrieves the relevant workouts from the collection
Renders Template : overview.html
    '''
    query = request.form.get("query")
    workouts = list(mongo.db.workouts.find({"$text": {"$search": query}}))
    return render_template("overview.html", workouts=workouts)


@app.route("/account", methods=["GET", "POST"])
def account():
    '''
Login/Create account page. Visable to all users

Args:
Renders Template : account.html
    '''
    return render_template("account.html")


@app.route("/create_account", methods=["GET", "POST"])
def create_account():
    '''
Allows a user to create an account with a username and a password
If username is taken/ already exists then the user will get a flash
message tellimg them the username is taken
create_account will generate an account to be added to
the users collection

Args:
Renders Template : account.html
    '''
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
    '''
Checks the information the user has entered onto the login page is correct.
If the user information matches the username and password from
the users Collection, the user will be logged into the site

Args:
Renders Templates : account.html
    '''
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
@login_required
def profile(username):
    '''
Retrieves the username and records from the database.
Displays the users stored data from the users collection
and renders the profile.html page

If user not in session, redirect to def login()

Parameters:
username: Retrieves users information from the database

Args:
Redirect : def login()
Renders Templates : def login()
    '''
    records = list(mongo.db.records.find())
    # grab the session user's username from database
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template(
            "profile.html", username=username, records=records)

    return redirect(url_for("login"))


@app.route("/add_record/", methods=["GET", "POST"])
@login_required
def add_record():
    '''
Lets user fill out form for records. All data entered
onto form is saved to records Collection in database

If user not in session, redirected to def login()

Args:
Redirect : def login()
Renders Template : add_record.html
    '''
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
@login_required
def edit_record(record_id):
    '''
Lets the user retrieve a record already stored in the
database and edit that specific record. Displays the
stored record from the database in the form, in the relevant fields

Parameters:
record_id: This is the unique identifier that is
associated with each stored record

Args:
Redirect : def login()
Renders Template : edit_record.html
    '''
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
@login_required
def delete_record(record_id):
    '''
Allows the user to delete a record if they do not
wish to keep that specific record

Fetches the relevant record and deletes it from
the database collection. User gets redirected to
profile.html with deleted record not showing

If user not in session, redirected back to def login()

Parameters:
record-id: Retrieves the record_id from the records
collection in the database

Args:
Redirect : def login()
Redirect : def profile(username)
    '''
    mongo.db.records.remove({"_id": ObjectId(record_id)})
    flash("Record Deleted")
    return redirect(url_for("profile", username=session["user"]))


@app.route("/logout")
def logout():
    '''
Allows user to logout of their session

Args:
 Redirect : Redirects user back to def login()
    '''
    # remove user from session cookies
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/add_workout", methods=["GET", "POST"])
@login_required
def add_workout():
    '''
Allows the user to add a workout to the workouts Collection
Shows a form for the user to fill out relevant fields to
be saved to the database and retreived later

If user not in session they will be redirected to the
rendered template of 403.html

Args:
Renders Template : 403.html
Renders Template : def get_overview()
    '''
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
@login_required
def edit_workout(exercise_id):
    '''
Retrieves the users stored workout from the workouts collection.
Shows the same form for when the user added the workout, with
the form already filled out with all the stored information
from the database Collection. The information can then be editted

If user not in session redirected to def login()

Parameters:
exercise_id: Retrieves the stored exercise, with all the
 relevant fields from the collection showing in the form in
the correct spots in the form.

Args:
Redirect: def login()
Renders Template : edit_workout.html
    '''
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
@login_required
def delete_workout(exercise_id):
    '''
Allows the user to delete the relevant exercise

If user not in session, user will be redirect to
def login()

Parameters:
exercise_id: Fetches the relevant exericse using
the exercise id. Deletes the relevant stored
workout from the database collection.

Args:
Redirect : def login()
Redirect : def get_overview()
    '''
    mongo.db.workouts.remove({"_id": ObjectId(exercise_id)})
    flash("Workout Deleted")
    return redirect(url_for("get_overview"))


# Error 500 handler route
@app.errorhandler(500)
def server_error(e):
    '''
If there is a server issue, the user will be shown this page
Args:
Renders Template : 500.html
    '''
    return render_template('500.html'), 500


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=False)
