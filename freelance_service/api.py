from flask import Blueprint, jsonify, request

from . import services as svc
from .models import Contract, Freelancer, Project, Proposal

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.errorhandler(svc.ServiceError)
def handle_service_error(err):
    return jsonify(error=str(err)), err.status_code


def _payload():
    return request.get_json(silent=True) or {}


@api_bp.get('/projects')
def list_projects():
    query = Project.query.order_by(Project.created_at.desc())
    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)
    return jsonify([p.to_dict() for p in query.all()])


@api_bp.post('/projects')
def create_project():
    return jsonify(svc.create_project(_payload()).to_dict()), 201


@api_bp.get('/projects/<int:project_id>')
def get_project(project_id):
    project = svc.get_or_404(Project, project_id)
    data = project.to_dict()
    data['proposals'] = [p.to_dict() for p in svc.ranked_proposals(project)]
    data['contract'] = project.contract.to_dict() if project.contract else None
    return jsonify(data)


@api_bp.post('/projects/<int:project_id>/close')
def close_project(project_id):
    return jsonify(svc.close_project(svc.get_or_404(Project, project_id)).to_dict())


@api_bp.get('/projects/<int:project_id>/proposals')
def list_proposals(project_id):
    project = svc.get_or_404(Project, project_id)
    return jsonify([p.to_dict() for p in svc.ranked_proposals(project)])


@api_bp.post('/projects/<int:project_id>/proposals')
def submit_proposal(project_id):
    project = svc.get_or_404(Project, project_id)
    return jsonify(svc.submit_proposal(project, _payload()).to_dict()), 201


@api_bp.patch('/proposals/<int:proposal_id>')
def update_proposal(proposal_id):
    proposal = svc.get_or_404(Proposal, proposal_id)
    return jsonify(svc.set_proposal_status(proposal, _payload().get('status')).to_dict())


@api_bp.post('/proposals/<int:proposal_id>/hire')
def hire(proposal_id):
    proposal = svc.get_or_404(Proposal, proposal_id)
    return jsonify(svc.hire(proposal).to_dict()), 201


@api_bp.get('/contracts')
def list_contracts():
    return jsonify([c.to_dict() for c in Contract.query.order_by(Contract.created_at.desc())])


@api_bp.post('/contracts/<int:contract_id>/complete')
def complete_contract(contract_id):
    return jsonify(svc.complete_contract(svc.get_or_404(Contract, contract_id)).to_dict())


@api_bp.get('/freelancers')
def list_freelancers():
    return jsonify([f.to_dict() for f in Freelancer.query.order_by(Freelancer.name)])


@api_bp.get('/stats')
def stats():
    return jsonify(svc.stats())
