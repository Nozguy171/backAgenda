# backend/agendaBack/routes/call.py
from flask import Blueprint, jsonify, request
from models import db, CallSchedule, Prospect
from datetime import datetime

call_bp = Blueprint('calls', __name__, url_prefix='/calls')

@call_bp.route('', methods=['GET'])
def list_calls():
    calls = CallSchedule.query.order_by(CallSchedule.scheduled_for).all()
    result = []
    for c in calls:
        p = Prospect.query.get(c.prospect_id)
        result.append({
            'id': c.id,
            'prospect_id': c.prospect_id,
            'prospect_name': p.name,
            'prospect_phone': p.phone,
            'prospect_observation': p.observation,
            'scheduled_for': c.scheduled_for.isoformat()
        })
    return jsonify(result), 200

@call_bp.route('', methods=['POST'])
def create_call():
    data = request.get_json()
    dt = datetime.fromisoformat(data['scheduled_for'])
    call = CallSchedule(prospect_id=data['prospect_id'], scheduled_for=dt)
    db.session.add(call)
    db.session.commit()
    p = Prospect.query.get(call.prospect_id)
    return jsonify({
        'id': call.id,
        'prospect_id': call.prospect_id,
        'prospect_name': p.name,
        'prospect_phone': p.phone,
        'prospect_observation': p.observation,
        'scheduled_for': call.scheduled_for.isoformat()
    }), 201
