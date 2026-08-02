from .database import db
from datetime import datetime


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