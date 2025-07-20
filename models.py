import enum
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Role(enum.Enum):
    COLABORADOR     = 'COLABORADOR'
    FRANQUICIATARIO = 'FRANQUICIATARIO'

class User(db.Model):
    __tablename__ = 'users'
    id         = db.Column(db.Integer, primary_key=True)
    username   = db.Column(db.String(80), unique=True, nullable=False)
    password   = db.Column(db.String(200), nullable=False)
    role       = db.Column(db.Enum(Role), nullable=False,
                           default=Role.COLABORADOR)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role.value
        }

class ProspectStatus(enum.Enum):
    PENDING     = 'pending'
    NO_RESPONSE = 'no‑response'
    REJECTED    = 'rejected'
    SOLD        = 'sold'   
    SCHEDULED   = 'scheduled'
    FOLLOW_UP   = 'follow‑up'
    ANEXADO     = 'anexado'

class Prospect(db.Model):
    __tablename__ = 'prospects'
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(128), nullable=False)
    phone       = db.Column(db.String(32), nullable=False)
    observation = db.Column(db.String(256))
    status      = db.Column(db.Enum(ProspectStatus),
                            default=ProspectStatus.PENDING,
                            nullable=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    created_by_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_by       = db.relationship(
        'User',
        foreign_keys=[created_by_id],
        backref='created_prospects'
    )
    # NUEVAS RELS PARA RECOMENDACIONES
    recommended_by_id = db.Column(db.Integer, db.ForeignKey('prospects.id'), nullable=True)
    recommended_by    = db.relationship('Prospect', remote_side=[id], backref='referred')

    appointments = db.relationship(
        'Appointment', back_populates='prospect',
        cascade='all, delete-orphan'
    )
    calls = db.relationship(
        'CallSchedule', back_populates='prospect',
        cascade='all, delete-orphan'
    )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'observation': self.observation,
            'status': self.status.value,
            'appointments': [a.to_dict() for a in self.appointments],
            'calls':        [c.to_dict() for c in self.calls],
        }

class Appointment(db.Model):
    __tablename__  = 'appointments'
    id             = db.Column(db.Integer, primary_key=True)
    prospect_id    = db.Column(db.Integer,
                              db.ForeignKey('prospects.id'),
                              nullable=False)
    scheduled_for  = db.Column(db.DateTime, nullable=False)
    address        = db.Column(db.String(256), nullable=True)
    created_at     = db.Column(db.DateTime,
                              default=datetime.utcnow,
                              nullable=False)
    prospect       = db.relationship('Prospect',
                                     back_populates='appointments')
    def to_dict(self):
        return {
            'id': self.id,
            'prospect_id': self.prospect_id,
            'prospect_name': self.prospect.name,        # ← nuevo
            'scheduled_for': self.scheduled_for.isoformat(),
            'address': self.address,
            'prospect_status': self.prospect.status.value 
        }

class CallSchedule(db.Model):
    __tablename__  = 'calls'
    id             = db.Column(db.Integer, primary_key=True)
    prospect_id    = db.Column(db.Integer,
                              db.ForeignKey('prospects.id'),
                              nullable=False)
    scheduled_for  = db.Column(db.DateTime, nullable=False)
    created_at     = db.Column(db.DateTime,
                              default=datetime.utcnow,
                              nullable=False)
    prospect       = db.relationship('Prospect',
                                     back_populates='calls')

    def to_dict(self):
        return {
            'id': self.id,
            'prospect_id': self.prospect_id,
            'scheduled_for': self.scheduled_for.isoformat()
        }
class StatusHistory(db.Model):
    __tablename__ = 'status_history'
    id             = db.Column(db.Integer, primary_key=True)
    prospect_id    = db.Column(db.Integer, db.ForeignKey('prospects.id'), nullable=False)
    old_status     = db.Column(db.String(32), nullable=False)
    new_status     = db.Column(db.String(32), nullable=False)
    changed_at     = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    changed_by_id  = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    changed_by     = db.relationship(
        'User',
        foreign_keys=[changed_by_id],
        backref='status_changes'
    )
    prospect       = db.relationship('Prospect', backref='status_history')