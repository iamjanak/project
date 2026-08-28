from flask import Blueprint, render_template, request, jsonify, redirect, session
from datetime import datetime

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

        wards = (
            Ward.query
            .filter_by(status="Active")
            .order_by(Ward.ward_name.asc())
            .all()
        )

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

        print("ROOM SETUP ERROR:", repr(e))

        return (
            "Unable to load Room Setup.",
            500
        )

# =========================================================
# ADD ROOM
# =========================================================

@room_bp.route("/add", methods=["POST"])
def add_room():

    if "user" not in session:

        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 401

    try:

        # =================================================
        # READ JSON
        # =================================================

        data = request.get_json(silent=True) or {}

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

            return jsonify({
                "success": False,
                "message": "Please select a ward."
            }), 400


        try:

            ward_id = int(ward_id)

        except (TypeError, ValueError):

            return jsonify({
                "success": False,
                "message": "Invalid ward selected."
            }), 400


        # =================================================
        # VALIDATE ROOM CODE
        # =================================================

        if not room_code:

            return jsonify({
                "success": False,
                "message": "Room code is required."
            }), 400


        # =================================================
        # VALIDATE ROOM NAME
        # =================================================

        if not room_name:

            return jsonify({
                "success": False,
                "message": "Room name is required."
            }), 400


        # =================================================
        # VALIDATE ROOM TYPE
        # =================================================

        if not room_type:

            return jsonify({
                "success": False,
                "message": "Room type is required."
            }), 400


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

            return jsonify({
                "success": False,
                "message": "Selected ward was not found or is inactive."
            }), 404


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

            return jsonify({
                "success": False,
                "message": "Room code already exists."
            }), 400


        # =================================================
        # CREATE ROOM
        # =================================================

        now = datetime.utcnow()

        room = Room(

            ward_id=ward.id,

            room_code=room_code,

            # ---------------------------------------------
            # IMPORTANT
            # Room model requires room_number.
            # Current UI does not have a separate field,
            # therefore use room_code as room_number.
            # ---------------------------------------------

            room_number=room_code,

            room_name=room_name,

            room_type=room_type,

            floor=floor,

            # Default capacity
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
        # RESPONSE
        # =================================================

        return jsonify({

            "success": True,

            "message":
                "Room added successfully.",

            "room": {

                "id":
                    room.id,

                "ward_id":
                    room.ward_id,

                "ward_name":
                    ward.ward_name,

                "room_code":
                    room.room_code,

                "room_number":
                    room.room_number,

                "room_name":
                    room.room_name,

                "room_type":
                    room.room_type,

                "floor":
                    room.floor,

                "capacity":
                    room.capacity,

                "description":
                    room.description,

                "status":
                    room.status,

                "created_at":
                    (
                        room.created_at.strftime(
                            "%d/%m/%Y %I:%M %p"
                        )
                        if room.created_at
                        else ""
                    ),

                "updated_at":
                    (
                        room.updated_at.strftime(
                            "%d/%m/%Y %I:%M %p"
                        )
                        if room.updated_at
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
            "ADD ROOM ERROR:",
            repr(e)
        )

        print(
            "========================================"
        )

        return jsonify({

            "success": False,

            "message":
                "Unable to add room.",

            "error":
                str(e)

        }), 500