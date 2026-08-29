from flask import Blueprint, render_template, request, jsonify, redirect, session
from datetime import datetime, timedelta

from app.database import db
from app.models import Bed, Room


# =========================================================
# NEPAL TIME
# =========================================================

def nepal_now():
    return datetime.utcnow() + timedelta(hours=5, minutes=45)


# =========================================================
# BLUEPRINT
# =========================================================

bed_bp = Blueprint(
    "bed",
    __name__,
    url_prefix="/bed"
)


# =========================================================
# BED SETUP PAGE
# =========================================================

@bed_bp.route("/bed_setup", methods=["GET"])
def bed_setup():

    if "user" not in session:

        return redirect("/")


    try:

        # -------------------------------------------------
        # GET ROOMS
        # -------------------------------------------------

        rooms = (
            Room.query
            .order_by(Room.id.desc())
            .all()
        )


        # -------------------------------------------------
        # GET BEDS
        # -------------------------------------------------

        beds = (
            Bed.query
            .order_by(Bed.id.desc())
            .all()
        )


        return render_template(
            "setup/bed_setup.html",
            rooms=rooms,
            beds=beds,
            active_page="bed_setup"
        )


    except Exception as e:

        print("========================================")
        print("BED SETUP ERROR:", repr(e))
        print("========================================")

        return (
            "Unable to load Bed Setup.",
            500
        )


# =========================================================
# ADD BED PAGE
# =========================================================

@bed_bp.route("/add", methods=["GET"])
def add_bed_page():

    if "user" not in session:

        return redirect("/")


    try:

        # -------------------------------------------------
        # ONLY ACTIVE ROOMS
        # -------------------------------------------------

        rooms = (
            Room.query
            .filter_by(status="Active")
            .order_by(Room.room_name.asc())
            .all()
        )


        return render_template(
            "setup/add_bed.html",
            rooms=rooms,
            active_page="bed_setup"
        )


    except Exception as e:

        print("========================================")
        print("ADD BED PAGE ERROR:", repr(e))
        print("========================================")

        return (
            "Unable to load Add Bed page.",
            500
        )


# =========================================================
# ADD BED
# =========================================================

@bed_bp.route("/add", methods=["POST"])
def add_bed():

    if "user" not in session:

        if request.is_json:

            return jsonify({
                "success": False,
                "message": "Unauthorized"
            }), 401

        return redirect("/")


    try:

        # =================================================
        # READ REQUEST DATA
        # =================================================

        if request.is_json:

            data = request.get_json(
                silent=True
            ) or {}

        else:

            data = request.form.to_dict()


        # =================================================
        # BASIC DATA
        # =================================================

        room_id = data.get("room_id")


        bed_code = str(
            data.get("bed_code", "")
        ).strip()


        bed_name = str(
            data.get("bed_name", "")
        ).strip()


        bed_type = str(
            data.get("bed_type", "")
        ).strip()


        status = str(
            data.get(
                "status",
                "Available"
            )
        ).strip()


        description = str(
            data.get(
                "description",
                ""
            )
        ).strip()


        # =================================================
        # BED PRICE
        # =================================================

        bed_price_raw = data.get(
            "bed_price"
        )


        if (
            bed_price_raw is None
            or str(
                bed_price_raw
            ).strip() == ""
        ):

            bed_price = None

        else:

            try:

                bed_price = float(
                    str(
                        bed_price_raw
                    ).strip()
                )

            except (
                ValueError,
                TypeError
            ):

                return bed_error(
                    "Invalid bed charge.",
                    400
                )


            if bed_price < 0:

                return bed_error(
                    "Bed charge cannot be negative.",
                    400
                )


        # =================================================
        # VALIDATE ROOM
        # =================================================

        if not room_id:

            return bed_error(
                "Please select a room.",
                400
            )


        try:

            room_id = int(room_id)

        except (
            ValueError,
            TypeError
        ):

            return bed_error(
                "Invalid room selected.",
                400
            )


        # =================================================
        # VALIDATE BED CODE
        # =================================================

        if not bed_code:

            return bed_error(
                "Bed code is required.",
                400
            )


        # =================================================
        # VALIDATE BED NAME
        # =================================================

        if not bed_name:

            return bed_error(
                "Bed name is required.",
                400
            )


        # =================================================
        # VALIDATE BED TYPE
        # =================================================

        if not bed_type:

            return bed_error(
                "Bed type is required.",
                400
            )


        # =================================================
        # VALIDATE STATUS
        # =================================================

        allowed_statuses = [
            "Available",
            "Occupied",
            "Maintenance",
            "Inactive"
        ]


        if status not in allowed_statuses:

            return bed_error(
                "Invalid bed status.",
                400
            )


        # =================================================
        # CHECK ROOM
        # =================================================

        room = (
            Room.query
            .filter(
                Room.id == room_id,
                Room.status == "Active"
            )
            .first()
        )


        if not room:

            return bed_error(
                "Selected room was not found or is inactive.",
                404
            )


        # =================================================
        # CHECK DUPLICATE BED CODE
        # =================================================

        existing_bed = (
            Bed.query
            .filter(
                db.func.lower(
                    Bed.bed_code
                ) == bed_code.lower()
            )
            .first()
        )


        if existing_bed:

            return bed_error(
                "Bed code already exists.",
                409
            )


        # =================================================
        # CURRENT TIME
        # =================================================

        now = nepal_now()


        # =================================================
        # CREATE BED
        # =================================================

        bed = Bed(

            bed_code=bed_code,

            bed_name=bed_name,

            room_id=room.id,

            bed_price=bed_price,

            bed_type=bed_type,

            status=status or "Available",

            description=(
                description
                if description
                else None
            ),

            created_at=now,

            updated_at=now

        )


        # =================================================
        # SAVE
        # =================================================

        db.session.add(bed)

        db.session.commit()


        # =================================================
        # RESPONSE DATA
        # =================================================

        bed_data = {

            "id":
                bed.id,

            "bed_code":
                bed.bed_code,

            "bed_name":
                bed.bed_name,

            "bed_type":
                bed.bed_type,

            "bed_price": (
                float(
                    bed.bed_price
                )
                if bed.bed_price
                is not None
                else None
            ),

            "room_id":
                bed.room_id,

            "room_name":
                room.room_name,

            "room_code":
                room.room_code,

            "status":
                bed.status,

            "description":
                bed.description or "",

            "created_at": (
                bed.created_at.strftime(
                    "%d/%m/%Y %I:%M %p"
                )
                if bed.created_at
                else ""
            ),

            "updated_at": (
                bed.updated_at.strftime(
                    "%d/%m/%Y %I:%M %p"
                )
                if bed.updated_at
                else ""
            )

        }


        # =================================================
        # JSON / AJAX REQUEST
        # =================================================

        if request.is_json:

            return jsonify({

                "success":
                    True,

                "message":
                    "Bed added successfully.",

                "bed":
                    bed_data

            }), 201


        # =================================================
        # NORMAL FORM SUBMISSION
        # =================================================

        return redirect(
            "/bed/bed_setup"
        )


    except Exception as e:

        db.session.rollback()


        print("========================================")
        print("ADD BED ERROR:", repr(e))
        print("========================================")


        return bed_error(
            "Unable to add bed.",
            500,
            error=str(e)
        )


# =========================================================
# BED ERROR HELPER
# =========================================================

def bed_error(
    message,
    status_code=400,
    error=None
):

    # -----------------------------------------------------
    # JSON RESPONSE
    # -----------------------------------------------------

    if request.is_json:

        response = {

            "success":
                False,

            "message":
                message

        }


        if error:

            response["error"] = error


        return jsonify(
            response
        ), status_code


    # -----------------------------------------------------
    # NORMAL FORM RESPONSE
    # -----------------------------------------------------

    return (
        message,
        status_code
    )