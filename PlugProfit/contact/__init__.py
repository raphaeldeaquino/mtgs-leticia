from flask import Blueprint

bp = Blueprint('contact', __name__)

from PlugProfit.contact import routes
