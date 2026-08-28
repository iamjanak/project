from flask import Blueprint, render_template, request, jsonify, redirect, session
from app.models import Patient, Department, Doctor
from app.database import db


patient_report = Blueprint(
    "patient_report",
    __name__,
    url_prefix="/patient_report"
)


# =========================================================
# PATIENT REPORT PAGE
# =========================================================

@patient_report.route("/", methods=["GET"])
def patient_report_page():

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
            "patient/patient_report.html",
            departments=departments,
            doctors=doctors,
            active_page="patient_report"
        )

    except Exception as e:

        print(
            "PATIENT REPORT PAGE ERROR:",
            repr(e)
        )

        return (
            "Unable to load Patient Report page.",
            500
        )


# =========================================================
# FETCH PATIENT REPORT
# =========================================================

@patient_report.route(
    "/fetch",
    methods=["GET"]
)
def fetch_patient_report():

    if "user" not in session:

        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 401

    try:

        patient_no = (
            request.args.get("patient_no")
            or ""
        ).strip()

        patient_name = (
            request.args.get("patient_name")
            or ""
        ).strip()

        phone = (
            request.args.get("phone")
            or ""
        ).strip()

        department = (
            request.args.get("department")
            or ""
        ).strip()

        doctor = (
            request.args.get("doctor")
            or ""
        ).strip()


        query = Patient.query


        # -------------------------------------------------
        # HOSPITAL NUMBER
        # -------------------------------------------------

        if patient_no:

            query = query.filter(
                Patient.patient_no.ilike(
                    f"%{patient_no}%"
                )
            )


        # -------------------------------------------------
        # PATIENT NAME
        # -------------------------------------------------

        if patient_name:

            query = query.filter(
                Patient.full_name.ilike(
                    f"%{patient_name}%"
                )
            )


        # -------------------------------------------------
        # PHONE
        # -------------------------------------------------

        if phone:

            query = query.filter(
                Patient.phone.ilike(
                    f"%{phone}%"
                )
            )


        # -------------------------------------------------
        # DEPARTMENT
        # -------------------------------------------------

        if department:

            query = query.filter(
                db.func.lower(
                    Patient.department
                ) ==
                department.lower()
            )


        # -------------------------------------------------
        # DOCTOR
        # -------------------------------------------------

        if doctor:

            query = query.filter(
                db.func.lower(
                    Patient.doctor
                ) ==
                doctor.lower()
            )


        # -------------------------------------------------
        # ORDER
        # -------------------------------------------------

        query = query.order_by(
            Patient.id.desc()
        )


        patients = query.all()


        patient_list = []


        for patient in patients:

            created_at = ""

            if (
                hasattr(patient, "created_at")
                and patient.created_at
            ):

                created_at = (
                    patient.created_at.strftime(
                        "%d/%m/%Y %I:%M %p"
                    )
                )


            updated_at = ""

            if (
                hasattr(patient, "updated_at")
                and patient.updated_at
            ):

                updated_at = (
                    patient.updated_at.strftime(
                        "%d/%m/%Y %I:%M %p"
                    )
                )


            patient_list.append({

                "id":
                    patient.id,

                "patient_no":
                    patient.patient_no or "",

                "full_name":
                    patient.full_name or "",

                "dob":
                    (
                        patient.dob.strftime(
                            "%d/%m/%Y"
                        )
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

            })


        return jsonify({

            "success":
                True,

            "patients":
                patient_list,

            "total":
                len(patient_list)

        }), 200


    except Exception as e:

        print(
            "FETCH PATIENT REPORT ERROR:",
            repr(e)
        )

        return jsonify({

            "success":
                False,

            "message":
                "Unable to load patient report.",

            "error":
                str(e)

        }), 500