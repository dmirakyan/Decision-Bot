from flask import Flask, request

app = Flask(__name__)
# client = WebClient(token='xoxb-2275183503-2822568687904-VGTCw4haGfSiDRYOG08wDUR5')
# bolt_app = App(token='xoxb-2275183503-2822568687904-VGTCw4haGfSiDRYOG08wDUR5', signing_secret='dc1754690c5584a36c64a816642c3e34')
# handler = SlackRequestHandler(bolt_app)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"