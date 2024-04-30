from flask import Flask

from config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask extensions here

    # Register blueprints here
    from MobPowerEcon.main import bp as main_bp
    app.register_blueprint(main_bp)

    from MobPowerEcon.inputs import bp as inputs_bp
    app.register_blueprint(inputs_bp, url_prefix='/inputs')

    from MobPowerEcon.about import bp as about_bp
    app.register_blueprint(about_bp, url_prefix='/sobre')

    @app.route('/test/')
    def test_page():
        return '<h1>Testing the Flask Application Factory Pattern</h1>'

    return app