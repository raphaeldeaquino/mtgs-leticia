from flask import render_template
from MobPowerEcon.main import bp


@bp.route('/')
def index():
    return render_template('index.html')
