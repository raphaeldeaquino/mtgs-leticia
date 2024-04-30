from flask import Blueprint

bp = Blueprint('inputs', __name__)

from MobPowerEcon.inputs import routes
