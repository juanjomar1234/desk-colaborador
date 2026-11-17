from .. import db


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    icon = db.Column(db.String(40), nullable=False, default='th-large')
    description = db.Column(db.String(255), default='')
    url = db.Column(db.String(255), default='')
    enabled = db.Column(db.Boolean, nullable=False, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'icon': self.icon,
            'description': self.description,
            'url': self.url,
            'enabled': self.enabled
        }
