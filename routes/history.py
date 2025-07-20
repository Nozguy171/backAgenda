# agendaBack/routes/history.py
from flask import Blueprint, jsonify
from agendaBack.models import Prospect, StatusHistory

history_bp = Blueprint('history', __name__, url_prefix='/history')

@history_bp.route('', methods=['GET'])
def get_history():
    """
    GET /history
    Devuelve todos los prospectos junto con su historial de cambios.
    """
    todos = []
    for p in Prospect.query.order_by(Prospect.name).all():
        hist = [
            {
                'old_status': h.old_status,
                'new_status': h.new_status,
                'changed_at': h.changed_at.isoformat(),
                'changed_by': h.changed_by.to_dict() if h.changed_by else None
            }
            for h in p.status_history
        ]
        todos.append({
            'prospect_id': p.id,
            'name': p.name,
            'phone': p.phone,
            'observation': p.observation,
            'history': hist
        })
    return jsonify(todos), 200
