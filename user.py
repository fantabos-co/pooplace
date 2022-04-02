import requests
from praw import Reddit
import json
from time import time

def test_payload(x:int, y:int, c:int):
	return """{"operationName":"setPixel","variables":{"input":{"actionName":"r/replace:set_pixel","PixelMessageData":{"coordinate":{"x":%d,"y":%d},"colorIndex":%d,"canvasIndex":0}}},"query":"mutation setPixel($input: ActInput!) {\\n act(input: $input) {\\n data {\\n ... on BasicMessage {\\n id\\n data {\\n ... on GetUserCooldownResponseMessageData {\\n nextAvailablePixelTimestamp\\n __typename\\n }\\n ... on SetPixelResponseMessageData {\\n timestamp\\n __typename\\n }\\n __typename\\n }\\n __typename\\n }\\n __typename\\n }\\n __typename\\n }\\n}\\n"}""" % (x, y, c)

def test_user():
	return User(
		client_id="wLPQSYwEJdUXfnrXTsUyfQ",
		client_secret="YfpikK-FvwBc_D7929X4MoXJv2bo5w",
		username="Brilliant_Ad686",
		password="ballsack",
		user_agent="python:placebot:v1.0",
		redirect_uri="https://fantabos.co/msauth"
	)

class User:
	name : str
	client : Reddit
	token : str
	headers: dict
	_next_time : int

	URL = "https://gql-realtime-2.reddit.com/query"

	@staticmethod
	def get_payload(color:int, x:int, y:int): #this is broken for some reason, we didnt have time to investigate further
		return json.dumps({
			"operationName":"setPixel",
			"variables": {
				"input": {
					"actionName":"r/replace:set_pixel",
					"PixelMessageData": {
						"coordinate": {
							"x": x,
							"y": y
						},
						"colorIndex": color,
						"canvasIndex": 0
					}
				}
			},
			"query": "mutation setPixel($input: ActInput!) {\\n act(input: $input) {\\n data {\\n ... on BasicMessage {\\n id\\n data {\\n ... on GetUserCooldownResponseMessageData {\\n nextAvailablePixelTimestamp\\n __typename\\n }\\n ... on SetPixelResponseMessageData {\\n timestamp\\n __typename\\n }\\n __typename\\n }\\n __typename\\n }\\n __typename\\n }\\n __typename\\n }\\n}\\n"
		})

	def __init__(
		self,
		client_id:str,
		client_secret:str,
		username:str,
		password:str,
		redirect_uri:str,
		user_agent:str
	):
		self.name = username
		self.client = Reddit(
			client_id=client_id,
			client_secret=client_secret,
			username=username,
			password=password,
			user_agent=user_agent,
			redirect_uri=redirect_uri,
		)

		print("> go to this url and login")
		print(self.client.auth.url(
			scopes=["account", "creddits", "edit", "flair", "history", "identity", "livemanage", "modconfig", "modcontributors", "modflair", "modlog", "modmail", "modnote", "modothers", "modposts", "modself", "modwiki", "mysubreddits", "privatemessages", "read", "report", "save", "structuredstyles", "submit", "subscribe", "vote", "wikiedit", "wikiread"],
			state="fuck you",
		))
		code = input("code > ")
		self.client.auth.authorize(code)
		self.token = self.client._authorized_core._authorizer.access_token
		self.headers = {
			"accept": "*/*",
			"apollographql-client-name": "mona-lisa",
			"apollographql-client-version": "0.0.1",
			"authorization": f"Bearer {self.token}",
			"content-type": "application/json",
			"sec-fetch-dest": "empty",
			"sec-fetch-mode": "cors",
			"sec-fetch-site": "same-site",
		}
		self._next_time = 0
	
	@property
	def cooldown(self):
		return self._next_time - time()

	def put(self, color: int, x:int, y:int):
		r = requests.post(self.URL, headers=self.headers, data=fucking_payload(x=x, y=y, c=color))
		print(r.text)
		answ = r.json()
		if "errors" in answ:
			for err in answ['errors']:
				if 'extensions' in err:
					if 'nextAvailablePixelTs' in err['extensions']:
						self._next_time = err['extensions']['nextAvailablePixelTs'] / 1000
						return self._next_time