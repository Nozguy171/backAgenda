# backend/agendaBack/routes/appointment.py
from flask import Blueprint, request, jsonify
from agendaBack.models import db, Appointment, Prospect, ProspectStatus, StatusHistory
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity

appointment_bp = Blueprint('appointments', __name__, url_prefix='/appointments')

@appointment_bp.route('', methods=['GET'])
def list_appointments():
    apps = Appointment.query.order_by(Appointment.scheduled_for).all()
    return jsonify([a.to_dict() for a in apps]), 200

@appointment_bp.route('', methods=['POST'])
@jwt_required()
def create_appointment():
    """
    Crea una cita y marca al prospecto como SCHEDULED,
    además de guardar el cambio en status_history.
    """
    data = request.get_json()
    dt = datetime.fromisoformat(data['scheduled_for'])
    appt = Appointment(
        prospect_id   = data['prospect_id'],
        scheduled_for = dt,
        address       = data.get('address')
    )
    db.session.add(appt)

    # actualiza estado a SCHEDULED y guarda historial
    p = Prospect.query.get_or_404(data['prospect_id'])
    old = p.status.value
    p.status = ProspectStatus.SCHEDULED

    current_user = get_jwt_identity()
    hist = StatusHistory(
        prospect_id   = p.id,
        old_status    = old,
        new_status    = p.status.value,
        changed_at    = datetime.utcnow(),
        changed_by_id = current_user
    )
    db.session.add(hist)

    db.session.commit()
    return jsonify(appt.to_dict()), 201

@appointment_bp.route('/<int:id>/status', methods=['PATCH'])
@jwt_required()
def update_appointment_status(id):
    """
    Cambia el estado del prospecto asociado a la cita (sold/rejected)
    y guarda en status_history.
    """
    data = request.get_json()
    appt = Appointment.query.get_or_404(id)
    p = appt.prospect

    old = p.status.value
    action = data.get('action')
    if action == 'sold':
        p.status = ProspectStatus.FOLLOW_UP
    elif action == 'rejected':
        p.status = ProspectStatus.REJECTED
    else:
        return jsonify(error='invalid action'), 400

    current_user = get_jwt_identity()
    hist = StatusHistory(
        prospect_id   = p.id,
        old_status    = old,
        new_status    = p.status.value,
        changed_at    = datetime.utcnow(),
        changed_by_id = current_user
    )
    db.session.add(hist)

    db.session.commit()
    return jsonify(msg='updated'), 200
