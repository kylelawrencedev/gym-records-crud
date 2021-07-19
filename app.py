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


def valid_user(username):
    '''
    Checks if the user is Signed In with a session key

            Parameters:
                username: username from database collection users
            Returns:
                True/False: True if user is in session.
                            False if user not in session,
                            user will be redirected to relevant page

    https://github.com/AudreyLL88/MS3__Sante/blob/master/app.py
    Help for user signed in or guest user
    '''
    if "user" in session.keys():
        if session["user"] == username:
            return True

    return False


@app.route("/")
@app.route("/home")
def home():
    '''
    The landing page for the whole site. All users can see
    this page, whether they are signed in or not
            Parameters:
                None
            Returns:
                Renders Template : index.html
    '''
    return render_template("index.html")


@app.route("/get_overview")
def get_overview():
    '''
    Displays all the workouts from the workouts Collection
    Overview.html page will show all relevant results from
    the workouts collection
            Parameters:
                None
            Returns:
                Renders Template : overview.html
    '''
    if "user" in session:
        session["user"].lower()
    # prevent guest user access
    else:
        return render_template("403.html")

    workouts = list(mongo.db.workouts.find().sort("exercise_date", -1))
    return render_template("overview.html", workouts=workouts)


@app.route("/search", methods=["GET", "POST"])
def search():
    '''
    Allows the user to search the workouts collection

            Parameters:
                None
            Returns:
                Retrieves the relevant workouts from the collection
                Renders Template : overview.html
    '''
    if "user" in session:
        session["user"].lower()
    # prevent guest user access
    else:
        return render_template("403.html")

    query = request.form.get("query")
    workouts = list(mongo.db.workouts.find({"$text": {"$search": query}}))
    return render_template("overview.html", workouts=workouts)


@app.route("/account", methods=["GET", "POST"])
def account():
    '''
    Login/Create account page. Visable to all users

            Parameters:
                None
            Returns:
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

            Parameters:
                None
            Returns:
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

            Parameters:
                None
            Returns:
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
def profile(username):
    '''
    Retrieves the username and records from the database.
    Displays the users stored data from the users collection
    and renders the profile.html page

    If user not in session, redirect to def login()

            Parameters:
                username: Retrieves users information from the database
            Returns:
                Redirect : def login()
                Renders Templates : def login()

    '''
    records = list(mongo.db.records.find())
    # grab the session user's username from database
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if not valid_user(username.lower()):
        return redirect(url_for("login"))

    if session["user"]:
        return render_template(
            "profile.html", username=username, records=records)

    return redirect(url_for("login"))


@app.route("/add_record/", methods=["GET", "POST"])
def add_record():
    '''
    Lets user fill out form for records. All data entered
    onto form is saved to records Collection in database

    If user not in session, redirected to def login()

            Parameters:
                None
            Returns:
                Redirect : def login()
                Renders Template : add_record.html
    '''
    if "user" in session:
        user = session["user"].lower()

        if user == session["user"].lower():
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
    else:
        return render_template("403.html")


@app.route("/edit_record/<record_id>", methods=["GET", "POST"])
def edit_record(record_id):
    '''
    Lets the user retrieve a record already stored in the
    database and edit that specific record. Displays the
    stored record from the database in the form, in the relevant fields

            Parameters:
                record_id: This is the unique identifier that is
                associated with each stored record
            Returns:
                Redirect : def login()
                Renders Template : edit_record.html
    '''
    record_data = mongo.db.records.find_one({"_id": ObjectId(record_id)})

    if not valid_user(record_data["created_by"]):
        return redirect(url_for("login"))

    if request.method == "POST":
        update = {
            "user_fullName": request.form.get("user_fullName"),
            "user_height": request.form.get("user_height"),
            "user_weight": request.form.get("user_weight"),
            "date_added": request.form.get("date_added"),
            "created_by": session["user"],
        }
        mongo.db.records.update_many({"_id": ObjectId(record_id)}, update)
        flash("Record Successfully Updated")
        return redirect(url_for("profile", username=session["user"]))

    record = mongo.db.records.find_one({"_id": ObjectId(record_id)})
    return render_template("edit_record.html", record=record)


@app.route("/delete_record/<record_id>")
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
            Returns:
                Redirect : def login()
                Redirect : def profile(username)
    '''
    record_data = mongo.db.records.find_one({"_id": ObjectId(record_id)})

    if not valid_user(record_data["created_by"]):
        return redirect(url_for("login"))

    mongo.db.records.remove({"_id": ObjectId(record_id)})
    flash("Record Deleted")
    return redirect(url_for("profile", username=session["user"]))


@app.route("/logout")
def logout():
    '''
    Allows user to logout of their session

            Parameters:
                None
            Returns:
                Redirect : Redirects user back to def login()
    '''
    # remove user from session cookies
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/add_workout", methods=["GET", "POST"])
def add_workout():
    '''
    Allows the user to add a workout to the workouts Collection
    Shows a form for the user to fill out relevant fields to
    be saved to the database and retreived later

    If user not in session they will be redirected to the
    rendered template of 403.html

            Parameters:
                None
            Returns:
                Renders Template : 403.html
                Renders Template : def get_overview()
    '''
    if "user" in session:
        user = session["user"].lower()

        if user == session["user"].lower():
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

        # prevent other registered user access
        else:
            return redirect(url_for("login"))

    # prevent guest user access
    else:
        return render_template("403.html")


@app.route("/edit_workout/<exercise_id>", methods=["GET", "POST"])
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
            Returns:
                Redirect: def login()
                Renders Template : edit_workout.html
    '''
    workout_data = mongo.db.workouts.find_one({"_id": ObjectId(exercise_id)})

    if not valid_user(workout_data["created_by"]):
        return redirect(url_for("login"))

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
        mongo.db.workouts.update_many({"_id": ObjectId(exercise_id)}, submit)
        flash("Workout Session Successfully Updated")
        return redirect(url_for("get_overview"))
    workout = mongo.db.workouts.find_one({"_id": ObjectId(exercise_id)})
    return render_template("edit_workout.html", workout=workout)


@app.route("/delete_workout/<exercise_id>")
def delete_workout(exercise_id):
    '''
    Allows the user to delete the relevant exercise

    If user not in session, user will be redirect to
    def login()

            Parameters:
                exercise_id: Fetches the relevant exericse using
                the exercise id. Deletes the relevant stored
                workout from the database collection.
            Returns:
                Redirect : def login()
                Redirect : def get_overview()
    '''
    workout_data = mongo.db.workouts.find_one({"_id": ObjectId(exercise_id)})

    if not valid_user(workout_data["created_by"]):
        return redirect(url_for("login"))
    mongo.db.workouts.remove({"_id": ObjectId(exercise_id)})
    flash("Workout Deleted")
    return redirect(url_for("get_overview"))


# Error Handling
@app.errorhandler(403)
def forbidden(e):
    '''
    If user tries to access a forbidden link/page on the site

            Parameters:
                None
            Returns:
                Renders Template : 403.html
    '''

    return render_template('403.html'), 403


@app.errorhandler(404)
def page_not_found(e):
    '''
    If the user enters a url for the site that cannot be found,
    they are shown this page

            Parameters:
                None
            Returns:
                Renders Template : 404.html
    '''
    return render_template('404.html'), 404


# Error 500 handler route
@app.errorhandler(500)
def server_error(e):
    '''
    If there is a server issue, the user will be shown this page

            Parameters:
                None
            Returns:
                Renders Template : 500.html
    '''
    return render_template('500.html'), 500


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
