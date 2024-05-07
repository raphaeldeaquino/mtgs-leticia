from flask import render_template
from MobPowerEcon.contact import bp


@bp.route('/')
def index():
    return render_template('contact/index.html')
