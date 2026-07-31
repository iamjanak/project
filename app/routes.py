from flask import Blueprint, render_template, request, redirect, session, jsonify

main = Blueprint("main", __name__)


# Login page
@main.route("/")
def login():
    return render_template("login.html")


# Login form submit
@main.route("/login", methods=["POST"])
def login_post():

    username = request.form["username"]
    password = request.form["password"]

    # Temporary login
    if username == "admin" and password == "admin":

        session["user"] = username

        return redirect("/dashboard")

    return "Invalid Username or Password"


# Dashboard page
@main.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/")

    return render_template(
        "dashboard.html",
        patient_count=348,
        doctor_count=78,
        bill_count=52
    )


# Logout
@main.route("/logout")
def logout():

    session.pop("user", None)

    return redirect("/")