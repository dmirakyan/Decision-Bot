from flask import Flask, jsonify, request, Response
import openai
import os
from slackeventsapi import SlackEventAdapter
from slack import WebClient
from slack_bolt import App, Say
from slack_bolt.adapter.flask import SlackRequestHandler
import random




app = Flask(__name__)

SLACK_SIGNING_SECRET = os.environ['SLACK_SIGNING_SECRET']
SLACK_TOKEN = os.environ['SLACK_TOKEN']
openai.api_key = os.environ['OPENAI_KEY']
client = WebClient(token=SLACK_TOKEN)

bolt_app = App(token=SLACK_TOKEN, signing_secret=SLACK_SIGNING_SECRET)
handler = SlackRequestHandler(bolt_app)


def receive_wisdom(query):
    training_text = "Q: Do you want an apple or an orange?\n A: An orange\nQ: Shopping in-store or online?\nA: shopping online\nQ: Pepperoni pizza or cheese pizza?\nA: pepperoni pizza\nQ:Dark chocolate or white chocolate?\nA: white chocolate\nQ:Baseball or volleyball?\nA: volleyball\nQ:Bagels or muffins?\nA: bagels\nQ: Giving a gift or receiving a gift?\nA: Giving a gift\nQ: Workout at home or at the gym?\nA: Workout at home\nQ: Sleep on the left or the right side of the bed?\nA: Sleep on the right side of the bed\n"
    user_query = query
    prompt = training_text + "Q: " + user_query + "\nA:"
    response = openai.Completion.create(
        engine="curie",
        prompt=prompt,
        temperature=0.5,
        max_tokens=76,
        top_p=1,
        frequency_penalty=0.5,
        presence_penalty=0.3,
        stop=["Q:"]
    )
    answer = response.choices[0].text
    return answer



@bolt_app.message("Q:")
def greetings(payload: dict, say: Say):
    user = payload.get("user")
    user_query = payload.get("text")
    user_query = user_query[2:].strip()
    thread = payload.get('thread_ts')

    if thread == None:
        thread_ts = payload.get('ts')
    else:
        thread_ts = thread
    
    score = random.randint(1,100)
    if score > 95:
        answer = "Try asking in #analytics-work?"
    elif score > 90 :
        answer = "It's probably just seasonality"
    elif score > 85 :
        answer = "It's probably just pricing"
    elif score > 80 :
        answer = "It's probably just marketing mix"
    else:
        answer = receive_wisdom(user_query)  
    response = client.chat_postMessage(
                                    channel=payload.get('channel'),
                                    thread_ts=thread_ts,
                                    text = answer
    )

    # print(response)
    # if score > 90:
    #     answer = "Try asking in #analytics-work?"
    # else:
    #     answer = receive_wisdom(user_query)    
    # client.chat_post_Message(

    # )
    # say(text=answer, 
        # thread_ts=payload.get("ts"),
        # response_type="in_channel",
    # )


@app.route("/bot/events", methods=["POST"])
def slack_events():
    """ Declaring the route where slack will post a request """
    return handler.handle(request)

@app.route("/")
def hello_world():
    return "<p>I'm a real boy!!</p>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

