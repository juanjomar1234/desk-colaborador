from datetime import date, datetime, timezone

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

PROJECT_STATUSES = ('abierto', 'contratado', 'cerrado')
PROPOSAL_STATUSES = ('pendiente', 'preseleccionada', 'rechazada', 'aceptada')
CONTRACT_STATUSES = ('activo', 'finalizado')


def _now():
    return datetime.now(timezone.utc)


def parse_skills(value):
    if not value:
        return []
    if isinstance(value, (list, tuple)):
        items = value
    else:
        items = str(value).split(',')
    seen = []
    for item in items:
        skill = str(item).strip().lower()
        if skill and skill not in seen:
            seen.append(skill)
    return seen


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    skills = db.Column(db.String(500), nullable=False, default='')
    budget_min = db.Column(db.Float, nullable=True)
    budget_max = db.Column(db.Float, nullable=False)
    deadline = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='abierto')
    created_at = db.Column(db.DateTime(timezone=True), default=_now)

    proposals = db.relationship('Proposal', back_populates='project',
                                cascade='all, delete-orphan')
    contract = db.relationship('Contract', back_populates='project', uselist=False)

    @property
    def skill_list(self):
        return parse_skills(self.skills)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'skills': self.skill_list,
            'budget_min': self.budget_min,
            'budget_max': self.budget_max,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'status': self.status,
            'proposal_count': len(self.proposals),
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Freelancer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    skills = db.Column(db.String(500), nullable=False, default='')
    hourly_rate = db.Column(db.Float, nullable=True)
    portfolio_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=_now)

    proposals = db.relationship('Proposal', back_populates='freelancer')

    @property
    def skill_list(self):
        return parse_skills(self.skills)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'skills': self.skill_list,
            'hourly_rate': self.hourly_rate,
            'portfolio_url': self.portfolio_url,
        }


class Proposal(db.Model):
    __table_args__ = (db.UniqueConstraint('project_id', 'freelancer_id'),)

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    freelancer_id = db.Column(db.Integer, db.ForeignKey('freelancer.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    days = db.Column(db.Integer, nullable=False)
    message = db.Column(db.Text, nullable=False, default='')
    status = db.Column(db.String(20), nullable=False, default='pendiente')
    created_at = db.Column(db.DateTime(timezone=True), default=_now)

    project = db.relationship('Project', back_populates='proposals')
    freelancer = db.relationship('Freelancer', back_populates='proposals')

    @property
    def skill_match(self):
        required = self.project.skill_list
        if not required:
            return 100
        offered = set(self.freelancer.skill_list)
        return round(100 * sum(1 for s in required if s in offered) / len(required))

    @property
    def within_budget(self):
        return self.amount <= self.project.budget_max

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'freelancer': self.freelancer.to_dict(),
            'amount': self.amount,
            'days': self.days,
            'message': self.message,
            'status': self.status,
            'skill_match': self.skill_match,
            'within_budget': self.within_budget,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Contract(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False, unique=True)
    proposal_id = db.Column(db.Integer, db.ForeignKey('proposal.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.String(20), nullable=False, default='activo')
    created_at = db.Column(db.DateTime(timezone=True), default=_now)

    project = db.relationship('Project', back_populates='contract')
    proposal = db.relationship('Proposal')

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'project_title': self.project.title,
            'freelancer': self.proposal.freelancer.to_dict(),
            'amount': self.amount,
            'days': self.proposal.days,
            'start_date': self.start_date.isoformat(),
            'status': self.status,
        }
