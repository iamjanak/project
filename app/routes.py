from flask import Blueprint, render_template, request, redirect, session, jsonify, flash, url_for

from app.models import Patient, Bill, BillItem
from app.database import db
from datetime import datetime


main = Blueprint("main", __name__)


# ==============================
# Login Page
# ==============================

@main.route("/")
def login():
    return render_template("login.html")


# ==============================
# Login Submit
# ==============================

@main.route("/login", methods=["POST"])
def login_post():

    username = request.form["username"]
    password = request.form["password"]

    # Temporary login
    if username == "admin" and password == "admin":

        session["user"] = username

        return redirect("/dashboard")

    return "Invalid Username or Password"



# ==============================
# Dashboard
# ==============================

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
# Patient Registration
# ==============================

@main.route("/registration", methods=["GET", "POST"])
def patient_registration():

    if "user" not in session:
        return redirect("/")


    if request.method == "POST":

        # Generate patient number
        year = datetime.now().year

        last_patient = Patient.query.order_by(
            Patient.id.desc()
        ).first()


        if last_patient:
            number = last_patient.id + 1
        else:
            number = 1


        patient_no = f"{year}{number:04d}"


        # Combine first and last name
        full_name = (
            request.form["first_name"]
            + " "
            + request.form["last_name"]
        )


        # Convert DOB from DD/MM/YYYY to YYYY-MM-DD
        dob_input = request.form.get("dob")

        if dob_input:
            dob = datetime.strptime(
                dob_input,
                "%d/%m/%Y"
            ).date()
        else:
            dob = None



        patient = Patient(

            patient_no=patient_no,

            full_name=full_name,

            dob=dob,

            age=request.form.get("age"),

            gender=request.form.get("gender"),

            phone=request.form.get("phone"),

            address=request.form.get("address"),

            department=request.form.get("department"),

            doctor=request.form.get("doctor_id")

        )


        db.session.add(patient)

        db.session.commit()


        flash("Patient registered successfully", "success")

        return redirect("/registration")


    return render_template(
        "patient/registration.html"
    )


@main.route("/patients")
def patient_list():

    if "user" not in session:
        return redirect("/")


    patients = Patient.query.order_by(
        Patient.id.desc()
    ).all()


    return render_template(
        "patient/patient_list.html",
        patients=patients,
        active_page="patient_list"
    )

# ==============================
# Billing
# ==============================
@main.route("/billing", methods=["GET", "POST"])
def billing():

    if "user" not in session:
        return redirect("/")


    if request.method == "POST":

        patient_no = request.form.get("patient_id")

        patient = Patient.query.filter_by(
            patient_no=patient_no
        ).first()

        if not patient:
            return "Patient not found"

        # NOTE: Actual bill creation happens via the AJAX call to
        # /patient/billing/save (see save_bill() below), which handles
        # bill-number generation, line items, and totals correctly.
        # This POST branch just re-renders the billing page; remove it
        # entirely and make this route GET-only if the form no longer
        # submits here directly.
        return render_template(
            "billing/patient_billing.html",
            active_page="billing"
        )


    return render_template(
        "billing/patient_billing.html",
        active_page="billing"
    )



# ==============================
# Fetch Patient For Billing
# ==============================

@main.route("/fetch_patient/<patient_no>")
def fetch_patient(patient_no):

    if "user" not in session:
        return jsonify({
            "error": "Unauthorized"
        }), 401


    patient = Patient.query.filter_by(
        patient_no=patient_no
    ).first()


    if not patient:
        return jsonify({
            "error": "Patient not found"
        }), 404


    return jsonify({

        "patient_no": patient.patient_no,
        "name": patient.full_name,
        "age": patient.age,
        "gender": patient.gender,
        "department": patient.department,
        "doctor": patient.doctor

    })

# ==============================
# Save Patient Bill
# ==============================

@main.route("/patient/billing/save", methods=["POST"])
def save_bill():

    if "user" not in session:
        return jsonify({
            "error": "Unauthorized"
        }), 401


    data = request.get_json()


    patient = Patient.query.filter_by(
        patient_no=data["patient_id"]
    ).first()


    if not patient:
        return jsonify({
            "error": "Patient not found"
        }), 404


    if not data.get("items"):
        return jsonify({
            "error": "No items provided"
        }), 400


    try:

        # ==========================
        # Generate Bill Number
        # ==========================

        today = datetime.now()

        last_bill = Bill.query.order_by(
            Bill.id.desc()
        ).first()


        if last_bill:
            bill_number = last_bill.id + 1
        else:
            bill_number = 1


        bill_no = (
            f"CS"
            f"{today.year}"
            f"{today.month:02d}"
            f"{today.day:02d}"
            f"{bill_number:04d}"
        )



        # ==========================
        # Compute subtotal / discount
        # from the line items themselves,
        # so the numbers are always consistent
        # (gross before discount, and total discount)
        # ==========================

        computed_subtotal = 0
        computed_discount = 0

        for item in data["items"]:
            gross = float(item["price"]) * float(item["qty"])
            net = float(item["netTotal"])

            computed_subtotal += gross
            computed_discount += (gross - net)


        grand_total = float(data["grand_total"])



        # ==========================
        # Create Bill
        # ==========================

        bill = Bill(

            bill_no=bill_no,

            patient_id=patient.id,

            subtotal=computed_subtotal,

            discount=computed_discount,

            total=grand_total,

            pay_type=data.get("pay_type", "Cash"),

            tender_amt=data.get("tender_amt", 0),

            return_amt=data.get("return_amt", 0),

            remarks=data.get("remarks", "")

        )


        db.session.add(bill)

        db.session.flush()



        for item in data["items"]:

            bill_item = BillItem(

                bill_id=bill.id,

                service_name=item["name"],

                quantity=item["qty"],

                rate=item["price"],

                amount=item["netTotal"]

            )


            db.session.add(bill_item)



        db.session.commit()


        return jsonify({

            "success": True,

            "bill_id": bill.id

        })

    except Exception as e:

        db.session.rollback()

        return jsonify({

            "error": str(e)

        }), 500

# ==============================
# User Setup
# ==============================

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

    return render_template(
        "setup/add_user.html"
    )



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



@main.route("/add_department", methods=["GET", "POST"])
def add_department():

    if "user" not in session:
        return redirect("/")


    if request.method == "POST":

        department_name = request.form["department_name"]
        description = request.form["description"]
        status = request.form["status"]


        # Database connection later


        return redirect("/department_setup")


    return render_template(
        "setup/add_department.html"
    )



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
@main.route("/generate_bill/<int:bill_id>")
def generate_bill(bill_id):

    if "user" not in session:
        return redirect("/")


    bill = Bill.query.get_or_404(bill_id)


    items = []

    for item in bill.items:

        gross = item.rate * item.quantity
        net = item.amount
        disc_amt = gross - net
        disc_pct = (disc_amt / gross * 100) if gross else 0

        items.append({
            "name": item.service_name,
            "code": getattr(item, "service_code", ""),
            "qty": item.quantity,
            "rate": item.rate,
            "total": gross,
            "disc_pct": disc_pct,
            "disc_amt": disc_amt,
            "net_total": net
        })


    bill_data = {

        "hospital_name": "SwasthaCare Hospital",
        "hospital_address": "Kathmandu, Nepal",

        "bill_no": bill.bill_no,

        "patient_no": bill.patient.patient_no,

        "patient_name": bill.patient.full_name,

        "age_gender": f"{bill.patient.age} Yrs / {bill.patient.gender}",

        "doctor": bill.patient.doctor,

        "department": bill.patient.department,

        "transaction_date": bill.bill_date.strftime("%Y-%m-%d")
            if hasattr(bill, "bill_date") and bill.bill_date else "",

        "items": items,

        "subtotal": bill.subtotal,

        "discount": bill.discount,

        "total": bill.total,

        "pay_type": bill.pay_type,

        "tender_amt": bill.tender_amt,

        "return_amt": bill.return_amt,

        "remarks": bill.remarks
    }


    return render_template(
        "billing/bill.html",
        bill=bill_data
    )

# ==============================
# Logout
# ==============================

@main.route("/logout")
def logout():

    session.pop("user", None)

    return redirect("/")