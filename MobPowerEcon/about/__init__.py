from flask import Blueprint

bp = Blueprint('about', __name__)

from MobPowerEcon.about import routes
