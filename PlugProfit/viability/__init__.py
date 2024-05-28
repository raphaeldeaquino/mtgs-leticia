from flask import Blueprint

bp = Blueprint('viability', __name__)

from PlugProfit.viability import routes
