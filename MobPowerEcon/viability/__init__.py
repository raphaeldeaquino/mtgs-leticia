from flask import Blueprint

bp = Blueprint('viability', __name__)

from MobPowerEcon.viability import routes
