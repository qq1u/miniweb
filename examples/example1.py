from src import Application, Response, request

app = Application()


@app.route('/', methods=['GET', 'POST'])
def index():
    return f'Hello World, from: {request.ip_port}'


@app.route('/json')
def json():
    return {'code': 0, 'data': []}


@app.route('/response')
def response():
    return Response('Hello Response!')


@app.route('/headers')
def get_headers():
    return {
        'data': request.headers
    }


@app.route('/args')
def get_args():
    return {
        'data': request.args
    }


if __name__ == '__main__':
    app.run()
