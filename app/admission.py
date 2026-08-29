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
            next_number = (
                int(last_admission.admission_no[-4:]) + 1
            )

        except (ValueError, TypeError):

            next_number = 1

    else:

        next_number = 1

    return f"{prefix}{next_number:04d}"


# =========================================================
# SERIALIZE ADMISSION
# =========================================================

def serialize_admission(admission):

    return {

        "id": admission.id,

        "admission_no": admission.admission_no,

        "patient_id": admission.patient_id,

        "patient_no": admission.patient_no,

        "patient_name": admission.patient_name,

        "department": admission.department_name,

        "ward": admission.ward_name,

        "room": admission.room_name,

        "bed": admission.bed_name,

        "admission_type": admission.admission_type,

        "admission_date": (
            admission.admission_date.strftime(
                "%d/%m/%Y %I:%M %p"
            )
            if admission.admission_date
            else ""
        ),

        "discharge_date": (
            admission.discharge_date.strftime(
                "%d/%m/%Y %I:%M %p"
            )
            if getattr(
                admission,
                "discharge_date",
                None
            )
            else ""
        ),

        "status": admission.status
    }


# =========================================================
# ADMIT PATIENT PAGE
#
# URL:
# /admission/patient_admission
#
# THIS IS THE PAGE YOU OPEN IN BROWSER.
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
        # ACTIVE DEPARTMENTS
        # -------------------------------------------------

        departments = (
            Department.query
            .filter_by(status="Active")
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
            .filter_by(status="Active")
            .order_by(
                Ward.ward_name.asc()
            )
            .all()
        )

        # -------------------------------------------------
        # AVAILABLE BEDS
        # -------------------------------------------------

        beds = (
            Bed.query
            .filter_by(status="Available")
            .order_by(
                Bed.bed_name.asc()
            )
            .all()
        )

        # -------------------------------------------------
        # CURRENTLY ADMITTED
        # -------------------------------------------------

        admitted_patients = (
            Admission.query
            .filter_by(status="Admitted")
            .order_by(
                Admission.id.desc()
            )
            .all()
        )

        # -------------------------------------------------
        # REGISTERED PATIENTS
        #
        # Keep this only if your admission page
        # still uses patient list.
        # -------------------------------------------------

        patients = (
            Patient.query
            .order_by(
                Patient.id.desc()
            )
            .all()
        )

        return render_template(
            "patient/patient_admission.html",

            patients=patients,

            departments=departments,

            wards=wards,

            beds=beds,

            admitted_patients=admitted_patients,

            active_page="patient_admission"
        )

    except Exception as e:

        print("=" * 60)
        print(
            "PATIENT ADMISSION PAGE ERROR:",
            repr(e)
        )
        print("=" * 60)

        return (
            f"Unable to load Patient Admission. Error: {str(e)}",
            500
        )


# =========================================================
# SEARCH PATIENT
#
# GET:
# /admission/search_patient/20260001
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

                "id": patient.id,

                "patient_no": patient.patient_no,

                "full_name": patient.full_name,

                "dob": (
                    patient.dob.strftime(
                        "%d/%m/%Y"
                    )
                    if patient.dob
                    else ""
                ),

                "age": patient.age,

                "gender": patient.gender,

                "phone": patient.phone,

                "address": patient.address,

                "department": patient.department,

                "doctor": patient.doctor,

                "already_admitted": (
                    True
                    if active_admission
                    else False
                ),

                "admission_no": (
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

            "message": "Unable to search patient.",

            "error": str(e)

        }), 500


# =========================================================
# GET ROOMS BY WARD
#
# GET:
# /admission/rooms/1
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
                    "id": room.id,

                    "room_code": room.room_code,

                    "room_name": room.room_name,

                    "room_type": room.room_type,

                    "floor": room.floor
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

            "message": "Unable to load rooms.",

            "error": str(e)

        }), 500


# =========================================================
# GET AVAILABLE BEDS BY ROOM
#
# GET:
# /admission/beds/1
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
                    "id": bed.id,

                    "bed_code": bed.bed_code,

                    "bed_name": bed.bed_name,

                    "bed_type": bed.bed_type,

                    "bed_price": (
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

            "message": "Unable to load beds.",

            "error": str(e)

        }), 500


# =========================================================
# ADMIT PATIENT API
#
# POST ONLY
#
# DO NOT OPEN THIS URL DIRECTLY:
# http://localhost:5000/admission/admit
#
# JavaScript must POST to this URL.
# =========================================================

@admission_bp.route(
    "/admit",
    methods=["POST"]
)
def admit_patient():

    if "user" not in session:

        return jsonify({

            "success": False,

            "message": "Unauthorized"

        }), 401

    try:

        # -------------------------------------------------
        # SUPPORT JSON REQUEST
        # -------------------------------------------------

        data = request.get_json(
            silent=True
        ) or {}

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

        # -------------------------------------------------
        # REQUIRED VALIDATION
        # -------------------------------------------------

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

        # -------------------------------------------------
        # CONVERT IDS
        # -------------------------------------------------

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

                "message": "Invalid admission information."

            }), 400

        # -------------------------------------------------
        # PATIENT
        # -------------------------------------------------

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

                "message": "Patient not found."

            }), 404

        # -------------------------------------------------
        # CHECK EXISTING ADMISSION
        # -------------------------------------------------

        existing_admission = (
            Admission.query
            .filter(

                Admission.patient_id
                == patient.id,

                Admission.status
                == "Admitted"

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

        # -------------------------------------------------
        # DEPARTMENT
        # -------------------------------------------------

        department = (
            Department.query
            .filter(

                Department.id
                == department_id,

                Department.status
                == "Active"

            )
            .first()
        )

        if not department:

            return jsonify({

                "success": False,

                "message":
                    "Department not found or inactive."

            }), 404

        # -------------------------------------------------
        # WARD
        # -------------------------------------------------

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

        # -------------------------------------------------
        # ROOM
        # -------------------------------------------------

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

        # -------------------------------------------------
        # BED
        # -------------------------------------------------

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

        # -------------------------------------------------
        # GENERATE ADMISSION NUMBER
        # -------------------------------------------------

        admission_no = (
            generate_admission_no()
        )

        now = nepal_now()

        # -------------------------------------------------
        # CREATE ADMISSION
        # -------------------------------------------------

        admission = Admission(

            admission_no=admission_no,

            patient_id=patient.id,

            patient_no=patient.patient_no,

            patient_name=patient.full_name,

            department_id=department.id,

            department_name=
                department.department_name,

            ward_id=ward.id,

            ward_name=ward.ward_name,

            room_id=room.id,

            room_name=room.room_name,

            bed_id=bed.id,

            bed_name=bed.bed_name,

            admission_type=admission_type,

            admission_date=now,

            status="Admitted",

            reason=(
                reason
                if reason
                else None
            ),

            remarks=(
                remarks
                if remarks
                else None
            ),

            created_at=now,

            updated_at=now
        )

        db.session.add(
            admission
        )

        # -------------------------------------------------
        # OCCUPY BED
        # -------------------------------------------------

        bed.status = "Occupied"

        bed.updated_at = now

        # -------------------------------------------------
        # SAVE
        # -------------------------------------------------

        db.session.commit()

        return jsonify({

            "success": True,

            "message":
                "Patient admitted successfully.",

            "admission":
                serialize_admission(
                    admission
                )

        }), 201

    except Exception as e:

        db.session.rollback()

        print("=" * 50)

        print(
            "PATIENT ADMISSION ERROR:",
            repr(e)
        )

        print("=" * 50)

        return jsonify({

            "success": False,

            "message":
                "Unable to admit patient.",

            "error": str(e)

        }), 500


# =========================================================
# PATIENT DISCHARGE PAGE
#
# URL:
# /admission/patient_discharge
# =========================================================

@admission_bp.route(
    "/patient_discharge",
    methods=["GET"]
)
def patient_discharge():

    if "user" not in session:

        return redirect("/")

    try:

        # -------------------------------------------------
        # CURRENTLY ADMITTED
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

        # -------------------------------------------------
        # DISCHARGED PATIENTS
        # -------------------------------------------------

        discharged_patients = (
            Admission.query
            .filter_by(
                status="Discharged"
            )
            .order_by(
                Admission.id.desc()
            )
            .all()
        )

        # -------------------------------------------------
        # DISCHARGED TODAY
        # -------------------------------------------------

        today = nepal_now().date()

        discharged_today = 0

        for admission in discharged_patients:

            if (
                admission.discharge_date
                and
                admission.discharge_date.date()
                == today
            ):

                discharged_today += 1

        # -------------------------------------------------
        # AVAILABLE BEDS
        # -------------------------------------------------

        available_beds_count = (
            Bed.query
            .filter_by(
                status="Available"
            )
            .count()
        )

        return render_template(

            "patient/patient_discharge.html",

            admitted_patients=
                admitted_patients,

            discharged_patients=
                discharged_patients,

            discharged_today=
                discharged_today,

            available_beds_count=
                available_beds_count,

            active_page=
                "patient_discharge"
        )

    except Exception as e:

        print("=" * 50)

        print(
            "PATIENT DISCHARGE PAGE ERROR:",
            repr(e)
        )

        print("=" * 50)

        return (
            f"Unable to load Patient Discharge. Error: {str(e)}",
            500
        )


# =========================================================
# DISCHARGE PATIENT API
# =========================================================

@admission_bp.route(
    "/discharge/<int:admission_id>",
    methods=["POST"]
)
def discharge_patient(admission_id):

    print("🔥 DISCHARGE ROUTE HIT:", admission_id)

    if "user" not in session:
        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 401

    try:

        data = request.get_json(silent=True) or {}

        discharge_reason = (
            data.get("discharge_reason") or ""
        ).strip()

        discharge_summary = (
            data.get("discharge_summary") or ""
        ).strip()

        if not discharge_reason:
            return jsonify({
                "success": False,
                "message": "Discharge reason is required."
            }), 400

        admission = Admission.query.get(admission_id)

        if not admission:
            return jsonify({
                "success": False,
                "message": "Admission record not found."
            }), 404

        if admission.status != "Admitted":
            return jsonify({
                "success": False,
                "message": "This patient is not currently admitted."
            }), 409

        now = nepal_now()

        admission.status = "Discharged"
        admission.discharge_date = now
        admission.discharge_reason = discharge_reason
        admission.discharge_summary = (
            discharge_summary or None
        )
        admission.updated_at = now

        # Free the occupied bed
        bed = Bed.query.get(admission.bed_id)

        if bed:
            bed.status = "Available"
            bed.updated_at = now

        db.session.commit()

        print("✅ PATIENT DISCHARGED:", admission.admission_no)

        return jsonify({
            "success": True,
            "message": "Patient discharged successfully.",
            "admission": serialize_admission(admission)
        }), 200

    except Exception as e:

        db.session.rollback()

        print("=" * 70)
        print("❌ PATIENT DISCHARGE ERROR:", repr(e))
        print("=" * 70)

        return jsonify({
            "success": False,
            "message": "Unable to discharge patient.",
            "error": str(e)
        }), 500