from flask import Blueprint, render_template, request, jsonify, redirect, session
from datetime import datetime

from app.database import db
from app.models import Ward


ward_bp = Blueprint(
    "ward",
    __name__,
    url_prefix="/ward"
)


# =========================================================
# WARD SETUP PAGE
# =========================================================

@ward_bp.route("/ward_setup", methods=["GET"])
def ward_setup():

    if "user" not in session:
        return redirect("/")

    try:

        wards = (
            Ward.query
            .order_by(Ward.id.desc())
            .all()
        )

        return render_template(
            "setup/ward_setup.html",
            wards=wards,
            active_page="ward_setup"
        )

    except Exception as e:

        print(
            "WARD SETUP ERROR:",
            repr(e)
        )

        return (
            "Unable to load Ward Setup.",
            500
        )


# =========================================================
# ADD WARD
# =========================================================

@ward_bp.route("/add", methods=["POST"])
def add_ward():

    if "user" not in session:

        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 401

    try:

        data = request.get_json(
            silent=True
        ) or {}

        ward_code = (
            data.get("ward_code")
            or ""
        ).strip()

        ward_name = (
            data.get("ward_name")
            or ""
        ).strip()

        ward_type = (
            data.get("ward_type")
            or ""
        ).strip()

        floor = (
            data.get("floor")
            or ""
        ).strip()

        description = (
            data.get("description")
            or ""
        ).strip()

        status = (
            data.get("status")
            or "Active"
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
        # DUPLICATE WARD CODE
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
            }), 400


        # =================================================
        # DUPLICATE WARD NAME
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
            }), 400


        # =================================================
        # CREATE WARD
        # =================================================

        now = datetime.utcnow()

        ward = Ward(

            ward_code=ward_code,

            ward_name=ward_name,

            ward_type=ward_type,

            floor=floor,

            description=description,

            status=status,

            created_at=now,

            updated_at=now

        )

        db.session.add(ward)

        db.session.commit()


        # =================================================
        # RESPONSE
        # =================================================

        return jsonify({

            "success": True,

            "message":
                "Ward added successfully.",

            "ward": {

                "id":
                    ward.id,

                "ward_code":
                    ward.ward_code,

                "ward_name":
                    ward.ward_name,

                "ward_type":
                    ward.ward_type,

                "floor":
                    ward.floor or "",

                "description":
                    ward.description or "",

                "status":
                    ward.status,

                "created_at":
                    (
                        ward.created_at.strftime(
                            "%d/%m/%Y %I:%M %p"
                        )
                        if ward.created_at
                        else ""
                    ),

                "updated_at":
                    (
                        ward.updated_at.strftime(
                            "%d/%m/%Y %I:%M %p"
                        )
                        if ward.updated_at
                        else ""
                    )

            }

        }), 201


    except Exception as e:

        db.session.rollback()

        print(
            "ADD WARD ERROR:",
            repr(e)
        )

        return jsonify({

            "success": False,

            "message":
                "Unable to add ward.",

            "error":
                str(e)

        }), 500