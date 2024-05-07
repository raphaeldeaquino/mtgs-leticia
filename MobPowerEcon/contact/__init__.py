from flask import Blueprint

bp = Blueprint('contact', __name__)

from MobPowerEcon.contact import routes
