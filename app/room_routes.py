from flask import Blueprint, render_template, request, jsonify, redirect, session
from datetime import datetime, timedelta

from app.database import db
from app.models import Room, Ward


room_bp = Blueprint(
    "room",
    __name__,
    url_prefix="/room"
)


# =========================================================
# ROOM SETUP PAGE
# =========================================================

@room_bp.route("/room_setup", methods=["GET"])
def room_setup():

    if "user" not in session:
        return redirect("/")

    try:

        # -------------------------------------------------
        # GET ACTIVE WARDS
        # -------------------------------------------------

        wards = (
            Ward.query
            .filter_by(status="Active")
            .order_by(Ward.ward_name.asc())
            .all()
        )

        # -------------------------------------------------
        # GET ROOMS
        # -------------------------------------------------

        rooms = (
            Room.query
            .order_by(Room.id.desc())
            .all()
        )

        return render_template(
            "setup/room_setup.html",
            wards=wards,
            rooms=rooms,
            active_page="room_setup"
        )

    except Exception as e:

        print("========================================")
        print("ROOM SETUP ERROR:", repr(e))
        print("========================================")

        return (
            "Unable to load Room Setup.",
            500
        )


# =========================================================
# ADD ROOM PAGE
# =========================================================

@room_bp.route("/add", methods=["GET"])
def add_room_page():

    if "user" not in session:
        return redirect("/")

    try:

        # -------------------------------------------------
        # GET ACTIVE WARDS
        # -------------------------------------------------

        wards = (
            Ward.query
            .filter_by(status="Active")
            .order_by(Ward.ward_name.asc())
            .all()
        )

        return render_template(
            "setup/add_room.html",
            wards=wards,
            active_page="room_setup"
        )

    except Exception as e:

        print("========================================")
        print("ADD ROOM PAGE ERROR:", repr(e))
        print("========================================")

        return (
            "Unable to load Add Room page.",
            500
        )


# =========================================================
# ADD ROOM
# =========================================================

@room_bp.route("/add", methods=["POST"])
def add_room():

    if "user" not in session:

        # AJAX request
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

            data = request.get_json(silent=True) or {}

        else:

            data = request.form.to_dict()


        # =================================================
        # READ FIELDS
        # =================================================

        ward_id = data.get("ward_id")

        room_code = (
            data.get("room_code") or ""
        ).strip()

        room_name = (
            data.get("room_name") or ""
        ).strip()

        room_type = (
            data.get("room_type") or ""
        ).strip()

        floor = (
            data.get("floor") or ""
        ).strip()

        status = (
            data.get("status") or "Active"
        ).strip()

        description = (
            data.get("description") or ""
        ).strip()


        # =================================================
        # VALIDATE WARD
        # =================================================

        if not ward_id:

            return room_error(
                "Please select a ward.",
                400
            )


        try:

            ward_id = int(ward_id)

        except (TypeError, ValueError):

            return room_error(
                "Invalid ward selected.",
                400
            )


        # =================================================
        # VALIDATE ROOM CODE
        # =================================================

        if not room_code:

            return room_error(
                "Room code is required.",
                400
            )


        # =================================================
        # VALIDATE ROOM NAME
        # =================================================

        if not room_name:

            return room_error(
                "Room name is required.",
                400
            )


        # =================================================
        # VALIDATE ROOM TYPE
        # =================================================

        if not room_type:

            return room_error(
                "Room type is required.",
                400
            )


        # =================================================
        # VALIDATE STATUS
        # =================================================

        allowed_statuses = [
            "Active",
            "Inactive",
            "Maintenance"
        ]

        if status not in allowed_statuses:

            return room_error(
                "Invalid room status.",
                400
            )


        # =================================================
        # CHECK WARD
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

            return room_error(
                "Selected ward was not found or is inactive.",
                404
            )


        # =================================================
        # CHECK DUPLICATE ROOM CODE
        # =================================================

        existing_room = (
            Room.query
            .filter(
                db.func.lower(
                    Room.room_code
                ) == room_code.lower()
            )
            .first()
        )

        if existing_room:

            return room_error(
                "Room code already exists.",
                400
            )


        # =================================================
        # CURRENT NEPAL TIME
        # =================================================

        now = datetime.utcnow() + timedelta(hours=5, minutes=45)


        # =================================================
        # CREATE ROOM
        # =================================================

        room = Room(

            ward_id=ward.id,

            # Room code
            room_code=room_code,

            # Your Room model requires room_number.
            # Using room_code as room_number because
            # there is currently no separate room number
            # field in the UI.

            room_number=room_code,

            room_name=room_name,

            room_type=room_type,

            floor=floor,

            # Default room capacity
            capacity=1,

            description=description,

            status=status,

            created_at=now,

            updated_at=now
        )


        # =================================================
        # SAVE
        # =================================================

        db.session.add(room)

        db.session.commit()


        # =================================================
        # AJAX RESPONSE
        # =================================================

        room_data = {

            "id": room.id,

            "ward_id": room.ward_id,

            "ward_name": ward.ward_name,

            "room_code": room.room_code,

            "room_number": room.room_number,

            "room_name": room.room_name,

            "room_type": room.room_type,

            "floor": room.floor,

            "capacity": room.capacity,

            "description": room.description,

            "status": room.status,

            "created_at": (
                room.created_at.strftime(
                    "%d/%m/%Y %I:%M %p"
                )
                if room.created_at
                else ""
            ),

            "updated_at": (
                room.updated_at.strftime(
                    "%d/%m/%Y %I:%M %p"
                )
                if room.updated_at
                else ""
            )
        }


        # =================================================
        # IF AJAX / JSON REQUEST
        # =================================================

        if request.is_json:

            return jsonify({

                "success": True,

                "message":
                    "Room added successfully.",

                "room":
                    room_data

            }), 201


        # =================================================
        # NORMAL FORM SUBMISSION
        # =================================================

        return redirect("/room/room_setup")


    except Exception as e:

        db.session.rollback()

        print("========================================")
        print("ADD ROOM ERROR:", repr(e))
        print("========================================")

        return room_error(
            "Unable to add room.",
            500,
            error=str(e)
        )


# =========================================================
# ROOM ERROR HELPER
# =========================================================

def room_error(message, status_code=400, error=None):

    # -----------------------------------------------------
    # JSON / AJAX RESPONSE
    # -----------------------------------------------------

    if request.is_json:

        response = {
            "success": False,
            "message": message
        }

        if error:
            response["error"] = error

        return jsonify(response), status_code


    # -----------------------------------------------------
    # NORMAL FORM REQUEST
    # -----------------------------------------------------

    return (
        message,
        status_code
    )