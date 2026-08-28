from flask import Blueprint, render_template, request, jsonify, redirect, session
from datetime import datetime

from app.database import db
from app.models import (
    Patient,
    Department,
    Doctor,
    User,
    PatientInfoCorrection
)


# =========================================================
# BLUEPRINT
# =========================================================

patient_correction = Blueprint(
    "patient_correction",
    __name__,
    url_prefix="/patient_correction"
)


# =========================================================
# PATIENT INFORMATION CORRECTION PAGE
# =========================================================

@patient_correction.route(
    "/patient_info_correction",
    methods=["GET"]
)
def patient_info_correction():

    if "user" not in session:
        return redirect("/")

    try:

        departments = (
            Department.query
            .filter_by(status="Active")
            .order_by(
                Department.department_name.asc()
            )
            .all()
        )

        doctors = (
            Doctor.query
            .filter_by(status="Active")
            .order_by(
                Doctor.doc_name.asc()
            )
            .all()
        )

        return render_template(
            "patient/patient_info_correction.html",
            departments=departments,
            doctors=doctors,
            active_page="patient_info_correction"
        )

    except Exception as e:

        print(
            "PATIENT CORRECTION PAGE ERROR:",
            repr(e)
        )

        return (
            "Unable to load Patient Information Correction page.",
            500
        )


# =========================================================
# FETCH PATIENT FOR CORRECTION
# =========================================================

@patient_correction.route(
    "/fetch_patient_for_correction/<patient_no>",
    methods=["GET"]
)
def fetch_patient_for_correction(patient_no):

    if "user" not in session:

        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 401

    try:

        patient_no = str(patient_no).strip()

        if not patient_no:

            return jsonify({
                "success": False,
                "message": "Hospital number is required."
            }), 400


        # -------------------------------------------------
        # FIND PATIENT
        # -------------------------------------------------

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
        # SAFE PATIENT TIMESTAMPS
        # -------------------------------------------------

        created_at = ""

        if hasattr(patient, "created_at"):

            value = getattr(
                patient,
                "created_at",
                None
            )

            if value:

                created_at = value.strftime(
                    "%d/%m/%Y %I:%M %p"
                )


        updated_at = ""

        if hasattr(patient, "updated_at"):

            value = getattr(
                patient,
                "updated_at",
                None
            )

            if value:

                updated_at = value.strftime(
                    "%d/%m/%Y %I:%M %p"
                )


        # -------------------------------------------------
        # PATIENT DATA
        # -------------------------------------------------

        patient_data = {

            "id":
                patient.id,

            "patient_no":
                patient.patient_no,

            "full_name":
                patient.full_name or "",

            "dob":
                (
                    patient.dob.strftime("%Y-%m-%d")
                    if patient.dob
                    else ""
                ),

            "age":
                (
                    patient.age
                    if patient.age is not None
                    else ""
                ),

            "gender":
                patient.gender or "",

            "phone":
                patient.phone or "",

            "address":
                patient.address or "",

            "department":
                patient.department or "",

            "doctor":
                patient.doctor or "",

            "created_at":
                created_at,

            "updated_at":
                updated_at
        }


        print(
            "PATIENT CORRECTION FETCH:",
            patient_data
        )


        return jsonify({

            "success": True,

            "patient":
                patient_data

        }), 200


    except Exception as e:

        print(
            "FETCH PATIENT CORRECTION ERROR:",
            repr(e)
        )

        return jsonify({

            "success": False,

            "message":
                "Unable to fetch patient information.",

            "error":
                str(e)

        }), 500


# =========================================================
# SAVE PATIENT INFORMATION CORRECTION
# =========================================================

@patient_correction.route(
    "/save_patient_info_correction",
    methods=["POST"]
)
def save_patient_info_correction():

    if "user" not in session:

        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 401


    try:

        data = request.get_json(
            silent=True
        ) or {}


        patient_id = data.get(
            "patient_id"
        )

        reason = (
            data.get("reason")
            or ""
        ).strip()


        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not patient_id:

            return jsonify({
                "success": False,
                "message": "Patient ID is required."
            }), 400


        if not reason:

            return jsonify({
                "success": False,
                "message": "Correction reason is required."
            }), 400


        # -------------------------------------------------
        # FIND PATIENT
        # -------------------------------------------------

        patient = (
            Patient.query
            .filter_by(
                id=patient_id
            )
            .first()
        )


        if not patient:

            return jsonify({
                "success": False,
                "message": "Patient not found."
            }), 404


        # -------------------------------------------------
        # EDITABLE FIELDS
        # -------------------------------------------------

        editable_fields = [

            "full_name",
            "dob",
            "age",
            "gender",
            "phone",
            "address",
            "department",
            "doctor"

        ]


        changes = []


        # =================================================
        # PROCESS FIELDS
        # =================================================

        for field in editable_fields:

            if field not in data:
                continue


            new_value = data.get(
                field
            )


            # =================================================
            # DOB
            # =================================================

            if field == "dob":

                if isinstance(
                    new_value,
                    str
                ):

                    new_value = new_value.strip()

                else:

                    new_value = ""


                if new_value:

                    try:

                        parsed_value = datetime.strptime(
                            new_value,
                            "%Y-%m-%d"
                        ).date()

                    except ValueError:

                        return jsonify({
                            "success": False,
                            "message": "Invalid date of birth."
                        }), 400

                else:

                    parsed_value = None


                old_value = (

                    patient.dob.isoformat()

                    if patient.dob

                    else ""

                )


                new_value_string = (

                    parsed_value.isoformat()

                    if parsed_value

                    else ""

                )


                if old_value != new_value_string:

                    changes.append({

                        "field":
                            field,

                        "old":
                            old_value,

                        "new":
                            new_value_string

                    })


                    patient.dob = parsed_value


                continue


            # =================================================
            # AGE
            # =================================================

            if field == "age":

                if (
                    new_value is None
                    or new_value == ""
                ):

                    parsed_value = None

                else:

                    try:

                        parsed_value = int(
                            new_value
                        )

                    except (
                        ValueError,
                        TypeError
                    ):

                        return jsonify({

                            "success": False,

                            "message":
                                "Invalid age."

                        }), 400


                    if (
                        parsed_value < 0
                        or parsed_value > 150
                    ):

                        return jsonify({

                            "success": False,

                            "message":
                                "Age must be between 0 and 150."

                        }), 400


                old_value = (

                    str(patient.age)

                    if patient.age is not None

                    else ""

                )


                new_value_string = (

                    str(parsed_value)

                    if parsed_value is not None

                    else ""

                )


                if old_value != new_value_string:

                    changes.append({

                        "field":
                            field,

                        "old":
                            old_value,

                        "new":
                            new_value_string

                    })


                    patient.age = parsed_value


                continue


            # =================================================
            # NORMAL FIELDS
            # =================================================

            if new_value is None:

                new_value = ""


            new_value = str(
                new_value
            ).strip()


            old_value = getattr(
                patient,
                field,
                ""
            )


            if old_value is None:

                old_value = ""


            old_value = str(
                old_value
            ).strip()


            if old_value != new_value:

                changes.append({

                    "field":
                        field,

                    "old":
                        old_value,

                    "new":
                        new_value

                })


                setattr(
                    patient,
                    field,
                    new_value
                )


        # =================================================
        # NO CHANGES
        # =================================================

        if not changes:

            return jsonify({

                "success": False,

                "message":
                    "No changes were detected."

            }), 400


        # =================================================
        # LOGGED-IN USER
        # =================================================

        user_id = session.get(
            "user_id"
        )


        if not user_id:

            username = session.get(
                "user"
            )


            if username:

                user = (
                    User.query
                    .filter_by(
                        username=username
                    )
                    .first()
                )


                if user:

                    user_id = user.id


        # =================================================
        # CREATE AUDIT HISTORY
        # =================================================

        correction_time = datetime.utcnow()


        for change in changes:

            correction = PatientInfoCorrection(

                patient_id=
                    patient.id,

                patient_no=
                    patient.patient_no,

                field_name=
                    change["field"],

                old_value=
                    change["old"],

                new_value=
                    change["new"],

                reason=
                    reason,

                corrected_by=
                    user_id,

                created_at=
                    correction_time

            )


            db.session.add(
                correction
            )


        # =================================================
        # SAVE
        # =================================================

        db.session.commit()


        return jsonify({

            "success":
                True,

            "message":
                "Patient information corrected successfully.",

            "patient_no":
                patient.patient_no,

            "changes":
                len(changes)

        }), 200


    except Exception as e:

        db.session.rollback()


        print(
            "SAVE PATIENT CORRECTION ERROR:",
            repr(e)
        )


        return jsonify({

            "success":
                False,

            "message":
                "Unable to save patient correction.",

            "error":
                str(e)

        }), 500


# =========================================================
# CORRECTION HISTORY
# =========================================================

@patient_correction.route(
    "/patient_correction_history/<patient_no>",
    methods=["GET"]
)
def patient_correction_history(patient_no):

    if "user" not in session:

        return jsonify({

            "success":
                False,

            "message":
                "Unauthorized"

        }), 401


    try:

        patient_no = str(
            patient_no
        ).strip()


        corrections = (

            PatientInfoCorrection.query

            .filter_by(
                patient_no=patient_no
            )

            .order_by(
                PatientInfoCorrection.created_at.desc()
            )

            .all()

        )


        history = []


        for correction in corrections:

            username = "System"


            if correction.user:

                username = (

                    getattr(
                        correction.user,
                        "username",
                        None
                    )

                    or

                    getattr(
                        correction.user,
                        "full_name",
                        None
                    )

                    or

                    "System"

                )


            history.append({

                "id":
                    correction.id,

                "field_name":
                    correction.field_name,

                "old_value":
                    correction.old_value or "",

                "new_value":
                    correction.new_value or "",

                "reason":
                    correction.reason or "",

                "corrected_by":
                    username,

                "created_at":
                    (
                        correction.created_at.strftime(
                            "%d/%m/%Y %I:%M %p"
                        )

                        if correction.created_at

                        else ""
                    )

            })


        return jsonify({

            "success":
                True,

            "history":
                history

        }), 200


    except Exception as e:

        print(
            "CORRECTION HISTORY ERROR:",
            repr(e)
        )


        return jsonify({

            "success":
                False,

            "message":
                "Unable to load correction history.",

            "error":
                str(e)

        }), 500

# =========================================================
# FETCH DOCTORS BY DEPARTMENT
# =========================================================

@patient_correction.route(
    "/fetch_doctors",
    methods=["GET"]
)
def fetch_doctors():

    if "user" not in session:
        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 401

    try:

        # -------------------------------------------------
        # GET DEPARTMENT FROM REQUEST
        # -------------------------------------------------

        department_name = (
            request.args.get("department")
            or ""
        ).strip()


        print(
            "FETCH DOCTORS SESSION:",
            dict(session)
        )

        print(
            "FETCH DOCTORS DEPARTMENT:",
            department_name
        )


        # -------------------------------------------------
        # DEPARTMENT REQUIRED
        # -------------------------------------------------

        if not department_name:

            return jsonify({
                "success": True,
                "doctors": []
            }), 200


        # -------------------------------------------------
        # FIND DEPARTMENT
        #
        # Patient stores department NAME.
        # Doctor stores department_id.
        # -------------------------------------------------

        department = (
            Department.query
            .filter(
                db.func.lower(
                    Department.department_name
                ) ==
                department_name.lower()
            )
            .first()
        )


        if not department:

            print(
                "DEPARTMENT NOT FOUND:",
                department_name
            )

            return jsonify({
                "success": True,
                "doctors": []
            }), 200


        print(
            "MATCHED DEPARTMENT:",
            department.id,
            department.department_name
        )


        # -------------------------------------------------
        # GET ONLY DOCTORS FROM THIS DEPARTMENT
        # -------------------------------------------------

        doctors = (
            Doctor.query
            .filter(
                Doctor.department_id ==
                department.id
            )
            .filter(
                db.func.lower(
                    Doctor.status
                ) == "active"
            )
            .order_by(
                Doctor.doc_name.asc()
            )
            .all()
        )


        doctor_list = []


        for doctor in doctors:

            doctor_name = (
                doctor.doc_name
                or ""
            ).strip()


            if not doctor_name:
                continue


            doctor_list.append({

                "id":
                    doctor.id,

                "name":
                    doctor_name

            })


        print(
            "PATIENT CORRECTION DOCTORS:",
            doctor_list
        )


        return jsonify({

            "success":
                True,

            "doctors":
                doctor_list

        }), 200


    except Exception as e:

        print(
            "FETCH DOCTORS ERROR:",
            repr(e)
        )


        return jsonify({

            "success":
                False,

            "message":
                "Unable to load doctors.",

            "error":
                str(e)

        }), 500