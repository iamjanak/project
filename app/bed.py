from flask import Blueprint, render_template, request, jsonify, redirect, session
from datetime import datetime, timedelta

from app.database import db
from app.models import Bed, Room

def nepal_now():
    return datetime.utcnow() + timedelta(hours=5, minutes=45)



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
        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 401


    rooms = (
        Room.query
        .order_by(Room.id.desc())
        .all()
    )

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

# =========================================================
# ADD BED
# =========================================================

@bed_bp.route("/add", methods=["POST"])
def add_bed():

    try:

        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "message": "No data received."
            }), 400

        # -------------------------------------------------
        # BASIC DATA
        # -------------------------------------------------

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
            data.get("status", "Available")
        ).strip()

        description = str(
            data.get("description", "")
        ).strip()

        # -------------------------------------------------
        # BED PRICE
        # Price is optional and can be updated later.
        # -------------------------------------------------

        bed_price_raw = data.get("bed_price")

        if (
            bed_price_raw is None
            or str(bed_price_raw).strip() == ""
        ):
            bed_price = None

        else:

            try:

                bed_price = float(
                    str(bed_price_raw).strip()
                )

            except (ValueError, TypeError):

                return jsonify({
                    "success": False,
                    "message": "Invalid bed charge."
                }), 400

            if bed_price < 0:

                return jsonify({
                    "success": False,
                    "message": "Bed charge cannot be negative."
                }), 400

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not room_id:

            return jsonify({
                "success": False,
                "message": "Please select a room."
            }), 400

        if not bed_code:

            return jsonify({
                "success": False,
                "message": "Bed code is required."
            }), 400

        if not bed_name:

            return jsonify({
                "success": False,
                "message": "Bed name is required."
            }), 400

        if not bed_type:

            return jsonify({
                "success": False,
                "message": "Bed type is required."
            }), 400

        # -------------------------------------------------
        # ROOM
        # -------------------------------------------------

        try:

            room_id = int(room_id)

        except (ValueError, TypeError):

            return jsonify({
                "success": False,
                "message": "Invalid room selected."
            }), 400

        room = Room.query.get(room_id)

        if not room:

            return jsonify({
                "success": False,
                "message": "Selected room was not found."
            }), 404

        # -------------------------------------------------
        # DUPLICATE BED CODE
        # -------------------------------------------------

        existing_bed = (
            Bed.query
            .filter_by(bed_code=bed_code)
            .first()
        )

        if existing_bed:

            return jsonify({
                "success": False,
                "message": "Bed code already exists."
            }), 409

        # -------------------------------------------------
        # CREATE BED
        # -------------------------------------------------

        now = nepal_now()
        bed = Bed(
            bed_code=bed_code,
            bed_name=bed_name,
            room_id=room.id,
            bed_price=bed_price,
            bed_type=bed_type,
            status=status or "Available",
            description=description or None,
            created_at=now,
            updated_at=now
        )

        db.session.add(bed)

        db.session.commit()

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------

        return jsonify({
            "success": True,
            "message": "Bed added successfully.",
            "bed": {
                "id": bed.id,
                "bed_code": bed.bed_code,
                "bed_name": bed.bed_name,
                "bed_type": bed.bed_type,
                "bed_price": (
                    float(bed.bed_price)
                    if bed.bed_price is not None
                    else None
                ),
                "room_id": bed.room_id,
                "room_name": room.room_name,
                "status": bed.status,
                "description": bed.description or "",
                "created_at": (
                    bed.created_at.strftime(
                        "%d/%m/%Y %I:%M %p"
                    )
                    if bed.created_at
                    else ""
                )
            }
        }), 201

    except Exception as e:

        db.session.rollback()

        print(
            "BED SETUP ERROR:",
            repr(e)
        )

        return jsonify({
            "success": False,
            "message": "Unable to add bed."
        }), 500