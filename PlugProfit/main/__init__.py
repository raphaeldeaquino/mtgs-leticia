from flask import Blueprint

bp = Blueprint('main', __name__)

from PlugProfit.main import routes
