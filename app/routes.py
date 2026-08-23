from flask import Blueprint, render_template, request, redirect, session, jsonify, flash, url_for

from app.models import Patient, Bill, BillItem, Role, User, Department, Doctor
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

    # Temporary hardcoded admin login (kept as a fallback for now)
    if username == "admin" and password == "admin":

        session["user"] = username
        session["role"] = "Admin"

        return redirect("/dashboard")

    # Real users created via User Setup
    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):

        if user.status != "Active":
            flash("Your account is inactive. Please contact the administrator.", "danger")
            return redirect("/")

        session["user"] = user.username
        session["user_id"] = user.id
        session["role"] = user.role.name if user.role else None

        return redirect("/dashboard")

    flash("Invalid Username or Password", "danger")
    return redirect("/")



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

        year = datetime.now().year

        last_patient = Patient.query.order_by(
            Patient.id.desc()
        ).first()

        if last_patient:
            number = last_patient.id + 1
        else:
            number = 1

        patient_no = f"{year}{number:04d}"

        full_name = (
            request.form.get("first_name", "")
            + " "
            + request.form.get("last_name", "")
        )

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

        return redirect(url_for("main.patient_registration"))

    # Load departments
    departments = Department.query.filter_by(
        status="Active"
    ).order_by(
        Department.department_name.asc()
    ).all()

    # Load active doctors
    doctors = Doctor.query.filter_by(
        status="Active"
    ).order_by(
        Doctor.doc_name.asc()
    ).all()

    return render_template(
        "patient/registration.html",
        departments=departments,
        doctors=doctors
    )

# ==============================
# Patient List
# ==============================

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


# ==============================
# Department Setup
# ==============================
@main.route("/department_setup", methods=["GET"])
def department_setup():

    if "user" not in session:
        return redirect("/")

    departments = Department.query.order_by(
        Department.id.desc()
    ).all()

    return render_template(
        "setup/department_setup.html",
        departments=departments
    )


@main.route("/add_department", methods=["GET", "POST"])
def add_department():
    if "user" not in session:
        return redirect("/")

    if request.method == "POST":

        dep_code = request.form.get("dep_code")
        department_name = request.form.get("department_name")
        dep_type = request.form.get("dep_type")
        status = request.form.get("status")

        # Check duplicate department code
        existing_department = Department.query.filter_by(
            dep_code=dep_code
        ).first()

        if existing_department:
            flash("Department code already exists.", "error")
            return render_template("setup/add_department.html")

        # Create department
        department = Department(
            dep_code=dep_code,
            department_name=department_name,
            dep_type=dep_type,
            status=status
        )

        db.session.add(department)
        db.session.commit()

        flash("Department added successfully.", "success")

        return redirect(url_for("main.add_department"))

    return render_template("setup/add_department.html")

@main.route("/department/edit/<int:dep_id>", methods=["GET", "POST"])
def edit_department(dep_id):

    if "user" not in session:
        return redirect("/")

    # Get the actual department from database
    department = Department.query.get_or_404(dep_id)

    if request.method == "POST":

        dep_code = request.form.get("dep_code", "").strip()
        department_name = request.form.get("department_name", "").strip()
        dep_type = request.form.get("dep_type", "").strip()
        status = request.form.get("status", "").strip()

        # Validation
        if not dep_code or not department_name or not dep_type or not status:
            flash("All department fields are required.", "error")
            return render_template(
                "setup/edit_department.html",
                department=department
            )

        # Check duplicate department code
        existing_department = Department.query.filter(
            Department.dep_code == dep_code,
            Department.id != dep_id
        ).first()

        if existing_department:
            flash("Department code already exists.", "error")
            return render_template(
                "setup/edit_department.html",
                department=department
            )

        # Update department
        department.dep_code = dep_code
        department.department_name = department_name
        department.dep_type = dep_type
        department.status = status

        db.session.commit()

        flash("Department updated successfully!", "success")

        return redirect(url_for("main.department_setup"))

    return render_template(
        "setup/edit_department.html",
        department=department
    )

# ==============================
# Doctor Setup
# ==============================
# ==============================
# Doctor Setup
# ==============================

@main.route("/doctor-setup")
def doctor_setup():

    if "user" not in session:
        return redirect("/")

    doctors = Doctor.query.order_by(
        Doctor.id.desc()
    ).all()

    return render_template(
        "setup/doctor_setup.html",
        doctors=doctors
    )


# ==============================
# Add Doctor
# ==============================

@main.route("/add-doctor", methods=["GET", "POST"])
def add_doctor():

    if "user" not in session:
        return redirect("/")

    if request.method == "POST":

        doc_code = request.form.get("doc_code")
        doc_name = request.form.get("doc_name")
        department_id = request.form.get("department_id")
        specialization = request.form.get("specialization")
        email = request.form.get("email")
        phone = request.form.get("phone")
        status = request.form.get("status")

        # Check duplicate doctor code
        existing_doctor = Doctor.query.filter_by(
            doc_code=doc_code
        ).first()

        if existing_doctor:

            flash(
                "Doctor code already exists.",
                "error"
            )

            departments = Department.query.order_by(
                Department.id.desc()
            ).all()

            return render_template(
                "setup/add_doctor.html",
                departments=departments
            )

        # Create doctor
        doctor = Doctor(
            doc_code=doc_code,
            doc_name=doc_name,
            department_id=department_id,
            specialization=specialization,
            email=email,
            phone=phone,
            status=status
        )

        db.session.add(doctor)
        db.session.commit()

        flash(
            "Doctor added successfully!",
            "success"
        )

        return redirect(
            url_for("main.doctor_setup")
        )

    # Get departments from database
    departments = Department.query.order_by(
        Department.id.desc()
    ).all()

    return render_template(
        "setup/add_doctor.html",
        departments=departments
    )


# ==============================
# Edit Doctor
# ==============================

@main.route(
    "/edit-doctor/<int:doctor_id>",
    methods=["GET", "POST"]
)
def edit_doctor(doctor_id):

    if "user" not in session:
        return redirect("/")

    doctor = Doctor.query.get_or_404(
        doctor_id
    )

    if request.method == "POST":

        doctor.doc_code = request.form.get(
            "doc_code"
        )

        doctor.doc_name = request.form.get(
            "doc_name"
        )

        doctor.department_id = request.form.get(
            "department_id"
        )

        doctor.specialization = request.form.get(
            "specialization"
        )

        doctor.email = request.form.get(
            "email"
        )

        doctor.phone = request.form.get(
            "phone"
        )


        doctor.status = request.form.get(
            "status"
        )

        db.session.commit()

        flash(
            "Doctor edited successfully!",
            "success"
        )

        return redirect(
            url_for("main.doctor_setup")
        )

    # Get departments from database
    departments = Department.query.order_by(
        Department.id.desc()
    ).all()

    return render_template(
        "setup/edit_doctor.html",
        doctor=doctor,
        departments=departments
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
# User Setup List
# ==============================

@main.route("/user_setup")
def user_setup():

    if "user" not in session:
        return redirect("/")

    users = User.query.all()

    return render_template(
        "setup/user_setup.html",
        users=users
    )

@main.route("/add_user", methods=["GET", "POST"])
def add_user():

    if "user" not in session:
        return redirect(url_for("main.login"))

    roles = Role.query.all()

    if request.method == "POST":

        full_name = request.form.get("full_name")
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        email = request.form.get("email")
        role_id = request.form.get("role_id")
        status = request.form.get("status")

        # Password confirmation
        if password != confirm_password:
            flash("Passwords do not match", "danger")
            return redirect(url_for("main.add_user"))

        # Check username
        existing_user = User.query.filter_by(
            username=username
        ).first()

        if existing_user:
            flash("Username already taken", "danger")
            return redirect(url_for("main.add_user"))

        # Create user
        user = User(
            full_name=full_name,
            username=username,
            email=email,
            role_id=int(role_id),
            status=status
        )

        # Hash password
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash(
            "User created successfully!",
            "success"
        )

        # Go back to User Setup
        return redirect(
            # url_for("main.user_setup")
        url_for("main.add_user")
        )

    return render_template(
        "setup/add_user.html",
        roles=roles
    )

@main.route("/edit_user/<int:user_id>", methods=["GET", "POST"])
def edit_user(user_id):

    if "user" not in session:
        return redirect("/")

    user = User.query.get_or_404(user_id)

    if request.method == "POST":

        full_name = request.form["full_name"]
        username = request.form["username"]
        email = request.form["email"]
        role_id = request.form["role_id"]
        status = request.form["status"]
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        # Username taken by someone ELSE
        existing_user = User.query.filter(
            User.username == username,
            User.id != user.id
        ).first()

        if existing_user:
            flash("Username already taken", "danger")
            return redirect(url_for("main.edit_user", user_id=user.id))

        # Password is optional on edit — only update if they typed one
        if password:
            if password != confirm_password:
                flash("Passwords do not match", "danger")
                return redirect(url_for("main.edit_user", user_id=user.id))

            user.set_password(password)

        user.full_name = full_name
        user.username = username
        user.email = email
        user.role_id = role_id
        user.status = status

        db.session.commit()

        flash("User updated successfully!", "success")

        return redirect(url_for("main.edit_user", user_id=user.id))

    roles = Role.query.all()

    return render_template(
         "setup/edit_user.html",
        user=user,
        roles=roles
    )

# ==============================
# Patient Reports
# ==============================
@main.route("/patient-report")
def patient_report():

    patients = Patient.query.all()

    return render_template(
        "reports/patient_report.html",
        patients=patients,
        active_page="patient_report"
    )


@main.route("/patient-report/<int:patient_id>")
def patient_report_view(patient_id):

    patient = Patient.query.get_or_404(patient_id)

    return render_template(
        "reports/patient_report_view.html",
        patient=patient,
        active_page="patient_report"
    )



# ==============================
# Logout
# ==============================

@main.route("/logout")
def logout():

    session.pop("user", None)

    return redirect("/")