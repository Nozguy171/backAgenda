# backend/agendaBack/routes/prospect.py
from flask import Blueprint, request, jsonify, abort
from ..models import db, Prospect, ProspectStatus, Appointment, CallSchedule, StatusHistory
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity

prospect_bp = Blueprint('prospect', __name__, url_prefix='/prospects')

@prospect_bp.route('/<int:prospect_id>', methods=['GET'])
def get_prospect(prospect_id):
    p = Prospect.query.get_or_404(prospect_id)
    return jsonify(p.to_dict()), 200

@prospect_bp.route('', methods=['GET'])
def list_prospects():
    search = request.args.get('search', '')
    query = Prospect.query
    if search:
        query = query.filter(Prospect.name.ilike(f"%{search}%"))
    pros = query.all()
    return jsonify([p.to_dict() for p in pros])

@prospect_bp.route('', methods=['POST'])
@jwt_required()
def create_prospect():
    """
    Crea prospecto y guarda el cambio inicial en status_history.
    """
    current_user = get_jwt_identity()
    data = request.get_json()
    p = Prospect(
        name             = data['name'],
        phone            = data['phone'],
        observation      = data.get('observation',''),
        status           = ProspectStatus.PENDING,
        created_at       = datetime.utcnow(),
        recommended_by_id= data.get('recomendadoPorId'),
        created_by_id    = current_user
    )
    db.session.add(p)
    db.session.flush()  # para obtener p.id antes de commit

    hist = StatusHistory(
        prospect_id   = p.id,
        old_status    = '',
        new_status    = p.status.value,
        changed_at    = datetime.utcnow(),
        changed_by_id = current_user
    )
    db.session.add(hist)
    db.session.commit()
    return jsonify(p.to_dict()), 201

@prospect_bp.route('/<int:prospect_id>/status', methods=['PATCH'])
@jwt_required()
def update_status(prospect_id):
    """
    Cambia el estado del prospecto (pending|no-response|rejected)
    y registra el cambio.
    """
    raw = request.args.get('status','')
    norm = raw.replace('-', '\u2011')
    if norm not in ProspectStatus._value2member_map_:
        return jsonify({'error':'status no válido'}), 400

    p = Prospect.query.get_or_404(prospect_id)
    old = p.status.value
    p.status = ProspectStatus(norm)

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
    return jsonify(p.to_dict()), 200

@prospect_bp.route('/<int:prospect_id>/schedule', methods=['POST'])
@jwt_required()
def schedule_appointment(prospect_id):
    """
    Programa cita desde /prospects/:id/schedule,
    cambia estado a SCHEDULED y registra en historial.
    """
    p = Prospect.query.get_or_404(prospect_id)
    data = request.get_json() or {}
    dt_str = data.get('datetime')
    if not dt_str:
        return jsonify({'error':'datetime requerido'}), 400
    try:
        dt = datetime.fromisoformat(dt_str)
    except ValueError:
        return jsonify({'error':'datetime inválido'}), 400

    appt = Appointment(
        prospect_id   = prospect_id,
        scheduled_for = dt,
        address       = data.get('address')
    )
    db.session.add(appt)

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
    return jsonify(p.to_dict()), 200

@prospect_bp.route('/<int:prospect_id>/call', methods=['POST'])
@jwt_required()
def schedule_call(prospect_id):
    """
    Programa llamada desde /prospects/:id/call,
    **no** cambia el estado de prospecto.
    """
    p = Prospect.query.get_or_404(prospect_id)
    data = request.get_json() or {}
    dt_str = data.get('datetime')
    if not dt_str:
        return jsonify({'error':'datetime requerido'}), 400
    try:
        dt = datetime.fromisoformat(dt_str)
    except ValueError:
        return jsonify({'error':'datetime inválido'}), 400

    call = CallSchedule(prospect_id=prospect_id, scheduled_for=dt)
    db.session.add(call)
    db.session.commit()
    return jsonify(p.to_dict()), 201

@prospect_bp.route('/<int:prospect_id>/friends', methods=['GET'])
def view_friends(prospect_id):
    p = Prospect.query.get_or_404(prospect_id)
    return jsonify({
        'recommended_by': p.recommended_by    and p.recommended_by.to_dict(),
        'referred'      : [r.to_dict() for r in p.referred]
    })

@prospect_bp.route('/<int:prospect_id>/follow-up', methods=['POST'])
@jwt_required()
def start_followup(prospect_id):
    """
    Mueve manualmente al prospecto a FOLLOW_UP
    y guarda historial.
    """
    p = Prospect.query.get_or_404(prospect_id)
    old = p.status.value
    p.status = ProspectStatus.FOLLOW_UP

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
    return jsonify(p.to_dict()), 200
