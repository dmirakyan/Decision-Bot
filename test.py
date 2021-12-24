import os
from slack_sdk import WebClient 
from slack_sdk.errors import SlackApiError 

slack_token = 'xoxb-2275183503-2822568687904-VGTCw4haGfSiDRYOG08wDUR5'

client = WebClient(token=slack_token)
client.chat_postMessage(channel="bad-ideas",text="I'm a real boy!")