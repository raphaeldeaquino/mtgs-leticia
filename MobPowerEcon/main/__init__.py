from flask import Blueprint

bp = Blueprint('main', __name__)


from MobPowerEcon.main import routes
