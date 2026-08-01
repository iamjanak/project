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
        active_page="dashboard",
        patient_count=348,
        doctor_count=78,
        bill_count=52
    )



# ==============================
# Patient Registration Page
# ==============================

@main.route("/registration")
def patient_registration():

    if "user" not in session:
        return redirect("/")

    return render_template(
        "patient/registration.html"
    )

# Billing Page
@main.route("/billing", methods=["GET", "POST"])
def billing():

    if "user" not in session:
        return redirect("/")

    if request.method == "POST":
        # You will handle form later
        patient = request.form.get("patient_name")
        amount = request.form.get("amount")
        print(patient, amount)

    return render_template(
        "billing/patient_billing.html",
        active_page="billing"
    )
@main.route("/user_setup")
def user_setup():

    if "user" not in session:
        return redirect("/")

    return render_template(
        "setup/user_setup.html"
    )

@main.route("/add-user")
def add_user():

    if "user" not in session:
        return redirect("/")

    return render_template("setup/add_user.html")

# ==============================
# Department Setup
# ==============================

@main.route("/department_setup")
def department_setup():

    if "user" not in session:
        return redirect("/")

    return render_template(
        "setup/department_setup.html"
    )

# ==============================
# Add Department
# ==============================

@main.route("/add_department", methods=["GET", "POST"])
def add_department():

    if "user" not in session:
        return redirect("/")


    if request.method == "POST":

        department_name = request.form["department_name"]
        description = request.form["description"]
        status = request.form["status"]


        # Database will be connected later


        return redirect("/department-setup")


    return render_template("setup/add_department.html")



# ==============================
# Doctor Setup
# ==============================

@main.route("/doctor_setup")
def doctor_setup():

    if "user" not in session:
        return redirect("/")

    return render_template(
        "setup/doctor_setup.html"
    )



# ==============================
# Add Doctor
# ==============================

@main.route("/add_doctor", methods=["GET", "POST"])
def add_doctor():

    if "user" not in session:
        return redirect("/")


    if request.method == "POST":

        doctor_name = request.form["doctor_name"]
        specialization = request.form["specialization"]
        department = request.form["department"]
        phone = request.form["phone"]
        email = request.form["email"]
        status = request.form["status"]


        # Database connection later


        return redirect("/doctor_setup")


    return render_template(
        "setup/add_doctor.html"
    )

# ==============================
# Generate Bill
# ==============================

@main.route("/generate_bill")
def generate_bill():

    if "user" not in session:
        return redirect("/")


    # Temporary bill data
    bill_data = {

        "hospital_name": "SwasthaCare Hospital",
        "hospital_address": "Kathmandu, Nepal",

        "bill_no": "CS2026-00001",
        "patient_no": "20260001",

        "patient_name": "Test Patient",
        "age_gender": "25 Yrs / Male",

        "doctor": "Dr. Saurab Sharma",
        "department": "Cardiology",

        "transaction_date": "2026-08-02",


        "items": [

            {
                "name": "Doctor Consultation Charge",
                "code": "DOC001",
                "qty": 1,
                "rate": 500
            },

            {
                "name": "ECG Test",
                "code": "LAB002",
                "qty": 1,
                "rate": 800
            }

        ],

        "discount": 0

    }


    # Calculate total

    subtotal = 0

    for item in bill_data["items"]:
        subtotal += item["qty"] * item["rate"]


    bill_data["subtotal"] = subtotal

    bill_data["total"] = subtotal - bill_data["discount"]


    return render_template(
        "billing/bill.html",
        bill=bill_data
    )


# Logout
@main.route("/logout")
def logout():

    session.pop("user", None)

    return redirect("/")