from flask import render_template
from PlugProfit.contact import bp


@bp.route('/')
def index():
    return render_template('contact/index.html')
