from .database import db
from datetime import datetime
from zoneinfo import ZoneInfo
from werkzeug.security import generate_password_hash, check_password_hash

def nepal_now():
    return datetime.now(ZoneInfo("Asia/Kathmandu"))


# =========================================================
# PATIENT MODEL
# =========================================================

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
        db.Date,
        nullable=True
    )

    age = db.Column(
        db.Integer,
        nullable=True
    )

    gender = db.Column(
        db.String(10),
        nullable=True
    )

    phone = db.Column(
        db.String(15),
        nullable=True
    )

    address = db.Column(
        db.Text,
        nullable=True
    )

    # -----------------------------------------------------
    # STORE DEPARTMENT NAME
    # -----------------------------------------------------

    department = db.Column(
        db.String(150),
        nullable=True
    )

    # -----------------------------------------------------
    # STORE DOCTOR NAME
    # -----------------------------------------------------

    doctor = db.Column(
        db.String(150),
        nullable=True
    )

    # -----------------------------------------------------
    # FOLLOW-UP RELATIONSHIP
    # -----------------------------------------------------

    followups = db.relationship(
        "FollowUp",
        back_populates="patient",
        foreign_keys="FollowUp.patient_id",
        lazy=True
    )


# =========================================================
# BILL MODEL
# =========================================================

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
        default=datetime.utcnow,
        nullable=False
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
        db.Text,
        nullable=True
    )

    patient = db.relationship(
        "Patient",
        backref="bills"
    )


# =========================================================
# BILL ITEM MODEL
# =========================================================

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


# =========================================================
# ROLE MODEL
# =========================================================

class Role(db.Model):

    __tablename__ = "roles"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )


# =========================================================
# USER MODEL
# =========================================================

class User(db.Model):

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    full_name = db.Column(
        db.String(100),
        nullable=False
    )

    username = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        nullable=True
    )

    status = db.Column(
        db.String(20),
        default="Active"
    )

    role_id = db.Column(
        db.Integer,
        db.ForeignKey("roles.id")
    )

    role = db.relationship(
        "Role"
    )

    def set_password(self, password):

        self.password_hash = generate_password_hash(
            password
        )

    def check_password(self, password):

        return check_password_hash(
            self.password_hash,
            password
        )


# =========================================================
# DEPARTMENT MODEL
# =========================================================

class Department(db.Model):

    __tablename__ = "departments"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    dep_code = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    department_name = db.Column(
        db.String(150),
        nullable=False
    )

    dep_type = db.Column(
        db.String(100),
        nullable=True
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="Active"
    )

    # -----------------------------------------------------
    # DOCTORS
    # -----------------------------------------------------

    doctors = db.relationship(
        "Doctor",
        back_populates="department",
        lazy=True
    )

    # -----------------------------------------------------
    # FOLLOW-UPS
    # -----------------------------------------------------

    followups = db.relationship(
        "FollowUp",
        back_populates="department",
        foreign_keys="FollowUp.department_id",
        lazy=True
    )


# =========================================================
# DOCTOR MODEL
# =========================================================

class Doctor(db.Model):

    __tablename__ = "doctors"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    doc_code = db.Column(
        db.String(50),
        nullable=False
    )

    doc_name = db.Column(
        db.String(100),
        nullable=False
    )

    department_id = db.Column(
        db.Integer,
        db.ForeignKey("departments.id"),
        nullable=False
    )

    specialization = db.Column(
        db.String(100),
        nullable=True
    )

    email = db.Column(
        db.String(100),
        nullable=True
    )

    phone = db.Column(
        db.String(20),
        nullable=True
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="Active"
    )

    # -----------------------------------------------------
    # DEPARTMENT
    # -----------------------------------------------------

    department = db.relationship(
        "Department",
        back_populates="doctors"
    )

    # -----------------------------------------------------
    # FOLLOW-UPS
    # -----------------------------------------------------

    followups = db.relationship(
        "FollowUp",
        back_populates="doctor",
        foreign_keys="FollowUp.doctor_id",
        lazy=True
    )


# =========================================================
# TEST MODEL
# =========================================================

class Test(db.Model):

    __tablename__ = "tests"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    test_code = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    test_name = db.Column(
        db.String(150),
        nullable=False
    )

    price = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    status = db.Column(
        db.String(20),
        default="Active"
    )


# =========================================================
# DEPOSIT MODEL
# =========================================================

class Deposit(db.Model):

    __tablename__ = "deposits"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    receipt_no = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )

    patient_id = db.Column(
        db.Integer,
        nullable=False
    )

    patient_no = db.Column(
        db.String(20),
        nullable=True
    )

    patient_name = db.Column(
        db.String(100),
        nullable=True
    )

    amount = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    deposit_date = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    remarks = db.Column(
        db.Text,
        nullable=True
    )


# =========================================================
# BILL REFUND MODEL
# =========================================================

class BillRefund(db.Model):

    __tablename__ = "bill_refunds"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    refund_no = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    patient_id = db.Column(
        db.Integer,
        nullable=False
    )

    patient_no = db.Column(
        db.String(20),
        nullable=False
    )

    patient_name = db.Column(
        db.String(200),
        nullable=False
    )

    bill_no = db.Column(
        db.String(50),
        nullable=False
    )

    bill_amount = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    refund_amount = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    reason = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )


# =========================================================
# FOLLOW-UP MODEL
# =========================================================

class FollowUp(db.Model):

    __tablename__ = "follow_ups"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # -----------------------------------------------------
    # FOLLOW-UP NUMBER
    # -----------------------------------------------------

    followup_no = db.Column(
        db.String(30),
        unique=True,
        nullable=False
    )

    # -----------------------------------------------------
    # PATIENT
    # -----------------------------------------------------

    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("patients.id"),
        nullable=False
    )

    patient_no = db.Column(
        db.String(20),
        nullable=False
    )

    patient_name = db.Column(
        db.String(150),
        nullable=False
    )

    # -----------------------------------------------------
    # DEPARTMENT
    # -----------------------------------------------------

    department_id = db.Column(
        db.Integer,
        db.ForeignKey("departments.id"),
        nullable=False
    )

    # -----------------------------------------------------
    # DOCTOR
    # -----------------------------------------------------

    doctor_id = db.Column(
        db.Integer,
        db.ForeignKey("doctors.id"),
        nullable=False
    )

    # -----------------------------------------------------
    # VISIT INFORMATION
    # -----------------------------------------------------

    visit_date = db.Column(
        db.DateTime,
        nullable=False
    )

    visit_type = db.Column(
        db.String(50),
        nullable=False,
        default="Follow-Up"
    )

    # -----------------------------------------------------
    # CLINICAL INFORMATION
    # -----------------------------------------------------

    chief_complaint = db.Column(
        db.Text,
        nullable=True
    )

    diagnosis = db.Column(
        db.Text,
        nullable=True
    )

    treatment = db.Column(
        db.Text,
        nullable=True
    )

    prescription = db.Column(
        db.Text,
        nullable=True
    )

    notes = db.Column(
        db.Text,
        nullable=True
    )

    # -----------------------------------------------------
    # NEXT FOLLOW-UP
    # -----------------------------------------------------

    next_followup_date = db.Column(
        db.DateTime,
        nullable=True
    )

    # -----------------------------------------------------
    # STATUS
    # -----------------------------------------------------

    status = db.Column(
        db.String(20),
        nullable=False,
        default="Active"
    )

    # -----------------------------------------------------
    # RELATIONSHIPS
    # -----------------------------------------------------

    patient = db.relationship(
        "Patient",
        back_populates="followups",
        foreign_keys=[patient_id]
    )

    department = db.relationship(
        "Department",
        back_populates="followups",
        foreign_keys=[department_id]
    )

    doctor = db.relationship(
        "Doctor",
        back_populates="followups",
        foreign_keys=[doctor_id]
    )

    # -----------------------------------------------------
    # REPRESENTATION
    # -----------------------------------------------------

    def __repr__(self):

        return (
            f"<FollowUp "
            f"{self.followup_no} "
            f"- {self.patient_no}>"
        )
        
# app/models.py

from datetime import datetime
from app.database import db


class PatientInfoCorrection(db.Model):

    
    __tablename__ = "patient_info_corrections"

    id = db.Column(db.Integer, primary_key=True)

    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("patients.id"),
        nullable=False,
        index=True
    )

    patient_no = db.Column(
        db.String(50),
        nullable=False,
        index=True
    )

    field_name = db.Column(
        db.String(100),
        nullable=False
    )

    old_value = db.Column(
        db.Text,
        nullable=True
    )

    new_value = db.Column(
        db.Text,
        nullable=True
    )

    reason = db.Column(
        db.Text,
        nullable=False
    )

    corrected_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    patient = db.relationship(
        "Patient",
        backref=db.backref(
            "info_corrections",
            lazy=True
        )
    )

    user = db.relationship(
        "User",
        foreign_keys=[corrected_by]
    )
    
class Ward(db.Model):

    __tablename__ = "wards"

    # =====================================================
    # PRIMARY KEY
    # =====================================================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # =====================================================
    # WARD CODE
    # =====================================================

    ward_code = db.Column(
        db.String(50),
        nullable=False,
        unique=True
    )

    # =====================================================
    # WARD NAME
    # =====================================================

    ward_name = db.Column(
        db.String(150),
        nullable=False,
        unique=True
    )

    # =====================================================
    # WARD TYPE
    # =====================================================

    ward_type = db.Column(
        db.String(100),
        nullable=False
    )

    # =====================================================
    # FLOOR
    # =====================================================

    floor = db.Column(
        db.String(50),
        nullable=True
    )

    # =====================================================
    # DESCRIPTION
    # =====================================================

    description = db.Column(
        db.Text,
        nullable=True
    )

    # =====================================================
    # STATUS
    # =====================================================

    status = db.Column(
        db.String(20),
        nullable=False,
        default="Active"
    )

    # =====================================================
    # CREATED DATE/TIME
    # =====================================================

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    # =====================================================
    # UPDATED DATE/TIME
    # =====================================================

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
class Room(db.Model):

    __tablename__ = "rooms"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    ward_id = db.Column(
        db.Integer,
        db.ForeignKey("wards.id"),
        nullable=False
    )

    room_code = db.Column(
        db.String(50),
        nullable=False,
        unique=True
    )

    room_number = db.Column(
        db.String(50),
        nullable=False
    )

    room_name = db.Column(
        db.String(150),
        nullable=False
    )

    room_type = db.Column(
        db.String(100),
        nullable=False
    )

    floor = db.Column(
        db.String(50)
    )

    capacity = db.Column(
        db.Integer,
        nullable=False,
        default=1
    )

    description = db.Column(
        db.Text
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="Available"
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    ward = db.relationship(
        "Ward",
        backref=db.backref(
            "rooms",
            lazy=True
        )
    )
    
class Bed(db.Model):
    __tablename__ = "beds"

    id = db.Column(db.Integer, primary_key=True)

    bed_code = db.Column(
        db.String(50),
        nullable=False,
        unique=True
    )

    bed_name = db.Column(
        db.String(100),
        nullable=False
    )

    room_id = db.Column(
        db.Integer,
        db.ForeignKey("rooms.id"),
        nullable=False
    )

    bed_type = db.Column(
        db.String(50),
        nullable=False
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="Available"
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    room = db.relationship(
        "Room",
        backref=db.backref(
            "beds",
            lazy=True
        )
    )

    bed_price = db.Column(
        db.Numeric(10, 2),
        nullable=True
    )
    
    
# =========================================================
# PATIENT ADMISSION / IPD
# =========================================================
class Admission(db.Model):

    __tablename__ = "admissions"

    id = db.Column(db.Integer, primary_key=True)

    admission_no = db.Column(
        db.String(30),
        unique=True,
        nullable=False
    )

    patient_id = db.Column(
        db.Integer,
        nullable=False
    )

    patient_no = db.Column(
        db.String(30),
        nullable=False
    )

    patient_name = db.Column(
        db.String(150),
        nullable=False
    )

    department_id = db.Column(
        db.Integer,
        nullable=False
    )

    department_name = db.Column(
        db.String(150)
    )

    ward_id = db.Column(
        db.Integer,
        nullable=False
    )

    ward_name = db.Column(
        db.String(150)
    )

    room_id = db.Column(
        db.Integer,
        nullable=False
    )

    room_name = db.Column(
        db.String(150)
    )

    bed_id = db.Column(
        db.Integer,
        nullable=False
    )

    bed_name = db.Column(
        db.String(150)
    )

    admission_type = db.Column(
        db.String(50),
        default="IPD"
    )

    admission_date = db.Column(
        db.DateTime,
        nullable=False
    )

    discharge_date = db.Column(
        db.DateTime,
        nullable=True
    )

    status = db.Column(
        db.String(30),
        default="Admitted"
    )

    reason = db.Column(
        db.Text,
        nullable=True
    )

    remarks = db.Column(
        db.Text,
        nullable=True
    )

    discharge_reason = db.Column(
        db.Text,
        nullable=True
    )

    discharge_summary = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False
    )

