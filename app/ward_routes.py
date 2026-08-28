
from flask import Blueprint, render_template, request, jsonify, redirect, session
from datetime import datetime, timedelta

from app.database import db
from app.models import Ward


# =========================================================
# WARD BLUEPRINT
# =========================================================

ward_bp = Blueprint(
    "ward",
    __name__,
    url_prefix="/ward"
)


# =========================================================
# NEPAL TIME
# =========================================================

def nepal_now():
    """
    Return current Nepal local time.
    Nepal = UTC + 5 hours 45 minutes.
    """
    return datetime.utcnow() + timedelta(hours=5, minutes=45)


# =========================================================
# WARD SETUP PAGE
# =========================================================

    
@ward_bp.route("/ward_setup", methods=["GET"])
def ward_setup():

    if "user" not in session:
        return redirect("/")

    print("========================================")
    print("WARD SETUP ROUTE CALLED")
    print("========================================")

    wards = (
        Ward.query
        .order_by(Ward.id.desc())
        .all()
    )

    print("WARD COUNT:", len(wards))

    return render_template(
        "setup/ward_setup.html",
        wards=wards,
        active_page="ward_setup"
    )

# =========================================================
# ADD WARD PAGE
# =========================================================

@ward_bp.route("/add_ward", methods=["GET"])
def add_ward_page():

    # -----------------------------------------------------
    # LOGIN CHECK
    # -----------------------------------------------------

    if "user" not in session:
        return redirect("/")


    try:

        return render_template(
            "setup/add_ward.html",
            active_page="ward_setup"
        )


    except Exception as e:

        print("========================================")
        print("ADD WARD PAGE ERROR")
        print("ERROR:", repr(e))
        print("========================================")

        return (
            f"Add Ward Page Error: {str(e)}",
            500
        )


# =========================================================
# SAVE WARD
# =========================================================

@ward_bp.route("/save", methods=["POST"])
def save_ward():

    # -----------------------------------------------------
    # LOGIN CHECK
    # -----------------------------------------------------

    if "user" not in session:

        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 401


    try:

        # =================================================
        # READ REQUEST DATA
        # =================================================

        data = request.get_json(
            silent=True
        )


        if not data:

            return jsonify({
                "success": False,
                "message": "No ward data received."
            }), 400


        # =================================================
        # GET FORM VALUES
        # =================================================

        ward_code = str(
            data.get("ward_code", "")
        ).strip()


        ward_name = str(
            data.get("ward_name", "")
        ).strip()


        ward_type = str(
            data.get("ward_type", "")
        ).strip()


        floor = str(
            data.get("floor", "")
        ).strip()


        description = str(
            data.get("description", "")
        ).strip()


        status = str(
            data.get("status", "Active")
        ).strip()


        # =================================================
        # VALIDATION
        # =================================================

        if not ward_code:

            return jsonify({
                "success": False,
                "message": "Ward code is required."
            }), 400


        if not ward_name:

            return jsonify({
                "success": False,
                "message": "Ward name is required."
            }), 400


        if not ward_type:

            return jsonify({
                "success": False,
                "message": "Ward type is required."
            }), 400


        # =================================================
        # NORMALIZE STATUS
        # =================================================

        if status not in ["Active", "Inactive"]:
            status = "Active"


        # =================================================
        # CHECK DUPLICATE WARD CODE
        # =================================================

        existing_code = (
            Ward.query
            .filter(
                db.func.lower(
                    Ward.ward_code
                ) == ward_code.lower()
            )
            .first()
        )


        if existing_code:

            return jsonify({
                "success": False,
                "message": "Ward code already exists."
            }), 409


        # =================================================
        # CHECK DUPLICATE WARD NAME
        # =================================================

        existing_name = (
            Ward.query
            .filter(
                db.func.lower(
                    Ward.ward_name
                ) == ward_name.lower()
            )
            .first()
        )


        if existing_name:

            return jsonify({
                "success": False,
                "message": "Ward name already exists."
            }), 409


        # =================================================
        # CURRENT TIME
        # =================================================

        now = nepal_now()


        # =================================================
        # CREATE WARD
        # =================================================

        ward = Ward(
            ward_code=ward_code,
            ward_name=ward_name,
            ward_type=ward_type,
            floor=floor or None,
            description=description or None,
            status=status,
            created_at=now,
            updated_at=now
        )


        # =================================================
        # SAVE DATABASE
        # =================================================

        db.session.add(ward)

        db.session.commit()


        # =================================================
        # SUCCESS RESPONSE
        # =================================================

        print("========================================")
        print("WARD ADDED SUCCESSFULLY")
        print("ID:", ward.id)
        print("CODE:", ward.ward_code)
        print("NAME:", ward.ward_name)
        print("========================================")


        return jsonify({

            "success": True,

            "message": "Ward added successfully.",

            "redirect": "/ward/ward_setup",

            "ward": {

                "id": ward.id,

                "ward_code": ward.ward_code,

                "ward_name": ward.ward_name,

                "ward_type": ward.ward_type,

                "floor": ward.floor or "",

                "description": ward.description or "",

                "status": ward.status,

                "created_at": (
                    ward.created_at.strftime(
                        "%d/%m/%Y %I:%M %p"
                    )
                    if ward.created_at
                    else ""
                ),

                "updated_at": (
                    ward.updated_at.strftime(
                        "%d/%m/%Y %I:%M %p"
                    )
                    if ward.updated_at
                    else ""
                )

            }

        }), 201


    # =====================================================
    # SERVER / DATABASE ERROR
    # =====================================================

    except Exception as e:

        db.session.rollback()


        print("========================================")
        print("SAVE WARD ERROR")
        print("ERROR:", repr(e))
        print("========================================")


        return jsonify({

            "success": False,

            "message": "Unable to add ward.",

            "error": str(e)

        }), 500

