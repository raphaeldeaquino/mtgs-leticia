from flask import Flask

from .config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Flask extensions here

# Register blueprints here
from PlugProfit.main import bp as main_bp
app.register_blueprint(main_bp)

from PlugProfit.viability import bp as inputs_bp
app.register_blueprint(inputs_bp, url_prefix='/viabilidade')

from PlugProfit.about import bp as about_bp
app.register_blueprint(about_bp, url_prefix='/sobre')

from PlugProfit.contact import bp as contact_bp
app.register_blueprint(contact_bp, url_prefix='/contato')
