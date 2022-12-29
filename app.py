from flask import Flask , render_template
from flask_swagger_ui import get_swaggerui_blueprint
from auth import login_manager
from flask_bootstrap import Bootstrap
import os
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from models import db

app = Flask(__name__)
login_manager.init_app(app)

dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(dir,'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'secretkey'

db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
bootstrap = Bootstrap(app)

SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.yml'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Coride"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)

from auth import auth_bp
from rides import rides_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(rides_bp, url_prefix='/api/rides')



@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)



    
    