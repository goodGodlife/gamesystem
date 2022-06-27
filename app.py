from flask_cors import  CORS
from accout.api import *
from game.api import *
from report.api import *
from usdt.api import *
app = Flask(__name__)
app.register_blueprint(accout)
app.register_blueprint(gameapi)
app.register_blueprint(reportapi)
app.register_blueprint(usdtapi)
app.register_blueprint(admin)

CORS(app, supports_credentials=True,allow_heads='*')

@app.route('/hello')
def hello_world():  # put application's code here
    return 'Hello World!'


# if __name__ == '__main__':
    # app.run(threading=True)
