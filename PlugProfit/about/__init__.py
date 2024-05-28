from flask import Blueprint

bp = Blueprint('about', __name__)

from PlugProfit.about import routes
