
# =========================================================
# SWASTHACARE - HOSPITAL DASHBOARD
# =========================================================

from datetime import datetime, timedelta, timezone

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    session,
)

from sqlalchemy import func, or_

from .database import db

from .models import (
    Patient,
    Doctor,
    Department,
    FollowUp,
    Admission,
    Bill,
    Deposit,
    BillRefund,
    Ward,
    Room,
    Bed,
)


# =========================================================
# BLUEPRINT
# =========================================================

dashboard_bp = Blueprint(
    "dashboard",
    __name__,
)


# =========================================================
# NEPAL TIME
# =========================================================
# Nepal Standard Time = UTC +05:45
#
# Using timezone() instead of ZoneInfo avoids the
# "Asia/Kathmandu" tzdata error on Windows.
# =========================================================

NEPAL_TZ = timezone(
    timedelta(
        hours=5,
        minutes=45,
    )
)


def nepal_now():
    """
    Return current date and time in Nepal.
    """
    return datetime.now(NEPAL_TZ)


# =========================================================
# HELPER
# =========================================================

def percentage_change(current, previous):
    try:

        current = float(current or 0)
        previous = float(previous or 0)

        if previous == 0:

            if current > 0:
                return 100

            return 0

        return round(
            ((current - previous) / previous) * 100,
            1,
        )

    except (TypeError, ValueError):

        return 0


# =========================================================
# DASHBOARD
# =========================================================

@dashboard_bp.route("/dashboard")
def dashboard():

    # =====================================================
    # SESSION CHECK
    # =====================================================

    if "user" not in session:

        return redirect(
            url_for("main.login")
        )

    # =====================================================
    # CURRENT NEPAL DATE / TIME
    # =====================================================

    now = nepal_now()

    today = now.date()

    tomorrow = today + timedelta(days=1)

    # =====================================================
    # TODAY DATE RANGE
    # =====================================================

    today_start = datetime.combine(
        today,
        datetime.min.time(),
    )

    tomorrow_start = datetime.combine(
        tomorrow,
        datetime.min.time(),
    )

    # =====================================================
    # CURRENT MONTH
    # =====================================================

    month_start = today.replace(
        day=1
    )

    month_start_dt = datetime.combine(
        month_start,
        datetime.min.time(),
    )

    # =====================================================
    # PREVIOUS MONTH
    # =====================================================

    previous_month_end = (
        month_start
        - timedelta(days=1)
    )

    previous_month_start = (
        previous_month_end.replace(
            day=1
        )
    )

    previous_month_start_dt = datetime.combine(
        previous_month_start,
        datetime.min.time(),
    )

    # =====================================================
    # PATIENTS
    # =====================================================

    total_patients = (
        Patient.query.count()
    )

    # =====================================================
    # DOCTORS
    # =====================================================

    total_doctors = (
        Doctor.query.count()
    )

    active_doctors = (
        Doctor.query
        .filter(
            func.lower(
                Doctor.status
            ) == "active"
        )
        .count()
    )

    inactive_doctors = max(
        total_doctors
        - active_doctors,
        0,
    )

    # =====================================================
    # DEPARTMENTS
    # =====================================================

    total_departments = (
        Department.query.count()
    )

    active_departments = (
        Department.query
        .filter(
            func.lower(
                Department.status
            ) == "active"
        )
        .count()
    )

    inactive_departments = max(
        total_departments
        - active_departments,
        0,
    )

    # =====================================================
    # FOLLOW UPS
    # =====================================================

    followups_today = (
        FollowUp.query
        .filter(
            FollowUp.visit_date >= today_start,
            FollowUp.visit_date < tomorrow_start,
        )
        .count()
    )

    followups_this_month = (
        FollowUp.query
        .filter(
            FollowUp.visit_date >= month_start_dt,
            FollowUp.visit_date < tomorrow_start,
        )
        .count()
    )

    followups_previous_month = (
        FollowUp.query
        .filter(
            FollowUp.visit_date >= previous_month_start_dt,
            FollowUp.visit_date < month_start_dt,
        )
        .count()
    )

    followups_change = percentage_change(
        followups_this_month,
        followups_previous_month,
    )

    # =====================================================
    # ADMISSIONS
    # =====================================================

    admissions_today = (
        Admission.query
        .filter(
            Admission.admission_date >= today_start,
            Admission.admission_date < tomorrow_start,
        )
        .count()
    )

    admissions_this_month = (
        Admission.query
        .filter(
            Admission.admission_date >= month_start_dt,
            Admission.admission_date < tomorrow_start,
        )
        .count()
    )

    admissions_previous_month = (
        Admission.query
        .filter(
            Admission.admission_date >= previous_month_start_dt,
            Admission.admission_date < month_start_dt,
        )
        .count()
    )

    admissions_change = percentage_change(
        admissions_this_month,
        admissions_previous_month,
    )

    # =====================================================
    # CURRENT IPD PATIENTS
    # =====================================================

    current_admissions = (
        Admission.query
        .filter(
            func.lower(
                Admission.status
            ) == "admitted"
        )
        .count()
    )

    # =====================================================
    # DISCHARGES TODAY
    # =====================================================

    discharged_today = (
        Admission.query
        .filter(
            Admission.discharge_date >= today_start,
            Admission.discharge_date < tomorrow_start,
        )
        .count()
    )

    # =====================================================
    # BEDS
    # =====================================================

    total_beds = (
        Bed.query.count()
    )

    occupied_beds = (
        Bed.query
        .filter(
            func.lower(
                Bed.status
            ) == "occupied"
        )
        .count()
    )

    available_beds = (
        Bed.query
        .filter(
            func.lower(
                Bed.status
            ) == "available"
        )
        .count()
    )

    other_beds = max(
        total_beds
        - occupied_beds
        - available_beds,
        0,
    )

    if total_beds > 0:

        bed_occupancy = round(
            (
                occupied_beds
                / total_beds
            ) * 100,
            1,
        )

    else:

        bed_occupancy = 0

    # =====================================================
    # WARDS
    # =====================================================

    total_wards = (
        Ward.query.count()
    )

    active_wards = (
        Ward.query
        .filter(
            func.lower(
                Ward.status
            ) == "active"
        )
        .count()
    )

    # =====================================================
    # ROOMS
    # =====================================================

    total_rooms = (
        Room.query.count()
    )

    available_rooms = (
        Room.query
        .filter(
            func.lower(
                Room.status
            ) == "available"
        )
        .count()
    )

    # =====================================================
    # MONTHLY REVENUE
    # =====================================================

    total_revenue = (
        db.session.query(
            func.coalesce(
                func.sum(Bill.total),
                0,
            )
        )
        .filter(
            Bill.bill_date >= month_start_dt,
            Bill.bill_date < tomorrow_start,
        )
        .scalar()
        or 0
    )

    total_revenue = float(
        total_revenue or 0
    )

    # =====================================================
    # PREVIOUS MONTH REVENUE
    # =====================================================

    previous_month_revenue = (
        db.session.query(
            func.coalesce(
                func.sum(Bill.total),
                0,
            )
        )
        .filter(
            Bill.bill_date >= previous_month_start_dt,
            Bill.bill_date < month_start_dt,
        )
        .scalar()
        or 0
    )

    previous_month_revenue = float(
        previous_month_revenue or 0
    )

    revenue_change = percentage_change(
        total_revenue,
        previous_month_revenue,
    )

    # =====================================================
    # TODAY'S BILLING
    # =====================================================

    today_billing = (
        db.session.query(
            func.coalesce(
                func.sum(Bill.total),
                0,
            )
        )
        .filter(
            Bill.bill_date >= today_start,
            Bill.bill_date < tomorrow_start,
        )
        .scalar()
        or 0
    )

    today_billing = float(
        today_billing or 0
    )

    # =====================================================
    # TODAY'S DEPOSIT
    # =====================================================
    #
    # IMPORTANT:
    # Deposit model uses created_at.
    #
    # Do NOT use:
    # Deposit.deposit_date
    #
    # =====================================================

    today_deposit = (
        db.session.query(
            func.coalesce(
                func.sum(Deposit.amount),
                0
            )
        )
        .filter(
            Deposit.deposit_date >= today_start,
            Deposit.deposit_date < tomorrow_start,
        )
        .scalar()
        or 0
    )

    today_deposit = float(
        today_deposit or 0
    )

    # =====================================================
    # TODAY'S REFUND
    # =====================================================

    today_refund = (
        db.session.query(
            func.coalesce(
                func.sum(
                    BillRefund.refund_amount
                ),
                0,
            )
        )
        .filter(
            BillRefund.created_at >= today_start,
            BillRefund.created_at < tomorrow_start,
        )
        .scalar()
        or 0
    )

    today_refund = float(
        today_refund or 0
    )

    # =====================================================
    # NET COLLECTION
    # =====================================================

    net_collection = (
        today_billing
        + today_deposit
        - today_refund
    )

    # =====================================================
    # ADMISSION TREND
    # LAST 14 DAYS
    # =====================================================

    admission_labels = []
    admission_values = []

    for i in range(13, -1, -1):

        day = today - timedelta(
            days=i
        )

        day_start = datetime.combine(
            day,
            datetime.min.time(),
        )

        day_end = (
            day_start
            + timedelta(days=1)
        )

        count = (
            Admission.query
            .filter(
                Admission.admission_date >= day_start,
                Admission.admission_date < day_end,
            )
            .count()
        )

        admission_labels.append(
            day.strftime("%d %b")
        )

        admission_values.append(
            count
        )

    # =====================================================
    # REVENUE TREND
    # LAST 14 DAYS
    # =====================================================

    revenue_labels = []
    revenue_values = []

    for i in range(13, -1, -1):

        day = today - timedelta(
            days=i
        )

        day_start = datetime.combine(
            day,
            datetime.min.time(),
        )

        day_end = (
            day_start
            + timedelta(days=1)
        )

        amount = (
            db.session.query(
                func.coalesce(
                    func.sum(
                        Bill.total
                    ),
                    0,
                )
            )
            .filter(
                Bill.bill_date >= day_start,
                Bill.bill_date < day_end,
            )
            .scalar()
            or 0
        )

        revenue_labels.append(
            day.strftime("%d %b")
        )

        revenue_values.append(
            float(amount or 0)
        )

    # =====================================================
    # ADMISSION STATUS
    # =====================================================

    admitted_count = (
        Admission.query
        .filter(
            func.lower(
                Admission.status
            ) == "admitted"
        )
        .count()
    )

    discharged_count = (
        Admission.query
        .filter(
            func.lower(
                Admission.status
            ) == "discharged"
        )
        .count()
    )

    total_admission_records = (
        Admission.query.count()
    )

    other_admission_status = max(
        total_admission_records
        - admitted_count
        - discharged_count,
        0,
    )

    admission_status_labels = [
        "Admitted",
        "Discharged",
        "Other",
    ]

    admission_status_values = [
        admitted_count,
        discharged_count,
        other_admission_status,
    ]

    # =====================================================
    # DEPARTMENT PATIENT LOAD
    # =====================================================

    department_labels = []
    department_values = []

    departments = (
        Department.query
        .order_by(
            Department.department_name.asc()
        )
        .all()
    )

    for department in departments:

        name = (
            department.department_name
            or ""
        ).strip()

        if not name:
            continue

        count = (
            Patient.query
            .filter(
                Patient.department == name
            )
            .count()
        )

        department_labels.append(
            name
        )

        department_values.append(
            count
        )

    # =====================================================
    # TOP DOCTORS
    # CURRENT MONTH FOLLOW-UP VISITS
    # =====================================================

    top_doctors_raw = (
        db.session.query(
            Doctor.id,
            Doctor.doc_name,
            Doctor.specialization,
            Department.department_name,
            func.count(
                FollowUp.id
            ).label(
                "visit_count"
            ),
        )
        .outerjoin(
            FollowUp,
            FollowUp.doctor_id == Doctor.id,
        )
        .outerjoin(
            Department,
            Doctor.department_id == Department.id,
        )
        .filter(
            or_(
                FollowUp.id.is_(None),
                FollowUp.visit_date >= month_start_dt,
            )
        )
        .group_by(
            Doctor.id,
            Doctor.doc_name,
            Doctor.specialization,
            Department.department_name,
        )
        .order_by(
            func.count(
                FollowUp.id
            ).desc()
        )
        .limit(5)
        .all()
    )

    top_doctors = []

    for doctor in top_doctors_raw:

        top_doctors.append(
            {
                "name": (
                    doctor.doc_name
                    or "-"
                ),

                "specialization": (
                    doctor.specialization
                    or "General"
                ),

                "department": (
                    doctor.department_name
                    or "Unassigned"
                ),

                "visits": (
                    doctor.visit_count
                    or 0
                ),
            }
        )

    # =====================================================
    # RECENT ADMISSIONS
    # =====================================================

    recent_admissions = (
        Admission.query
        .order_by(
            Admission.admission_date.desc()
        )
        .limit(7)
        .all()
    )

    recent_activity = []

    for admission in recent_admissions:

        recent_activity.append(
            {
                "patient_no": (
                    admission.patient_no
                    or "-"
                ),

                "patient_name": (
                    admission.patient_name
                    or "-"
                ),

                "department": (
                    admission.department_name
                    or "-"
                ),

                "ward": (
                    admission.ward_name
                    or "-"
                ),

                "room": (
                    admission.room_name
                    or "-"
                ),

                "bed": (
                    admission.bed_name
                    or "-"
                ),

                "status": (
                    admission.status
                    or "-"
                ),

                "date": (
                    admission.admission_date.strftime(
                        "%d/%m/%Y %I:%M %p"
                    )
                    if admission.admission_date
                    else "-"
                ),
            }
        )

    # =====================================================
    # RECENT BILLING
    # =====================================================

    recent_bills = (
        Bill.query
        .order_by(
            Bill.bill_date.desc()
        )
        .limit(6)
        .all()
    )

    billing_activity = []

    for bill in recent_bills:

        billing_activity.append(
            {
                "bill_no": (
                    bill.bill_no
                    or "-"
                ),

                "patient_name": (
                    bill.patient.full_name
                    if bill.patient
                    else "-"
                ),

                "amount": float(
                    bill.total or 0
                ),

                "pay_type": (
                    bill.pay_type
                    or "-"
                ),

                "date": (
                    bill.bill_date.strftime(
                        "%d/%m/%Y %I:%M %p"
                    )
                    if bill.bill_date
                    else "-"
                ),
            }
        )

    # =====================================================
    # RENDER DASHBOARD
    # =====================================================

    return render_template(

        "dashboard.html",

        # -------------------------------------------------
        # DATE / TIME
        # -------------------------------------------------

        today=today,

        current_time=now,

        # -------------------------------------------------
        # PATIENTS
        # -------------------------------------------------

        total_patients=total_patients,

        # -------------------------------------------------
        # DOCTORS
        # -------------------------------------------------

        total_doctors=total_doctors,

        active_doctors=active_doctors,

        inactive_doctors=inactive_doctors,

        # -------------------------------------------------
        # DEPARTMENTS
        # -------------------------------------------------

        total_departments=total_departments,

        active_departments=active_departments,

        inactive_departments=inactive_departments,

        # -------------------------------------------------
        # FOLLOW UPS
        # -------------------------------------------------

        followups_today=followups_today,

        followups_this_month=followups_this_month,

        followups_change=followups_change,

        # -------------------------------------------------
        # ADMISSIONS
        # -------------------------------------------------

        admissions_today=admissions_today,

        admissions_this_month=admissions_this_month,

        admissions_change=admissions_change,

        current_admissions=current_admissions,

        discharged_today=discharged_today,

        # -------------------------------------------------
        # BEDS
        # -------------------------------------------------

        total_beds=total_beds,

        occupied_beds=occupied_beds,

        available_beds=available_beds,

        other_beds=other_beds,

        bed_occupancy=bed_occupancy,

        # -------------------------------------------------
        # WARDS
        # -------------------------------------------------

        total_wards=total_wards,

        active_wards=active_wards,

        # -------------------------------------------------
        # ROOMS
        # -------------------------------------------------

        total_rooms=total_rooms,

        available_rooms=available_rooms,

        # -------------------------------------------------
        # REVENUE
        # -------------------------------------------------

        total_revenue=total_revenue,

        previous_month_revenue=previous_month_revenue,

        revenue_change=revenue_change,

        today_billing=today_billing,

        today_deposit=today_deposit,

        today_refund=today_refund,

        net_collection=net_collection,

        # -------------------------------------------------
        # CHARTS
        # -------------------------------------------------

        admission_labels=admission_labels,

        admission_values=admission_values,

        revenue_labels=revenue_labels,

        revenue_values=revenue_values,

        admission_status_labels=(
            admission_status_labels
        ),

        admission_status_values=(
            admission_status_values
        ),

        department_labels=department_labels,

        department_values=department_values,

        # -------------------------------------------------
        # TABLES
        # -------------------------------------------------

        top_doctors=top_doctors,

        recent_activity=recent_activity,

        billing_activity=billing_activity,
    )

