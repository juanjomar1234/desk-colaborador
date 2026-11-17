from flask import Blueprint, flash, redirect, render_template, request, url_for

from . import services as svc
from .models import Contract, Freelancer, Project, Proposal

views_bp = Blueprint('views', __name__)


def _run(action, success_msg):
    try:
        result = action()
        flash(success_msg, 'success')
        return result
    except svc.ServiceError as err:
        flash(str(err), 'error')
        return None


@views_bp.get('/')
def index():
    status = request.args.get('status', '')
    query = Project.query.order_by(Project.created_at.desc())
    if status:
        query = query.filter_by(status=status)
    return render_template('index.html', projects=query.all(), stats=svc.stats(),
                           status=status)


@views_bp.route('/projects/new', methods=['GET', 'POST'])
def project_new():
    if request.method == 'POST':
        project = _run(lambda: svc.create_project(request.form), 'Proyecto publicado')
        if project:
            return redirect(url_for('views.project_detail', project_id=project.id))
    return render_template('project_new.html', form=request.form)


@views_bp.get('/projects/<int:project_id>')
def project_detail(project_id):
    project = svc.get_or_404(Project, project_id)
    return render_template('project_detail.html', project=project,
                           proposals=svc.ranked_proposals(project))


@views_bp.post('/projects/<int:project_id>/close')
def project_close(project_id):
    project = svc.get_or_404(Project, project_id)
    _run(lambda: svc.close_project(project), 'Proyecto cerrado')
    return redirect(url_for('views.project_detail', project_id=project_id))


@views_bp.route('/projects/<int:project_id>/apply', methods=['GET', 'POST'])
def project_apply(project_id):
    project = svc.get_or_404(Project, project_id)
    if request.method == 'POST':
        proposal = _run(lambda: svc.submit_proposal(project, request.form),
                        'Propuesta enviada. ¡Gracias!')
        if proposal:
            return render_template('apply_done.html', project=project, proposal=proposal)
    return render_template('apply.html', project=project, form=request.form)


@views_bp.post('/proposals/<int:proposal_id>/status')
def proposal_status(proposal_id):
    proposal = svc.get_or_404(Proposal, proposal_id)
    _run(lambda: svc.set_proposal_status(proposal, request.form.get('status')),
         'Propuesta actualizada')
    return redirect(url_for('views.project_detail', project_id=proposal.project_id))


@views_bp.post('/proposals/<int:proposal_id>/hire')
def proposal_hire(proposal_id):
    proposal = svc.get_or_404(Proposal, proposal_id)
    _run(lambda: svc.hire(proposal), f'{proposal.freelancer.name} contratado/a')
    return redirect(url_for('views.project_detail', project_id=proposal.project_id))


@views_bp.get('/contracts')
def contracts():
    items = Contract.query.order_by(Contract.created_at.desc()).all()
    return render_template('contracts.html', contracts=items)


@views_bp.post('/contracts/<int:contract_id>/complete')
def contract_complete(contract_id):
    contract = svc.get_or_404(Contract, contract_id)
    _run(lambda: svc.complete_contract(contract), 'Contrato finalizado')
    return redirect(url_for('views.contracts'))


@views_bp.get('/freelancers')
def freelancers():
    items = Freelancer.query.order_by(Freelancer.name).all()
    return render_template('freelancers.html', freelancers=items)


@views_bp.app_errorhandler(svc.ServiceError)
def not_found(err):
    return render_template('error.html', message=str(err)), err.status_code
