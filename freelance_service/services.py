"""Reglas de negocio compartidas por la API JSON y las vistas HTML."""
from datetime import date

from .models import (Contract, Freelancer, Project, Proposal, db, parse_skills)


class ServiceError(ValueError):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.status_code = status_code


def _text(data, key, required=True, max_len=None):
    value = (data.get(key) or '').strip()
    if required and not value:
        raise ServiceError(f'El campo "{key}" es obligatorio')
    if max_len and len(value) > max_len:
        raise ServiceError(f'El campo "{key}" supera {max_len} caracteres')
    return value


def _number(data, key, required=True, cast=float, minimum=0):
    raw = data.get(key)
    if raw in (None, ''):
        if required:
            raise ServiceError(f'El campo "{key}" es obligatorio')
        return None
    try:
        value = cast(raw)
    except (TypeError, ValueError):
        raise ServiceError(f'El campo "{key}" debe ser numérico')
    if value < minimum:
        raise ServiceError(f'El campo "{key}" debe ser >= {minimum}')
    return value


def _date(data, key):
    raw = data.get(key)
    if not raw:
        return None
    try:
        return date.fromisoformat(raw)
    except ValueError:
        raise ServiceError(f'El campo "{key}" debe tener formato AAAA-MM-DD')


def get_or_404(model, obj_id):
    obj = db.session.get(model, obj_id)
    if obj is None:
        raise ServiceError(f'{model.__name__} {obj_id} no encontrado', 404)
    return obj


def create_project(data):
    budget_min = _number(data, 'budget_min', required=False)
    budget_max = _number(data, 'budget_max', minimum=1)
    if budget_min is not None and budget_min > budget_max:
        raise ServiceError('El presupuesto mínimo no puede superar al máximo')
    project = Project(
        title=_text(data, 'title', max_len=200),
        description=_text(data, 'description'),
        skills=','.join(parse_skills(data.get('skills'))),
        budget_min=budget_min,
        budget_max=budget_max,
        deadline=_date(data, 'deadline'),
    )
    db.session.add(project)
    db.session.commit()
    return project


def close_project(project):
    if project.status == 'cerrado':
        raise ServiceError('El proyecto ya está cerrado', 409)
    project.status = 'cerrado'
    for p in project.proposals:
        if p.status in ('pendiente', 'preseleccionada'):
            p.status = 'rechazada'
    db.session.commit()
    return project


def submit_proposal(project, data):
    if project.status != 'abierto':
        raise ServiceError('El proyecto no acepta propuestas', 409)
    email = _text(data, 'email', max_len=200).lower()
    if '@' not in email:
        raise ServiceError('Email no válido')
    amount = _number(data, 'amount', minimum=1)
    days = _number(data, 'days', cast=int, minimum=1)
    message = _text(data, 'message')

    freelancer = Freelancer.query.filter_by(email=email).first()
    if freelancer is None:
        freelancer = Freelancer(email=email)
        db.session.add(freelancer)
    freelancer.name = _text(data, 'name', max_len=200)
    freelancer.skills = ','.join(parse_skills(data.get('skills')))
    freelancer.hourly_rate = _number(data, 'hourly_rate', required=False)
    freelancer.portfolio_url = _text(data, 'portfolio_url', required=False, max_len=500) or None
    db.session.flush()

    if Proposal.query.filter_by(project_id=project.id, freelancer_id=freelancer.id).first():
        db.session.rollback()
        raise ServiceError('Este freelance ya envió una propuesta a este proyecto', 409)

    proposal = Proposal(project=project, freelancer=freelancer,
                        amount=amount, days=days, message=message)
    db.session.add(proposal)
    db.session.commit()
    return proposal


def set_proposal_status(proposal, status):
    if status not in ('pendiente', 'preseleccionada', 'rechazada'):
        raise ServiceError('Estado no permitido: use pendiente, preseleccionada o rechazada')
    if proposal.project.status != 'abierto':
        raise ServiceError('El proyecto ya no está abierto', 409)
    proposal.status = status
    db.session.commit()
    return proposal


def hire(proposal, start_date=None):
    project = proposal.project
    if project.status != 'abierto':
        raise ServiceError('El proyecto ya no está abierto', 409)
    if proposal.status == 'rechazada':
        raise ServiceError('No se puede contratar una propuesta rechazada', 409)
    proposal.status = 'aceptada'
    for other in project.proposals:
        if other.id != proposal.id:
            other.status = 'rechazada'
    project.status = 'contratado'
    contract = Contract(project=project, proposal=proposal, amount=proposal.amount,
                        start_date=start_date or date.today())
    db.session.add(contract)
    db.session.commit()
    return contract


def complete_contract(contract):
    if contract.status == 'finalizado':
        raise ServiceError('El contrato ya está finalizado', 409)
    contract.status = 'finalizado'
    contract.project.status = 'cerrado'
    db.session.commit()
    return contract


def ranked_proposals(project):
    return sorted(project.proposals,
                  key=lambda p: (-p.skill_match, not p.within_budget, p.amount))


def stats():
    return {
        'open_projects': Project.query.filter_by(status='abierto').count(),
        'proposals': Proposal.query.count(),
        'pending_proposals': Proposal.query.filter_by(status='pendiente').count(),
        'active_contracts': Contract.query.filter_by(status='activo').count(),
        'committed_budget': sum(c.amount for c in Contract.query.all()),
    }
