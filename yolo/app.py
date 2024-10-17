import os

from flask import Flask, request, abort
from function import handler

app = Flask(__name__)


@app.route('/', methods=["POST"])
def yolo():
    ret = None
    print(request.get_data())
    if request.data:
        ret = handler.handle(request.data.decode())
    if ret == None:
        abort(400)
    if not ret:
        abort(500)
    return ret

@app.route('/readiness', methods=["GET"])
def ready():
    return "Ready"

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080)
