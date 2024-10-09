import os

from flask import Flask, request, abort
from function import handler

app = Flask(__name__)


@app.route('/', methods=["POST"])
def yolo():
    ret = None
    print(request.data)
    if request.data:
        ret = handler.handle(request.data)
    if ret == None:
        abort(400)
    return ret


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080)
