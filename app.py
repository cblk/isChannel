from flask import Flask
from flask import request
from detector.window import Window

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/data', methods=['POST'])
def data():
    f = request.files['data']

    return f.filename


@app.route('/list', methods=['POST'])
def find_list():
    f = request.files['data']
    url = request.form.get("url")
    page_src = f.read()
    data = []
    if url is None:
        return {'code': 1, 'msg': 'url is None', 'data': data}
    try:
        data = Window.run(url, page_src)
    except Exception as e:
        return {'code': 1, 'msg': str(e), 'data': data}
    return {'code': 0, 'msg': 'success', 'data': data}


if __name__ == '__main__':
    app.run()
