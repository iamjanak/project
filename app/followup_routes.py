from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    redirect,
    session
)

from datetime import datetime

from app.database import db

from app.models import (
    Patient,
    Department,
    Doctor,
    FollowUp
)


# =========================================================
# FOLLOW-UP BLUEPRINT
# =========================================================

followup_bp = Blueprint(
    "followup",
    __name__
)


# =========================================================
# FOLLOW-UP PAGE
# =========================================================

@followup_bp.route("/followup")
def followup_page():

    if "user" not in session:
        return redirect("/")

    # Fetch active departments
    departments = Department.query.filter_by(
        status="Active"
    ).order_by(
        Department.department_name.asc()
    ).all()

    return render_template(
        "patient/followup.html",
        departments=departments,
        active_page="followup"
    )


# =========================================================
# FETCH PATIENT
# =========================================================

@followup_bp.route("/fetch_followup_patient/<patient_no>")
def fetch_followup_patient(patient_no):

    if "user" not in session:
        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 401

    try:

        patient_no = str(patient_no).strip()

        print(
            "FOLLOW-UP PATIENT SEARCH:",
            patient_no
        )

        # Search patient
        patient = Patient.query.filter(
            Patient.patient_no == patient_no
        ).first()

        print(
            "FOLLOW-UP PATIENT FOUND:",
            patient
        )

        if not patient:
            return jsonify({
                "success": False,
                "message": (
                    f"No patient found with hospital number "
                    f"{patient_no}."
                )
            }), 404

        # -------------------------------------------------
        # PATIENT DEPARTMENT
        # -------------------------------------------------

        department_name = "-"

        if getattr(patient, "department", None):
            department_name = patient.department

        # -------------------------------------------------
        # PATIENT DOCTOR
        # -------------------------------------------------

        doctor_name = "-"

        if getattr(patient, "doctor", None):
            doctor_name = patient.doctor

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------

        return jsonify({

            "success": True,

            "patient": {

                "id": patient.id,

                "patient_no": patient.patient_no,

                "full_name": patient.full_name,

                "age": patient.age,

                "gender": patient.gender,

                "phone": patient.phone,

                "address": patient.address,

                "department": department_name,

                "doctor": doctor_name

            }

        })

    except Exception as e:

        print(
            "FOLLOW-UP PATIENT ERROR:",
            repr(e)
        )

        return jsonify({
            "success": False,
            "message": "Server error while searching patient."
        }), 500


# =========================================================
# FETCH DOCTORS BY DEPARTMENT
# =========================================================

@followup_bp.route(
    "/fetch_followup_doctors/<int:department_id>"
)
def fetch_followup_doctors(department_id):

    if "user" not in session:
        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 401

    try:

        print(
            "FOLLOW-UP DEPARTMENT:",
            department_id
        )

        # Fetch doctors belonging to department
        doctors = Doctor.query.filter(
            Doctor.department_id == department_id
        ).all()

        doctor_list = []

        for doctor in doctors:

            # -------------------------------------------------
            # STATUS
            # -------------------------------------------------

            status = getattr(
                doctor,
                "status",
                "Active"
            )

            if status and str(status).lower() != "active":
                continue

            # -------------------------------------------------
            # DOCTOR NAME
            # -------------------------------------------------

            doctor_name = getattr(
                doctor,
                "doc_name",
                None
            )

            if not doctor_name:
                doctor_name = getattr(
                    doctor,
                    "doctor_name",
                    None
                )

            if not doctor_name:
                doctor_name = "Unknown Doctor"

            # -------------------------------------------------
            # SPECIALIZATION
            # -------------------------------------------------

            specialization = getattr(
                doctor,
                "specialization",
                None
            )

            doctor_list.append({

                "id": doctor.id,

                "doc_name": doctor_name,

                "specialization": specialization or ""

            })

        return jsonify({

            "success": True,

            "doctors": doctor_list

        })

    except Exception as e:

        print(
            "FOLLOW-UP DOCTOR ERROR:",
            repr(e)
        )

        return jsonify({
            "success": False,
            "message": "Unable to load doctors."
        }), 500

# =========================================================
# SAVE FOLLOW-UP
# =========================================================

@followup_bp.route(
    "/save_followup",
    methods=["POST"]
)
def save_followup():

    if "user" not in session:
        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 401

    try:

        print("\n========================================")
        print("SAVE FOLLOW-UP REQUEST")
        print("========================================")

        # -------------------------------------------------
        # GET JSON
        # -------------------------------------------------

        data = request.get_json(silent=True)

        print("REQUEST DATA:", data)

        if not data:
            return jsonify({
                "success": False,
                "message": "No follow-up data received."
            }), 400

        # -------------------------------------------------
        # GET VALUES
        # -------------------------------------------------

        patient_id = data.get("patient_id")
        department_id = data.get("department_id")
        doctor_id = data.get("doctor_id")

        visit_type = (
            data.get("visit_type")
            or "Follow-Up"
        )

        print("PATIENT ID:", patient_id)
        print("DEPARTMENT ID:", department_id)
        print("DOCTOR ID:", doctor_id)

        # -------------------------------------------------
        # VALIDATION
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

        if not doctor_id:
            return jsonify({
                "success": False,
                "message": "Doctor is required."
            }), 400

        # -------------------------------------------------
        # CONVERT IDS
        # -------------------------------------------------

        try:

            patient_id = int(patient_id)
            department_id = int(department_id)
            doctor_id = int(doctor_id)

        except (ValueError, TypeError):

            return jsonify({
                "success": False,
                "message": "Invalid patient, department or doctor ID."
            }), 400

        # -------------------------------------------------
        # FETCH PATIENT
        # -------------------------------------------------

        patient = Patient.query.get(patient_id)

        print("PATIENT:", patient)

        if not patient:

            return jsonify({
                "success": False,
                "message": "Patient not found."
            }), 404

        # -------------------------------------------------
        # FETCH DEPARTMENT
        # -------------------------------------------------

        department = Department.query.get(
            department_id
        )

        print("DEPARTMENT:", department)

        if not department:

            return jsonify({
                "success": False,
                "message": "Department not found."
            }), 404

        # -------------------------------------------------
        # FETCH DOCTOR
        # -------------------------------------------------

        doctor = Doctor.query.get(
            doctor_id
        )

        print("DOCTOR:", doctor)

        if not doctor:

            return jsonify({
                "success": False,
                "message": "Doctor not found."
            }), 404

        # -------------------------------------------------
        # VALIDATE DOCTOR + DEPARTMENT
        # -------------------------------------------------

        if doctor.department_id != department.id:

            return jsonify({
                "success": False,
                "message": (
                    "Selected doctor does not belong "
                    "to the selected department."
                )
            }), 400

        # -------------------------------------------------
        # NEXT FOLLOW-UP DATE
        # -------------------------------------------------

        next_followup_date = None

        next_date_value = (
            data.get("next_followup_date")
        )

        print(
            "NEXT FOLLOW-UP:",
            next_date_value
        )

        if next_date_value:

            try:

                next_followup_date = datetime.fromisoformat(
                    next_date_value
                )

            except ValueError as e:

                print(
                    "DATE ERROR:",
                    repr(e)
                )

                return jsonify({
                    "success": False,
                    "message": (
                        "Invalid next follow-up date."
                    )
                }), 400

        # -------------------------------------------------
        # GENERATE FOLLOW-UP NUMBER
        # -------------------------------------------------

        today = datetime.now().strftime(
            "%Y%m%d"
        )

        last_followup = FollowUp.query.order_by(
            FollowUp.id.desc()
        ).first()

        if last_followup:

            next_id = last_followup.id + 1

        else:

            next_id = 1

        followup_no = (
            f"FU{today}{next_id:04d}"
        )

        print(
            "FOLLOW-UP NUMBER:",
            followup_no
        )

        # -------------------------------------------------
        # CREATE OBJECT
        # -------------------------------------------------

        new_followup = FollowUp(

            followup_no=followup_no,

            patient_id=patient.id,

            patient_no=patient.patient_no,

            patient_name=patient.full_name,

            department_id=department.id,

            doctor_id=doctor.id,

            visit_date=datetime.now(),

            visit_type=visit_type,

            chief_complaint=(
                data.get("chief_complaint")
                or None
            ),

            diagnosis=(
                data.get("diagnosis")
                or None
            ),

            treatment=(
                data.get("treatment")
                or None
            ),

            prescription=(
                data.get("prescription")
                or None
            ),

            notes=(
                data.get("notes")
                or None
            ),

            next_followup_date=next_followup_date,

            status="Active"
        )

        print(
            "FOLLOW-UP OBJECT CREATED:",
            new_followup
        )

        # -------------------------------------------------
        # ADD
        # -------------------------------------------------

        db.session.add(
            new_followup
        )

        print(
            "FOLLOW-UP ADDED TO SESSION"
        )

        # -------------------------------------------------
        # COMMIT
        # -------------------------------------------------

        db.session.commit()

        print(
            "FOLLOW-UP COMMITTED SUCCESSFULLY"
        )

        print(
            "========================================\n"
        )

        return jsonify({

            "success": True,

            "message":
                "Follow-up recorded successfully.",

            "followup_no":
                followup_no

        }), 200

    except Exception as e:

        db.session.rollback()

        import traceback

        print("\n")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("FOLLOW-UP SAVE ERROR")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

        print(
            "ERROR TYPE:",
            type(e).__name__
        )

        print(
            "ERROR:",
            str(e)
        )

        print(
            "REPR:",
            repr(e)
        )

        print(
            "FULL TRACEBACK:"
        )

        traceback.print_exc()

        print(
            "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        )
        print("\n")

        return jsonify({

            "success": False,

            "message":
                f"Follow-up save failed: {str(e)}"

        }), 500
        
        
        
        
# =========================================================
# FETCH FOLLOW-UP HISTORY
# =========================================================

@followup_bp.route(
    "/fetch_followup_history/<patient_no>"
)
def fetch_followup_history(patient_no):

    if "user" not in session:
        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 401

    try:

        patient_no = str(
            patient_no
        ).strip()

        # -------------------------------------------------
        # FETCH HISTORY
        # -------------------------------------------------

        records = FollowUp.query.filter(
            FollowUp.patient_no == patient_no
        ).order_by(
            FollowUp.visit_date.desc()
        ).all()

        history = []

        for item in records:

            # -------------------------------------------------
            # DEPARTMENT
            # -------------------------------------------------

            department_name = "-"

            if getattr(
                item,
                "department_id",
                None
            ):

                department = Department.query.get(
                    item.department_id
                )

                if department:

                    department_name = getattr(
                        department,
                        "department_name",
                        "-"
                    )

            # -------------------------------------------------
            # DOCTOR
            # -------------------------------------------------

            doctor_name = "-"

            if getattr(
                item,
                "doctor_id",
                None
            ):

                doctor = Doctor.query.get(
                    item.doctor_id
                )

                if doctor:

                    doctor_name = (
                        getattr(
                            doctor,
                            "doc_name",
                            None
                        )
                        or
                        getattr(
                            doctor,
                            "doctor_name",
                            None
                        )
                        or
                        "-"
                    )

            # -------------------------------------------------
            # VISIT DATE
            # -------------------------------------------------

            visit_date = "-"

            if getattr(
                item,
                "visit_date",
                None
            ):

                visit_date = item.visit_date.strftime(
                    "%d/%m/%Y %I:%M %p"
                )

            # -------------------------------------------------
            # NEXT FOLLOW-UP
            # -------------------------------------------------

            next_followup = "-"

            if getattr(
                item,
                "next_followup_date",
                None
            ):

                next_followup = (
                    item.next_followup_date.strftime(
                        "%d/%m/%Y %I:%M %p"
                    )
                )

            # -------------------------------------------------
            # HISTORY
            # -------------------------------------------------

            history.append({

                "followup_no": getattr(
                    item,
                    "followup_no",
                    "-"
                ),

                "visit_date": visit_date,

                "department": department_name,

                "doctor": doctor_name,

                "visit_type": getattr(
                    item,
                    "visit_type",
                    "-"
                ),

                "diagnosis": (
                    getattr(
                        item,
                        "diagnosis",
                        None
                    ) or "-"
                ),

                "next_followup_date": next_followup,

                "status": getattr(
                    item,
                    "status",
                    "Active"
                )

            })

        return jsonify({

            "success": True,

            "history": history

        })

    except Exception as e:

        print(
            "FOLLOW-UP HISTORY ERROR:",
            repr(e)
        )

        return jsonify({

            "success": False,

            "message":
                "Unable to load follow-up history."

        }), 500