from flask import Flask, jsonify, request, Response
import openai
import os
import re
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
    # Training text primes the model. Here used a series of questions and answers.
    training_text = "Q: Do you want an apple or an orange?\n A: An orange\nQ: Shopping in-store or online?\nA: shopping online\nQ: Pepperoni pizza or cheese pizza?\nA: pepperoni pizza\nQ:Dark chocolate or white chocolate?\nA: white chocolate\nQ:Baseball or volleyball?\nA: volleyball\nQ:Bagels or muffins?\nA: bagels\nQ: Giving a gift or receiving a gift?\nA: Giving a gift\nQ: Workout at home or at the gym?\nA: Workout at home\nQ: Sleep on the left or the right side of the bed?\nA: Sleep on the right side of the bed\n"
    user_query = query
    prompt = training_text + "Q: " + user_query + "\nA:"
    response = openai.Completion.create(
        engine="curie", 
        prompt=prompt,
        temperature=0.5,
        max_tokens=76,
        top_p=1,
        frequency_penalty=0.9,
        presence_penalty=0.4,
        stop=["Q:"] # Cuts of responses after question is answered. Otherwise model continues generating question / answer pairs on its own.
    )
    answer = response.choices[0].text
    return answer

# App monitors channels it's in waiting for a message starting with "Q:"
@bolt_app.message(re.compile("^(Q:|q:)"))
def greetings(payload: dict, say: Say):
    user = payload.get("user")
    user_query = payload.get("text")
    user_query = user_query[2:].strip() # Parses / cleans up question
    print(user_query)

    # Replies get posted within thread. 
    thread = payload.get('thread_ts')
    if thread == None:
        thread_ts = payload.get('ts')
    else:
        thread_ts = thread
    
    # Rolls a 1-100 dice. Used to occasionally respond with a pre-determined phrase. Otherwise query GPT3.
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

@app.route("/bot/events", methods=["POST"])
def slack_events():
    """ Declaring the route where slack will post a request """
    return handler.handle(request)

@app.route("/")
def hello_world():
    return "<p>Nothing to see here. Move along.</p>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)