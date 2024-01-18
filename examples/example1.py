from src import Application, Response, Request

app = Application()


@app.route('/', methods=['GET', 'POST'])
async def index(request: Request):
    return f'Hello World, from: {request.ip_port}'


@app.route('/json')
def json(request: Request):
    return {'code': 0, 'data': []}


@app.route('/response')
def response(request: Request):
    return Response('Hello Response!')


@app.route('/headers')
def get_headers(request: Request):
    return {
        'data': request.headers
    }


@app.route('/args')
def get_args(request: Request):
    return {
        'data': request.args
    }


if __name__ == '__main__':
    app.run()
