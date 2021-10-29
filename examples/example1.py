from src import Application, Response, request, WebServer

app = Application()


@app.route('/', methods=['GET', 'POST'])
def index():
    print(request.json)
    return f'Hello World, from: {request.ip_port}'


@app.route('/json')
def json():
    return {'code': 0, 'data': []}


@app.route('/response')
def response():
    return Response('Hello Response!')


if __name__ == '__main__':
    WebServer().run(app)