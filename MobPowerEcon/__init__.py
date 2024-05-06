from flask import Flask

from .config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Flask extensions here

# Register blueprints here
from MobPowerEcon.main import bp as main_bp
app.register_blueprint(main_bp)

from MobPowerEcon.viability import bp as inputs_bp
app.register_blueprint(inputs_bp, url_prefix='/viabilidade')

from MobPowerEcon.about import bp as about_bp
app.register_blueprint(about_bp, url_prefix='/sobre')
