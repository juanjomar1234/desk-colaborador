from datetime import date, timedelta

import click

from . import services as svc
from .models import Project, db

DEMO_PROJECTS = [
    {
        'title': 'MVP de portal del colaborador',
        'description': 'Desarrollar el portal web para colaboradores: login, panel de '
                       'aplicaciones y API REST. Entrega en staging con README.',
        'skills': 'python, flask, javascript, sql',
        'budget_min': '3000', 'budget_max': '5000',
        'deadline': (date.today() + timedelta(days=45)).isoformat(),
    },
    {
        'title': 'Diseño UI del panel de facturación',
        'description': 'Wireframes y diseño visual (Figma) del módulo de facturación.',
        'skills': 'figma, ui, ux',
        'budget_max': '1200',
        'deadline': (date.today() + timedelta(days=20)).isoformat(),
    },
]

DEMO_PROPOSALS = [
    (0, {'name': 'Laura Gómez', 'email': 'laura@example.com',
         'skills': 'python, flask, sql, docker', 'hourly_rate': '35',
         'portfolio_url': 'https://example.com/laura', 'amount': '4200', 'days': '30',
         'message': 'He entregado 3 MVPs con Flask en el último año.'}),
    (0, {'name': 'Marc Puig', 'email': 'marc@example.com',
         'skills': 'python, django, javascript, flask, sql', 'hourly_rate': '45',
         'amount': '4900', 'days': '25',
         'message': 'Full-stack senior, disponible a tiempo completo.'}),
    (0, {'name': 'Ana Ruiz', 'email': 'ana@example.com', 'skills': 'php, laravel',
         'hourly_rate': '25', 'amount': '2800', 'days': '40',
         'message': 'Propuesta económica con stack PHP.'}),
    (1, {'name': 'Sofía Martín', 'email': 'sofia@example.com', 'skills': 'figma, ui, ux',
         'hourly_rate': '30', 'amount': '1000', 'days': '14',
         'message': 'Diseñadora de producto con experiencia en dashboards.'}),
]


def seed_demo(only_if_empty=False):
    if only_if_empty and Project.query.count():
        return False
    projects = [svc.create_project(p) for p in DEMO_PROJECTS]
    for idx, data in DEMO_PROPOSALS:
        svc.submit_proposal(projects[idx], data)
    return True


def register_cli(app):
    @app.cli.command('seed-demo')
    def seed_demo_command():
        """Carga proyectos y propuestas de ejemplo."""
        seed_demo()
        click.echo('Datos de ejemplo cargados')

    @app.cli.command('reset-db')
    def reset_db_command():
        """Borra y recrea todas las tablas."""
        db.drop_all()
        db.create_all()
        click.echo('Base de datos reiniciada')
