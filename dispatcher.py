from flask import Flask
from restservice import app as restserv
from train import app as mainapp
from handler import app as soapserv
from werkzeug.middleware.dispatcher import DispatcherMiddleware

app = Flask(__name__)

app.wsgi_app = DispatcherMiddleware(mainapp, {
    '/restservice': restserv,
    '/soapservice':soapserv
})

if __name__ == "__main__":
    app.run()
