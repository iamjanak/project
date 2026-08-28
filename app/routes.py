from flask import Blueprint, render_template, request, redirect, session, jsonify, flash, url_for

from app.models import (
    Patient,
    Bill,
    BillItem,
    Role,
    User,
    Department,
    Doctor,
    Test,
    Deposit,
    BillRefund,

)

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

    if user and user.check_password(password

                                    
                                    ):

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

    # =================================================
    # POST - REGISTER PATIENT
    # =================================================
    if request.method == "POST":

        # -------------------------------------------------
        # Generate Patient Number
        # -------------------------------------------------
        year = datetime.now().year

        last_patient = Patient.query.order_by(
            Patient.id.desc()
        ).first()

        if last_patient:
            number = last_patient.id + 1
        else:
            number = 1

        patient_no = f"{year}{number:04d}"

        # -------------------------------------------------
        # Full Name
        # -------------------------------------------------
        first_name = request.form.get(
            "first_name",
            ""
        ).strip()

        last_name = request.form.get(
            "last_name",
            ""
        ).strip()

        full_name = f"{first_name} {last_name}".strip()

        # -------------------------------------------------
        # DOB
        # -------------------------------------------------
        dob_input = request.form.get(
            "dob",
            ""
        ).strip()

        if dob_input:

            try:
                dob = datetime.strptime(
                    dob_input,
                    "%d/%m/%Y"
                ).date()

            except ValueError:

                flash(
                    "Invalid date of birth. Please use DD/MM/YYYY.",
                    "error"
                )

                return redirect(
                    url_for("main.patient_registration")
                )

        else:
            dob = None

        # =================================================
        # DEPARTMENT
        # =================================================

        department_id = request.form.get(
            "department",
            ""
        ).strip()

        department_name = None

        if department_id:

            try:

                department = Department.query.get(
                    int(department_id)
                )

            except (ValueError, TypeError):

                flash(
                    "Invalid department selected.",
                    "error"
                )

                return redirect(
                    url_for("main.patient_registration")
                )

            if not department:

                flash(
                    "Selected department was not found.",
                    "error"
                )

                return redirect(
                    url_for("main.patient_registration")
                )

            # ---------------------------------------------
            # Save Department NAME
            # ---------------------------------------------
            department_name = department.department_name

        # =================================================
        # DOCTOR
        # =================================================

        doctor_id = request.form.get(
            "doctor_id",
            ""
        ).strip()

        doctor_name = None

        if doctor_id:

            try:

                doctor = Doctor.query.get(
                    int(doctor_id)
                )

            except (ValueError, TypeError):

                flash(
                    "Invalid doctor selected.",
                    "error"
                )

                return redirect(
                    url_for("main.patient_registration")
                )

            if not doctor:

                flash(
                    "Selected doctor was not found.",
                    "error"
                )

                return redirect(
                    url_for("main.patient_registration")
                )

            # ---------------------------------------------
            # Save Doctor NAME
            # ---------------------------------------------
            doctor_name = doctor.doc_name

        # =================================================
        # AGE
        # =================================================

        age_input = request.form.get(
            "age",
            ""
        ).strip()

        if age_input:

            try:
                age = int(age_input)

            except (ValueError, TypeError):

                flash(
                    "Invalid age.",
                    "error"
                )

                return redirect(
                    url_for("main.patient_registration")
                )

        else:
            # Empty age is stored as NULL
            age = None

        # =================================================
        # CREATE PATIENT
        # =================================================

        patient = Patient(

            patient_no=patient_no,

            full_name=full_name,

            dob=dob,

            # IMPORTANT:
            # Use processed age value
            age=age,

            gender=request.form.get(
                "gender"
            ),

            phone=request.form.get(
                "phone"
            ),

            address=request.form.get(
                "address"
            ),

            # SAVE DEPARTMENT NAME
            department=department_name,

            # SAVE DOCTOR NAME
            doctor=doctor_name
        )

        # =================================================
        # SAVE
        # =================================================

        db.session.add(patient)

        db.session.commit()

        flash(
            f"Patient registered successfully. Patient No: {patient_no}",
            "success"
        )

        return redirect(
            url_for("main.patient_registration")
        )

    # =================================================
    # GET - LOAD DEPARTMENTS AND DOCTORS
    # =================================================

    departments = Department.query.filter_by(
        status="Active"
    ).order_by(
        Department.department_name.asc()
    ).all()

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
    
    
    
    
# =============================
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

    # ------------------------------------------
    # Find Patient
    # ------------------------------------------

    patient = Patient.query.filter_by(
        patient_no=patient_no
    ).first()

    if not patient:
        return jsonify({
            "error": "Patient not found"
        }), 404

    # ------------------------------------------
    # Department Name
    # ------------------------------------------

    department_name = ""

    if patient.department:

        try:
            department = Department.query.get(
                int(patient.department)
            )

            if department:
                department_name = department.department_name

        except (ValueError, TypeError):

            # If old patient record already contains department name
            department_name = str(patient.department)

    # ------------------------------------------
    # Doctor Name
    # ------------------------------------------

    doctor_name = ""

    if patient.doctor:

        try:
            doctor = Doctor.query.get(
                int(patient.doctor)
            )

            if doctor:
                doctor_name = doctor.doc_name

        except (ValueError, TypeError):

            # If old patient record already contains doctor name
            doctor_name = str(patient.doctor)

    # ------------------------------------------
    # Return Patient Data
    # ------------------------------------------

    return jsonify({

        "patient_no": patient.patient_no,

        "name": patient.full_name,

        "age": patient.age,

        "gender": patient.gender,

        "department": department_name,

        "doctor": doctor_name

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

    # ------------------------------------------
    # Get Bill
    # ------------------------------------------

    bill = Bill.query.get_or_404(bill_id)

    patient = bill.patient

    # ------------------------------------------
    # Get Department Name
    # ------------------------------------------

    department_name = ""

    if patient.department:

        try:
            department = Department.query.get(
                int(patient.department)
            )

            if department:
                department_name = department.department_name

        except (ValueError, TypeError):

            # If old record already contains department name/code
            department_name = str(patient.department)

    # ------------------------------------------
    # Get Doctor Name
    # ------------------------------------------

    doctor_name = ""

    if patient.doctor:

        try:
            doctor = Doctor.query.get(
                int(patient.doctor)
            )

            if doctor:
                doctor_name = doctor.doc_name

        except (ValueError, TypeError):

            # If old record already contains doctor name/code
            doctor_name = str(patient.doctor)

    # ------------------------------------------
    # Bill Items
    # ------------------------------------------

    items = []

    for item in bill.items:

        gross = item.rate * item.quantity

        net = item.amount

        disc_amt = gross - net

        disc_pct = (
            (disc_amt / gross * 100)
            if gross
            else 0
        )

        items.append({

            "name": item.service_name,

            "code": getattr(
                item,
                "service_code",
                ""
            ),

            "qty": item.quantity,

            "rate": item.rate,

            "total": gross,

            "disc_pct": disc_pct,

            "disc_amt": disc_amt,

            "net_total": net
        })

    # ------------------------------------------
    # Bill Data
    # ------------------------------------------

    bill_data = {

        "hospital_name": "SwasthaCare Hospital",

        "hospital_address": "Kathmandu, Nepal",

        "bill_no": bill.bill_no,

        "patient_no": patient.patient_no,

        "patient_name": patient.full_name,

        "age_gender": (
            f"{patient.age} Yrs / "
            f"{patient.gender}"
        ),

        # IMPORTANT
        # Use names instead of IDs/codes
        "doctor": doctor_name,

        "department": department_name,

        "transaction_date": (
            bill.bill_date.strftime("%Y-%m-%d")
            if bill.bill_date
            else ""
        ),

        "items": items,

        "subtotal": bill.subtotal,

        "discount": bill.discount,

        "total": bill.total,

        "pay_type": bill.pay_type,

        "tender_amt": bill.tender_amt,

        "return_amt": bill.return_amt,

        "remarks": bill.remarks
    }

    # ------------------------------------------
    # Render Bill
    # ------------------------------------------

    return render_template(
        "billing/bill.html",
        bill=bill_data
    )


# =========================================================
# BILL LIST
# =========================================================

@main.route("/bill_details")
def bill_details():

    if "user" not in session:
        return redirect("/")

    bills = Bill.query.order_by(
        Bill.id.desc()
    ).all()

    return render_template(
        "billing/bill_details.html",
        bills=bills
    )










# =========================================================
# BILL DETAIL - SINGLE BILL
# =========================================================
@main.route("/bill_detail/<int:bill_id>")
def bill_detail(bill_id):

    if "user" not in session:
        return redirect("/")

    bill = Bill.query.get_or_404(bill_id)

    patient = bill.patient

    if not patient:
        return "Patient not found", 404


    # =====================================================
    # DEPARTMENT
    # =====================================================

    department_name = ""

    if patient.department:

        try:

            department = Department.query.get(
                int(patient.department)
            )

            if department:
                department_name = department.department_name

        except (ValueError, TypeError):

            department_name = str(
                patient.department
            )


    # =====================================================
    # DOCTOR
    # =====================================================

    doctor_name = ""

    if patient.doctor:

        try:

            doctor = Doctor.query.get(
                int(patient.doctor)
            )

            if doctor:
                doctor_name = doctor.doc_name

        except (ValueError, TypeError):

            doctor_name = str(
                patient.doctor
            )










    # =====================================================
    # BILL ITEMS
    # =====================================================

    items = []

    for item in bill.items:

        qty = int(item.quantity or 1)

        rate = float(item.rate or 0)

        gross = rate * qty

        net = float(item.amount or 0)

        disc_amt = gross - net

        disc_pct = (
            (disc_amt / gross) * 100
            if gross > 0
            else 0
        )

        items.append({

            "name": item.service_name,

            "code": getattr(
                item,
                "service_code",
                ""
            ),

            "qty": qty,

            "rate": rate,

            "total": gross,

            "disc_pct": disc_pct,

            "disc_amt": disc_amt,

            "net_total": net

        })


    # =====================================================
    # BILL DATA
    # =====================================================

    bill_data = {

        "hospital_name":
            "SwasthaCare Hospital",

        "hospital_address":
            "Kathmandu, Nepal",

        "bill_no":
            bill.bill_no,

        "transaction_date":
            bill.bill_date.strftime("%Y-%m-%d")
            if bill.bill_date
            else "",

        "patient_no":
            patient.patient_no,

        "patient_name":
            patient.full_name,

        "age_gender":
            f"{patient.age or 0} Yrs / "
            f"{patient.gender or ''}",

        "doctor":
            doctor_name,

        "department":
            department_name,

        "items":
            items,

        "subtotal":
            float(bill.subtotal or 0),

        "discount":
            float(bill.discount or 0),

        "total":
            float(bill.total or 0),

        "pay_type":
            bill.pay_type or "Cash",

        "tender_amt":
            float(bill.tender_amt or 0),

        "return_amt":
            float(bill.return_amt or 0),

        "remarks":
            bill.remarks or "",

        "patient_type":
            "GEN",

        "status":
            "PAID"
    }


    return render_template(
        "billing/bill_detail.html",
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
# Test Setup
# ==============================

@main.route("/test_setup")
def test_setup():

    tests = Test.query.order_by(
        Test.id.desc()
    ).all()

    return render_template(
        "setup/test_setup.html",
        tests=tests,
        active_page="test_setup"
    )


# ==========================================
# Add Test
# ==========================================

@main.route("/add_test", methods=["GET", "POST"])
def add_test():

    if request.method == "POST":

        test_code = request.form.get(
            "test_code",
            ""
        ).strip()

        test_name = request.form.get(
            "test_name",
            ""
        ).strip()

        price = request.form.get(
            "price",
            ""
        ).strip()

        status = request.form.get(
            "status",
            "Active"
        ).strip()


        # ------------------------------------------
        # Validation
        # ------------------------------------------

        if not test_code:

            flash(
                "Test code is required.",
                "error"
            )

            return render_template(
                "setup/add_test.html"
            )


        if not test_name:

            flash(
                "Test name is required.",
                "error"
            )

            return render_template(
                "setup/add_test.html"
            )


        if not price:

            flash(
                "Test price is required.",
                "error"
            )

            return render_template(
                "setup/add_test.html"
            )


        # ------------------------------------------
        # Validate Price
        # ------------------------------------------

        try:

            price = float(price)

            if price < 0:

                flash(
                    "Test price cannot be negative.",
                    "error"
                )

                return render_template(
                    "setup/add_test.html"
                )

        except ValueError:

            flash(
                "Please enter a valid test price.",
                "error"
            )

            return render_template(
                "setup/add_test.html"
            )


        # ------------------------------------------
        # Check Duplicate Test Code
        # ------------------------------------------

        existing_test = Test.query.filter_by(
            test_code=test_code
        ).first()


        if existing_test:

            flash(
                f"Test code '{test_code}' already exists. "
                "Please use a different test code.",
                "error"
            )

            return render_template(
                "setup/add_test.html"
            )


        # ------------------------------------------
        # Create Test
        # ------------------------------------------

        test = Test(

            test_code=test_code,

            test_name=test_name,

            price=price,

            status=status

        )


        # ------------------------------------------
        # Save
        # ------------------------------------------

        try:

            db.session.add(test)

            db.session.commit()

            flash(
                "Test added successfully.",
                "success"
            )

            return redirect(
                url_for("main.test_setup")
            )


        except Exception as e:

            db.session.rollback()

            print(
                "Error adding test:",
                e
            )

            flash(
                "Unable to add test. Please try again.",
                "error"
            )

            return render_template(
                "setup/add_test.html"
            )


    # ------------------------------------------
    # GET
    # ------------------------------------------

    return render_template(
        "setup/add_test.html"
    )


# ==========================================
# Edit Test
# ==========================================

@main.route(
    "/edit_test/<int:test_id>",
    methods=["GET", "POST"]
)
def edit_test(test_id):

    test = Test.query.get_or_404(
        test_id
    )


    if request.method == "POST":

        test_code = request.form.get(
            "test_code",
            ""
        ).strip()

        test_name = request.form.get(
            "test_name",
            ""
        ).strip()

        price = request.form.get(
            "price",
            ""
        ).strip()

        status = request.form.get(
            "status",
            "Active"
        ).strip()


        # ------------------------------------------
        # Validation
        # ------------------------------------------

        if not test_code:

            flash(
                "Test code is required.",
                "error"
            )

            return render_template(
                "setup/edit_test.html",
                test=test
            )


        if not test_name:

            flash(
                "Test name is required.",
                "error"
            )

            return render_template(
                "setup/edit_test.html",
                test=test
            )


        if not price:

            flash(
                "Test price is required.",
                "error"
            )

            return render_template(
                "setup/edit_test.html",
                test=test
            )


        # ------------------------------------------
        # Validate Price
        # ------------------------------------------

        try:

            price = float(price)

            if price < 0:

                flash(
                    "Test price cannot be negative.",
                    "error"
                )

                return render_template(
                    "setup/edit_test.html",
                    test=test
                )

        except ValueError:

            flash(
                "Please enter a valid test price.",
                "error"
            )

            return render_template(
                "setup/edit_test.html",
                test=test
            )


        # ------------------------------------------
        # Check Duplicate Test Code
        # ------------------------------------------

        existing_test = Test.query.filter(
            Test.test_code == test_code,
            Test.id != test.id
        ).first()


        if existing_test:

            flash(
                f"Test code '{test_code}' already exists.",
                "error"
            )

            return render_template(
                "setup/edit_test.html",
                test=test
            )


        # ------------------------------------------
        # Update Test
        # ------------------------------------------

        test.test_code = test_code

        test.test_name = test_name

        test.price = price

        test.status = status


        # ------------------------------------------
        # Save
        # ------------------------------------------

        try:

            db.session.commit()

            flash(
                "Test updated successfully.",
                "success"
            )

            return redirect(
                url_for("main.test_setup")
            )


        except Exception as e:

            db.session.rollback()

            print(
                "Error updating test:",
                e
            )

            flash(
                "Unable to update test.",
                "error"
            )

            return render_template(
                "setup/edit_test.html",
                test=test
            )


    # ------------------------------------------
    # GET
    # ------------------------------------------

    return render_template(
        "setup/edit_test.html",
        test=test
    )


# ==========================================
# Delete Test
# ==========================================

@main.route(
    "/delete_test/<int:test_id>",
    methods=["POST"]
)
def delete_test(test_id):

    test = Test.query.get_or_404(
        test_id
    )


    try:

        db.session.delete(test)

        db.session.commit()

        flash(
            "Test deleted successfully.",
            "success"
        )


    except Exception as e:

        db.session.rollback()

        print(
            "Error deleting test:",
            e
        )

        flash(
            "Unable to delete test. Please try again.",
            "error"
        )


    return redirect(
        url_for("main.test_setup")
    )

# ==========================================
# Test API - Billing
# ==========================================

@main.route("/api/tests")
def get_tests():

    tests = Test.query.filter_by(
        status="Active"
    ).order_by(
        Test.test_name.asc()
    ).all()

    return jsonify([
        {
            "id": test.id,
            "test_code": test.test_code,
            "test_name": test.test_name,
            "price": float(test.price)
        }
        for test in tests
    ])

# =========================================================
# DEPOSIT PAGE
# =========================================================

@main.route("/deposit")
def deposit():

    if "user" not in session:
        return redirect("/")

    return render_template(
        "billing/deposit.html"
    )
# =========================================================
# SAVE DEPOSIT
# =========================================================

@main.route("/save_deposit", methods=["POST"])
def save_deposit():

    if "user" not in session:
        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 401

    try:

        data = request.get_json() or {}

        patient_no = str(
            data.get("patient_no", "")
        ).strip()

        amount = data.get("amount")

        remarks = str(
            data.get("remarks", "")
        ).strip()

        # ---------------------------------------------
        # Validation
        # ---------------------------------------------

        if not patient_no:
            return jsonify({
                "success": False,
                "message": "Hospital Number is required"
            }), 400

        if amount is None or amount == "":
            return jsonify({
                "success": False,
                "message": "Deposit amount is required"
            }), 400

        try:
            amount = float(amount)

        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "message": "Invalid deposit amount"
            }), 400

        if amount <= 0:
            return jsonify({
                "success": False,
                "message": "Deposit amount must be greater than 0"
            }), 400

        # ---------------------------------------------
        # Find patient
        # ---------------------------------------------

        patient = Patient.query.filter_by(
            patient_no=patient_no
        ).first()

        if not patient:
            return jsonify({
                "success": False,
                "message": "Patient not found"
            }), 404

        # ---------------------------------------------
        # Generate receipt number
        # ---------------------------------------------

        last_deposit = Deposit.query.order_by(
            Deposit.id.desc()
        ).first()

        if last_deposit:
            next_id = last_deposit.id + 1
        else:
            next_id = 1

        receipt_no = f"DEP-{next_id:05d}"

        # ---------------------------------------------
        # Create deposit
        # ---------------------------------------------

        new_deposit = Deposit(
            receipt_no=receipt_no,
            patient_id=patient.id,
            patient_no=patient.patient_no,
            patient_name=patient.full_name,
            amount=amount,
            remarks=remarks
        )

        db.session.add(new_deposit)

        db.session.commit()

        # ---------------------------------------------
        # Calculate current balance
        # ---------------------------------------------

        deposits = Deposit.query.filter_by(
            patient_id=patient.id
        ).all()

        balance = sum(
            float(d.amount or 0)
            for d in deposits
        )

        # ---------------------------------------------
        # Success response
        # ---------------------------------------------

        return jsonify({
            "success": True,
            "message": "Deposit saved successfully",
            "receipt_no": receipt_no,
            "balance": balance
        })

    except Exception as e:

        db.session.rollback()

        print("====================================")
        print("SAVE DEPOSIT ERROR:", repr(e))
        print("====================================")

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

# =========================================================
# FETCH PATIENT FOR DEPOSIT
# =========================================================

@main.route("/fetch_deposit_patient/<patient_no>")
def fetch_deposit_patient(patient_no):

    if "user" not in session:
        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 401

    try:

        patient_no = str(patient_no).strip()

        # -------------------------------------------------
        # FIND PATIENT
        # -------------------------------------------------

        patient = Patient.query.filter_by(
            patient_no=patient_no
        ).first()

        if not patient:

            return jsonify({
                "success": False,
                "message": "Patient not found"
            }), 404


        # -------------------------------------------------
        # DEPARTMENT
        # -------------------------------------------------

        department_name = patient.department or "-"

        try:

            if patient.department:

                department = Department.query.get(
                    int(patient.department)
                )

                if department:
                    department_name = department.department_name

        except (ValueError, TypeError):

            department_name = str(
                patient.department
            )


        # -------------------------------------------------
        # DOCTOR
        # -------------------------------------------------

        doctor_name = patient.doctor or "-"

        try:

            if patient.doctor:

                doctor = Doctor.query.get(
                    int(patient.doctor)
                )

                if doctor:
                    doctor_name = doctor.doc_name

        except (ValueError, TypeError):

            doctor_name = str(
                patient.doctor
            )


        # -------------------------------------------------
        # DEPOSIT HISTORY
        #
        # IMPORTANT:
        # Your SAVE route stores patient_id.
        # Therefore FETCH must also use patient_id.
        # -------------------------------------------------

        deposits = Deposit.query.filter_by(
            patient_id=patient.id
        ).order_by(
            Deposit.id.desc()
        ).all()


        # -------------------------------------------------
        # CURRENT BALANCE
        # -------------------------------------------------

        current_balance = sum(
            float(deposit.amount or 0)
            for deposit in deposits
        )


        # -------------------------------------------------
        # HISTORY
        # -------------------------------------------------

        history = []

        for deposit in deposits:

            deposit_date = ""

            if getattr(
                deposit,
                "deposit_date",
                None
            ):

                deposit_date = deposit.deposit_date.strftime(
                    "%d/%m/%Y %H:%M"
                )

            elif getattr(
                deposit,
                "created_at",
                None
            ):

                deposit_date = deposit.created_at.strftime(
                    "%d/%m/%Y %H:%M"
                )


            history.append({

                "receipt_no":
                    getattr(
                        deposit,
                        "receipt_no",
                        ""
                    ),

                "date":
                    deposit_date,

                "amount":
                    float(
                        deposit.amount or 0
                    ),

                "remarks":
                    getattr(
                        deposit,
                        "remarks",
                        ""
                    )

            })


        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------

        return jsonify({

            "success": True,

            "patient": {

                "id":
                    patient.id,

                "patient_no":
                    patient.patient_no,

                "full_name":
                    patient.full_name,

                "age":
                    patient.age or "",

                "gender":
                    patient.gender or "",

                "department":
                    department_name,

                "doctor":
                    doctor_name

            },

            "current_balance":
                current_balance,

            "history":
                history

        })


    except Exception as e:

        # IMPORTANT:
        # This will show the actual error in terminal
        print(
            "DEPOSIT FETCH ERROR:",
            str(e)
        )

        return jsonify({

            "success": False,

            "message":
                f"Server error: {str(e)}"

        }), 500


# =========================================================
# BILL REFUND PAGE
# =========================================================

@main.route("/refund")
def refund():

    if "user" not in session:
        return redirect("/")

    return render_template(
        "billing/refund.html",
        active_page="refund"
    )


# =========================================================
# FETCH PATIENT FOR REFUND
# =========================================================

@main.route("/fetch_refund_patient/<patient_no>")
def fetch_refund_patient(patient_no):

    if "user" not in session:
        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 401

    try:

        patient_no = str(patient_no).strip()

        # -------------------------------------------------
        # FIND PATIENT
        # -------------------------------------------------

        patient = Patient.query.filter_by(
            patient_no=patient_no
        ).first()

        if not patient:
            return jsonify({
                "success": False,
                "message": "Patient not found"
            }), 404

        # -------------------------------------------------
        # DEPARTMENT
        # -------------------------------------------------

        department_name = "-"

        if patient.department:

            try:

                department = Department.query.get(
                    int(patient.department)
                )

                if department:
                    department_name = department.department_name

            except (ValueError, TypeError):

                department_name = str(
                    patient.department
                )

        # -------------------------------------------------
        # DOCTOR
        # -------------------------------------------------

        doctor_name = "-"

        if patient.doctor:

            try:

                doctor = Doctor.query.get(
                    int(patient.doctor)
                )

                if doctor:
                    doctor_name = doctor.doc_name

            except (ValueError, TypeError):

                doctor_name = str(
                    patient.doctor
                )

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------

        return jsonify({

            "success": True,

            "patient": {

                "id": patient.id,

                "patient_no": patient.patient_no,

                "full_name": patient.full_name,

                "age": patient.age or "",

                "gender": patient.gender or "",

                "department": department_name,

                "doctor": doctor_name

            }

        })

    except Exception as e:

        print("REFUND PATIENT FETCH ERROR:", repr(e))

        return jsonify({

            "success": False,

            "message": f"Server error: {str(e)}"

        }), 500
    
# =========================================================
# FETCH BILLS FOR REFUND
# =========================================================

@main.route("/fetch_refund_bills/<patient_no>")
def fetch_refund_bills(patient_no):

    if "user" not in session:
        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 401

    try:

        patient_no = str(patient_no).strip()

        # -------------------------------------------------
        # FIND PATIENT
        # -------------------------------------------------

        patient = Patient.query.filter_by(
            patient_no=patient_no
        ).first()

        if not patient:

            return jsonify({
                "success": False,
                "message": "Patient not found"
            }), 404

        print("REFUND PATIENT FOUND:", patient.id, patient.patient_no)

        # -------------------------------------------------
        # FIND BILLS
        # -------------------------------------------------

        bills = Bill.query.filter_by(
            patient_id=patient.id
        ).order_by(
            Bill.id.desc()
        ).all()

        print("REFUND BILLS FOUND:", len(bills))

        bill_list = []

        for bill in bills:

            print("--------------------------------")
            print("CHECKING BILL:", bill.bill_no)

            # -------------------------------------------------
            # BILL AMOUNT
            # -------------------------------------------------

            bill_amount = float(
                bill.total or 0
            )

            print("BILL AMOUNT:", bill_amount)

            # -------------------------------------------------
            # PREVIOUS REFUNDS
            # -------------------------------------------------

            print("CHECKING BILL REFUNDS...")

            refunds = BillRefund.query.filter_by(
                patient_id=patient.id,
                bill_no=bill.bill_no
            ).all()

            print(
                "PREVIOUS REFUNDS:",
                len(refunds)
            )

            already_refunded = sum(
                float(
                    refund.refund_amount or 0
                )
                for refund in refunds
            )

            # -------------------------------------------------
            # REFUNDABLE AMOUNT
            # -------------------------------------------------

            refundable_amount = (
                bill_amount -
                already_refunded
            )

            if refundable_amount < 0:
                refundable_amount = 0

            print(
                "REFUNDABLE:",
                refundable_amount
            )

            # -------------------------------------------------
            # SKIP FULLY REFUNDED
            # -------------------------------------------------

            if refundable_amount <= 0:
                continue

            bill_list.append({

                "bill_no":
                    bill.bill_no,

                "bill_amount":
                    bill_amount,

                "already_refunded":
                    already_refunded,

                "refundable_amount":
                    refundable_amount

            })

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------

        return jsonify({

            "success": True,

            "bills":
                bill_list

        })

    except Exception as e:

        db.session.rollback()

        print("====================================")
        print("FETCH REFUND BILLS ERROR")
        print("ERROR TYPE:", type(e).__name__)
        print("ERROR:", repr(e))
        print("====================================")

        return jsonify({

            "success": False,

            "message":
                f"Refund bill error: {str(e)}"

        }), 500

# =========================================================
# SAVE BILL REFUND
# =========================================================

@main.route("/save_refund", methods=["POST"])
def save_refund():

    if "user" not in session:
        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 401

    try:

        data = request.get_json() or {}

        # -------------------------------------------------
        # GET DATA
        # -------------------------------------------------

        patient_no = str(
            data.get("patient_no", "")
        ).strip()

        bill_no = str(
            data.get("bill_no", "")
        ).strip()

        refund_amount = data.get(
            "refund_amount"
        )

        reason = str(
            data.get("reason", "")
        ).strip()

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not patient_no:

            return jsonify({
                "success": False,
                "message":
                    "Hospital Number is required"
            }), 400

        if not bill_no:

            return jsonify({
                "success": False,
                "message":
                    "Bill Number is required"
            }), 400

        if refund_amount is None or refund_amount == "":

            return jsonify({
                "success": False,
                "message":
                    "Refund amount is required"
            }), 400

        if not reason:

            return jsonify({
                "success": False,
                "message":
                    "Refund reason is required"
            }), 400

        # -------------------------------------------------
        # CONVERT REFUND AMOUNT
        # -------------------------------------------------

        try:

            refund_amount = float(
                refund_amount
            )

        except (ValueError, TypeError):

            return jsonify({
                "success": False,
                "message":
                    "Invalid refund amount"
            }), 400

        if refund_amount <= 0:

            return jsonify({
                "success": False,
                "message":
                    "Refund amount must be greater than 0"
            }), 400

        # -------------------------------------------------
        # FIND PATIENT
        # -------------------------------------------------

        patient = Patient.query.filter_by(
            patient_no=patient_no
        ).first()

        if not patient:

            return jsonify({
                "success": False,
                "message":
                    "Patient not found"
            }), 404

        # -------------------------------------------------
        # FIND BILL
        # -------------------------------------------------

        bill = Bill.query.filter_by(
            bill_no=bill_no,
            patient_id=patient.id
        ).first()

        if not bill:

            return jsonify({
                "success": False,
                "message":
                    "Bill not found"
            }), 404

        # -------------------------------------------------
        # BILL AMOUNT
        # -------------------------------------------------

        bill_amount = float(
    bill.total or 0
)

        # -------------------------------------------------
        # PREVIOUS REFUNDS
        # -------------------------------------------------

        previous_refunds = BillRefund.query.filter_by(
            patient_id=patient.id,
            bill_no=bill.bill_no
        ).all()

        already_refunded = sum(
            float(
                refund.refund_amount or 0
            )
            for refund in previous_refunds
        )

        # -------------------------------------------------
        # CALCULATE REFUNDABLE AMOUNT
        # -------------------------------------------------

        refundable_amount = (
            bill_amount -
            already_refunded
        )

        if refundable_amount < 0:
            refundable_amount = 0

        # -------------------------------------------------
        # CHECK REFUND AMOUNT
        # -------------------------------------------------

        if refund_amount > refundable_amount:

            return jsonify({

                "success": False,

                "message":
                    f"Maximum refundable amount is "
                    f"Rs. {refundable_amount:.2f}"

            }), 400

        # -------------------------------------------------
        # GENERATE REFUND NUMBER
        # -------------------------------------------------

        last_refund = BillRefund.query.order_by(
            BillRefund.id.desc()
        ).first()

        if last_refund:

            next_id = last_refund.id + 1

        else:

            next_id = 1

        refund_no = (
            f"REF-{next_id:05d}"
        )

        # -------------------------------------------------
        # CREATE REFUND
        # -------------------------------------------------

        new_refund = BillRefund(

            refund_no=refund_no,

            patient_id=patient.id,

            patient_no=patient.patient_no,

            patient_name=patient.full_name,

            bill_no=bill.bill_no,

            bill_amount=bill_amount,

            refund_amount=refund_amount,

            reason=reason

        )

        # -------------------------------------------------
        # SAVE
        # -------------------------------------------------

        db.session.add(
            new_refund
        )

        db.session.commit()

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------

        return jsonify({

            "success": True,

            "message":
                "Bill refund processed successfully",

            "refund_no":
                refund_no,

            "refund_amount":
                refund_amount,

            "bill_amount":
                bill_amount,

            "remaining_amount":
                refundable_amount -
                refund_amount

        })

    except Exception as e:

        db.session.rollback()

        print(
            "SAVE REFUND ERROR:",
            repr(e)
        )

        return jsonify({

            "success": False,

            "message":
                str(e)

        }), 500


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