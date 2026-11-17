import os

from flask import Flask, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix

from .models import db


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    os.makedirs(app.instance_path, exist_ok=True)

    default_db = 'sqlite:///' + os.path.join(app.instance_path, 'freelance.db')
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('FREELANCE_SECRET_KEY', 'dev'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('FREELANCE_DATABASE_URL', default_db),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SEED_DEMO=os.environ.get('FREELANCE_SEED_DEMO') == '1',
        CHANGE_REQUEST_URL=os.environ.get('FREELANCE_CHANGE_REQUEST_URL', ''),
    )
    if test_config:
        app.config.from_mapping(test_config)

    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
    db.init_app(app)

    from .api import api_bp
    from .views import views_bp
    app.register_blueprint(api_bp)
    app.register_blueprint(views_bp)

    @app.get('/health')
    def health():
        return jsonify(status='ok', service='freelance_service')

    @app.context_processor
    def inject_globals():
        return {'change_request_url': app.config['CHANGE_REQUEST_URL']}

    from .seed import register_cli, seed_demo
    register_cli(app)

    with app.app_context():
        db.create_all()
        if app.config['SEED_DEMO']:
            seed_demo(only_if_empty=True)

    return app
