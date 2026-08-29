from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    redirect,
    session
)

from datetime import datetime, timedelta

from app.database import db
from app.models import (
    Patient,
    Department,
    Ward,
    Room,
    Bed,
    Admission
)


# =========================================================
# BLUEPRINT
# =========================================================

admission_bp = Blueprint(
    "admission",
    __name__,
    url_prefix="/admission"
)


# =========================================================
# NEPAL TIME
# =========================================================

def nepal_now():
    return datetime.utcnow() + timedelta(hours=5, minutes=45)


# =========================================================
# GENERATE ADMISSION NUMBER
# Example:
# IPD202608290001
# =========================================================

def generate_admission_no():

    today = nepal_now().strftime("%Y%m%d")

    prefix = f"IPD{today}"

    last_admission = (
        Admission.query
        .filter(
            Admission.admission_no.like(f"{prefix}%")
        )
        .order_by(
            Admission.id.desc()
        )
        .first()
    )

    if last_admission:

        try:

            last_number = int(
                last_admission.admission_no[-4:]
            )

            next_number = last_number + 1

        except (ValueError, TypeError):

            next_number = 1

    else:

        next_number = 1

    return f"{prefix}{next_number:04d}"


# =========================================================
# PATIENT ADMISSION PAGE
# =========================================================

@admission_bp.route(
    "/patient_admission",
    methods=["GET"]
)
def patient_admission():

    if "user" not in session:

        return redirect("/")

    try:

        # -------------------------------------------------
        # PATIENT LIST
        # -------------------------------------------------

        patients = (
            Patient.query
            .order_by(
                Patient.id.desc()
            )
            .all()
        )


        # -------------------------------------------------
        # ACTIVE DEPARTMENTS
        # -------------------------------------------------

        departments = (
            Department.query
            .filter_by(
                status="Active"
            )
            .order_by(
                Department.department_name.asc()
            )
            .all()
        )


        # -------------------------------------------------
        # ACTIVE WARDS
        # -------------------------------------------------

        wards = (
            Ward.query
            .filter_by(
                status="Active"
            )
            .order_by(
                Ward.ward_name.asc()
            )
            .all()
        )


        # -------------------------------------------------
        # ACTIVE ROOMS
        # -------------------------------------------------

        rooms = (
            Room.query
            .filter_by(
                status="Active"
            )
            .order_by(
                Room.room_name.asc()
            )
            .all()
        )


        # -------------------------------------------------
        # AVAILABLE BEDS
        # -------------------------------------------------

        beds = (
            Bed.query
            .filter_by(
                status="Available"
            )
            .order_by(
                Bed.bed_name.asc()
            )
            .all()
        )


        # -------------------------------------------------
        # CURRENTLY ADMITTED PATIENTS
        # -------------------------------------------------

        admitted_patients = (
            Admission.query
            .filter_by(
                status="Admitted"
            )
            .order_by(
                Admission.id.desc()
            )
            .all()
        )


        return render_template(

            "patient/patient_admission.html",

            patients=patients,

            departments=departments,

            wards=wards,

            rooms=rooms,

            beds=beds,

            admitted_patients=admitted_patients,

            active_page="patient_admission"

        )


    except Exception as e:

        print(
            "========================================"
        )

        print(
            "PATIENT ADMISSION PAGE ERROR:",
            repr(e)
        )

        print(
            "========================================"
        )

        return (
            "Unable to load Patient Admission.",
            500
        )


# =========================================================
# SEARCH PATIENT
# =========================================================

@admission_bp.route(
    "/search_patient/<patient_no>",
    methods=["GET"]
)
def search_patient(patient_no):

    if "user" not in session:

        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 401


    try:

        patient_no = str(
            patient_no
        ).strip()


        if not patient_no:

            return jsonify({
                "success": False,
                "message": "Hospital number is required."
            }), 400


        patient = (
            Patient.query
            .filter_by(
                patient_no=patient_no
            )
            .first()
        )


        if not patient:

            return jsonify({
                "success": False,
                "message": "Patient not found."
            }), 404


        # -------------------------------------------------
        # CHECK ACTIVE ADMISSION
        # -------------------------------------------------

        active_admission = (
            Admission.query
            .filter(
                Admission.patient_id == patient.id,
                Admission.status == "Admitted"
            )
            .first()
        )


        return jsonify({

            "success": True,

            "patient": {

                "id":
                    patient.id,

                "patient_no":
                    patient.patient_no,

                "full_name":
                    patient.full_name,

                "dob":
                    (
                        patient.dob.strftime(
                            "%d/%m/%Y"
                        )
                        if patient.dob
                        else ""
                    ),

                "age":
                    patient.age,

                "gender":
                    patient.gender,

                "phone":
                    patient.phone,

                "address":
                    patient.address,

                "department":
                    patient.department,

                "doctor":
                    patient.doctor,

                "already_admitted":
                    True if active_admission else False,

                "admission_no":
                    (
                        active_admission.admission_no
                        if active_admission
                        else ""
                    )
            }

        })


    except Exception as e:

        print(
            "SEARCH PATIENT ERROR:",
            repr(e)
        )

        return jsonify({

            "success": False,

            "message":
                "Unable to search patient.",

            "error":
                str(e)

        }), 500


# =========================================================
# GET ROOMS BY WARD
# =========================================================

@admission_bp.route(
    "/rooms/<int:ward_id>",
    methods=["GET"]
)
def get_rooms_by_ward(ward_id):

    if "user" not in session:

        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 401


    try:

        rooms = (
            Room.query
            .filter(
                Room.ward_id == ward_id,
                Room.status == "Active"
            )
            .order_by(
                Room.room_name.asc()
            )
            .all()
        )


        return jsonify({

            "success": True,

            "rooms": [

                {

                    "id":
                        room.id,

                    "room_code":
                        room.room_code,

                    "room_name":
                        room.room_name,

                    "room_type":
                        room.room_type,

                    "floor":
                        room.floor

                }

                for room in rooms

            ]

        })


    except Exception as e:

        print(
            "ADMISSION ROOM ERROR:",
            repr(e)
        )

        return jsonify({

            "success": False,

            "message":
                "Unable to load rooms."

        }), 500


# =========================================================
# GET AVAILABLE BEDS BY ROOM
# =========================================================

@admission_bp.route(
    "/beds/<int:room_id>",
    methods=["GET"]
)
def get_beds_by_room(room_id):

    if "user" not in session:

        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 401


    try:

        beds = (
            Bed.query
            .filter(
                Bed.room_id == room_id,
                Bed.status == "Available"
            )
            .order_by(
                Bed.bed_name.asc()
            )
            .all()
        )


        return jsonify({

            "success": True,

            "beds": [

                {

                    "id":
                        bed.id,

                    "bed_code":
                        bed.bed_code,

                    "bed_name":
                        bed.bed_name,

                    "bed_type":
                        bed.bed_type,

                    "bed_price":
                        (
                            float(bed.bed_price)
                            if bed.bed_price is not None
                            else None
                        )

                }

                for bed in beds

            ]

        })


    except Exception as e:

        print(
            "ADMISSION BED ERROR:",
            repr(e)
        )

        return jsonify({

            "success": False,

            "message":
                "Unable to load beds."

        }), 500


# =========================================================
# ADMIT PATIENT
# =========================================================

@admission_bp.route(
    "/admit",
    methods=["POST"]
)
def admit_patient():

    if "user" not in session:

        return jsonify({

            "success": False,

            "message":
                "Unauthorized"

        }), 401


    try:

        data = request.get_json(
            silent=True
        ) or {}


        # =================================================
        # GET DATA
        # =================================================

        patient_id = data.get(
            "patient_id"
        )

        department_id = data.get(
            "department_id"
        )

        ward_id = data.get(
            "ward_id"
        )

        room_id = data.get(
            "room_id"
        )

        bed_id = data.get(
            "bed_id"
        )

        admission_type = (
            data.get(
                "admission_type"
            )
            or "IPD"
        ).strip()

        reason = (
            data.get(
                "reason"
            )
            or ""
        ).strip()

        remarks = (
            data.get(
                "remarks"
            )
            or ""
        ).strip()


        # =================================================
        # VALIDATION
        # =================================================

        if not patient_id:

            return jsonify({
                "success": False,
                "message": "Patient is required."
            }), 400


        if not department_id:

            return jsonify({
                "success": False,
                "message": "Department is required."
            }), 400


        if not ward_id:

            return jsonify({
                "success": False,
                "message": "Ward is required."
            }), 400


        if not room_id:

            return jsonify({
                "success": False,
                "message": "Room is required."
            }), 400


        if not bed_id:

            return jsonify({
                "success": False,
                "message": "Bed is required."
            }), 400


        # =================================================
        # CONVERT IDS
        # =================================================

        try:

            patient_id = int(
                patient_id
            )

            department_id = int(
                department_id
            )

            ward_id = int(
                ward_id
            )

            room_id = int(
                room_id
            )

            bed_id = int(
                bed_id
            )

        except (
            ValueError,
            TypeError
        ):

            return jsonify({

                "success": False,

                "message":
                    "Invalid admission information."

            }), 400


        # =================================================
        # GET PATIENT
        # =================================================

        patient = (
            Patient.query
            .filter(
                Patient.id == patient_id
            )
            .first()
        )


        if not patient:

            return jsonify({

                "success": False,

                "message":
                    "Patient not found."

            }), 404


        # =================================================
        # CHECK EXISTING ACTIVE ADMISSION
        # =================================================

        existing_admission = (
            Admission.query
            .filter(
                Admission.patient_id == patient.id,
                Admission.status == "Admitted"
            )
            .first()
        )


        if existing_admission:

            return jsonify({

                "success": False,

                "message":
                    "This patient is already admitted.",

                "admission_no":
                    existing_admission.admission_no

            }), 409


        # =================================================
        # DEPARTMENT
        # =================================================

        department = (
            Department.query
            .filter(
                Department.id == department_id,
                Department.status == "Active"
            )
            .first()
        )


        if not department:

            return jsonify({

                "success": False,

                "message":
                    "Department not found or inactive."

            }), 404


        # =================================================
        # WARD
        # =================================================

        ward = (
            Ward.query
            .filter(
                Ward.id == ward_id,
                Ward.status == "Active"
            )
            .first()
        )


        if not ward:

            return jsonify({

                "success": False,

                "message":
                    "Ward not found or inactive."

            }), 404


        # =================================================
        # ROOM
        # =================================================

        room = (
            Room.query
            .filter(
                Room.id == room_id,
                Room.ward_id == ward_id,
                Room.status == "Active"
            )
            .first()
        )


        if not room:

            return jsonify({

                "success": False,

                "message":
                    "Selected room is invalid."

            }), 404


        # =================================================
        # BED
        # =================================================

        bed = (
            Bed.query
            .filter(
                Bed.id == bed_id,
                Bed.room_id == room_id,
                Bed.status == "Available"
            )
            .first()
        )


        if not bed:

            return jsonify({

                "success": False,

                "message":
                    "Selected bed is not available."

            }), 409


        # =================================================
        # GENERATE ADMISSION NUMBER
        # =================================================

        admission_no = (
            generate_admission_no()
        )


        # =================================================
        # TIME
        # =================================================

        now = nepal_now()


        # =================================================
        # CREATE ADMISSION
        # =================================================

        admission = Admission(

            admission_no=
                admission_no,

            patient_id=
                patient.id,

            patient_no=
                patient.patient_no,

            patient_name=
                patient.full_name,

            department_id=
                department.id,

            department_name=
                department.department_name,

            ward_id=
                ward.id,

            ward_name=
                ward.ward_name,

            room_id=
                room.id,

            room_name=
                room.room_name,

            bed_id=
                bed.id,

            bed_name=
                bed.bed_name,

            admission_type=
                admission_type,

            admission_date=
                now,

            status=
                "Admitted",

            reason=
                reason or None,

            remarks=
                remarks or None,

            created_at=
                now,

            updated_at=
                now

        )


        # =================================================
        # ADD ADMISSION
        # =================================================

        db.session.add(
            admission
        )


        # =================================================
        # UPDATE BED STATUS
        # =================================================

        bed.status = "Occupied"

        bed.updated_at = now


        # =================================================
        # COMMIT
        # =================================================

        db.session.commit()


        # =================================================
        # RESPONSE
        # =================================================

        return jsonify({

            "success": True,

            "message":
                "Patient admitted successfully.",

            "admission": {

                "id":
                    admission.id,

                "admission_no":
                    admission.admission_no,

                "patient_id":
                    admission.patient_id,

                "patient_no":
                    admission.patient_no,

                "patient_name":
                    admission.patient_name,

                "department":
                    admission.department_name,

                "ward":
                    admission.ward_name,

                "room":
                    admission.room_name,

                "bed":
                    admission.bed_name,

                "admission_type":
                    admission.admission_type,

                "status":
                    admission.status,

                "admission_date":
                    (
                        admission.admission_date.strftime(
                            "%d/%m/%Y %I:%M %p"
                        )
                        if admission.admission_date
                        else ""
                    )

            }

        }), 201


    except Exception as e:

        db.session.rollback()


        print(
            "========================================"
        )

        print(
            "PATIENT ADMISSION ERROR:",
            repr(e)
        )

        print(
            "========================================"
        )


        return jsonify({

            "success": False,

            "message":
                "Unable to admit patient.",

            "error":
                str(e)

        }), 500