from .database import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# ==============================
# Patient Model
# ==============================

class Patient(db.Model):

    __tablename__ = "patients"


    id = db.Column(
        db.Integer,
        primary_key=True
    )


    patient_no = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )


    full_name = db.Column(
        db.String(100),
        nullable=False
    )


    dob = db.Column(
        db.Date
    )


    age = db.Column(
        db.Integer
    )


    gender = db.Column(
        db.String(10)
    )


    phone = db.Column(
        db.String(15)
    )


    address = db.Column(
        db.Text
    )


    department = db.Column(
        db.String(50)
    )


    doctor = db.Column(
        db.String(50)
    )



# ==============================
# Billing Model
# ==============================

class Bill(db.Model):

    __tablename__ = "bills"


    id = db.Column(
        db.Integer,
        primary_key=True
    )


    bill_no = db.Column(
        db.String(30),
        unique=True,
        nullable=False
    )


    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("patients.id"),
        nullable=False
    )


    bill_date = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


    subtotal = db.Column(
        db.Float,
        default=0
    )


    discount = db.Column(
        db.Float,
        default=0
    )


    total = db.Column(
        db.Float,
        default=0
    )


    # ---- New fields ----

    pay_type = db.Column(
        db.String(20),
        default="Cash"
    )


    tender_amt = db.Column(
        db.Float,
        default=0
    )


    return_amt = db.Column(
        db.Float,
        default=0
    )


    remarks = db.Column(
        db.Text
    )


    patient = db.relationship(
        "Patient",
        backref="bills"
    )



# ==============================
# Bill Item Model
# ==============================

class BillItem(db.Model):

    __tablename__ = "bill_items"


    id = db.Column(
        db.Integer,
        primary_key=True
    )


    bill_id = db.Column(
        db.Integer,
        db.ForeignKey("bills.id"),
        nullable=False
    )


    service_name = db.Column(
        db.String(100),
        nullable=False
    )


    quantity = db.Column(
        db.Integer,
        default=1
    )


    rate = db.Column(
        db.Float,
        nullable=False
    )


    amount = db.Column(
        db.Float,
        nullable=False
    )   


    bill = db.relationship(
        "Bill",
        backref="items"
    )

# ==============================
# Role Model
# ==============================
class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)


# ==============================
# User Model
# ==============================
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column(db.String(100), nullable=False)

    username = db.Column(db.String(50), unique=True, nullable=False)

    password_hash = db.Column(db.String(255), nullable=False)

    email = db.Column(db.String(120))

    status = db.Column(db.String(20), default="Active")

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    role = db.relationship('Role')

    # Password methods
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


print("Models file loaded")

try:
    print(Role)
except:
    print("Role class NOT FOUND")

    # ==============================
# Department Model
# ==============================
class Department(db.Model):
    __tablename__ = "departments"

    id = db.Column(db.Integer, primary_key=True)
    dep_code = db.Column(db.String(50), unique=True, nullable=False)
    department_name = db.Column(db.String(150), nullable=False)
    dep_type = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), nullable=False, default="Active")
class Doctor(db.Model):
    __tablename__ = "doctors"

    id = db.Column(db.Integer, primary_key=True)

    doc_code = db.Column(db.String(50), nullable=False)

    doc_name = db.Column(db.String(100), nullable=False)

    department_id = db.Column(
        db.Integer,
        db.ForeignKey("departments.id"),
        nullable=False
    )

    specialization = db.Column(db.String(100))

    email = db.Column(db.String(100))

    phone = db.Column(db.String(20))

    status = db.Column(
        db.String(20),
        nullable=False,
        default="Active"
    )

    department = db.relationship(
        "Department",
        backref="doctors"
    )