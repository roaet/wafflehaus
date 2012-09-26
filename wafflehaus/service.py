import logging

from flask import Flask
from flask import request

logging.basicConfig()
app = Flask(__name__)


@app.route("/")
def create():
    #request.body['server'] = "bobbeh"
    logging.fatal("Incoming request: %s" % request)
    logging.fatal("Request header: %s" % request.headers)

    #logging.fatal("Incoming request body: %s" % request.body)
    return "hello"

if __name__ == "__main__":
    app.run()


def app_factory(global_config, **local_conf):
    return app
