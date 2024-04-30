from flask import render_template
from MobPowerEcon.inputs import bp


@bp.route('/')
def index():
    return render_template('inputs/index.html')
