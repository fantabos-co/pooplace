import aiohttp
from praw import Reddit
import json
from time import time
from typing import List
import logging

from place.colors import RedditColor

def get_payload(x:int, y:int, c:int):
	return """{"operationName":"setPixel","variables":{"input":{"actionName":"r/replace:set_pixel","PixelMessageData":{"coordinate":{"x":%d,"y":%d},"colorIndex":%d,"canvasIndex":%d}}},"query":"mutation setPixel($input: ActInput!) {\\n act(input: $input) {\\n data {\\n ... on BasicMessage {\\n id\\n data {\\n ... on GetUserCooldownResponseMessageData {\\n nextAvailablePixelTimestamp\\n __typename\\n }\\n ... on SetPixelResponseMessageData {\\n timestamp\\n __typename\\n }\\n __typename\\n }\\n __typename\\n }\\n __typename\\n }\\n __typename\\n }\\n}\\n"}""" % (x, y, c, 0)

_ALL_SCOPES = ["account", "creddits", "edit", "flair", "history", "identity", "livemanage", "modconfig", "modcontributors", "modflair", "modlog", "modmail", "modnote", "modothers", "modposts", "modself", "modwiki", "mysubreddits", "privatemessages", "read", "report", "save", "structuredstyles", "submit", "subscribe", "vote", "wikiedit", "wikiread"]

class User:
	name : str
	token : str
	_next_time : int

	URL = "https://gql-realtime-2.reddit.com/query"

	def __init__(
		self,
		name:str,
		token:str
	):
		self.logger = logging.getLogger("user({username})")
		self.name = name
		self.token = token
		self._next_time = 0

	@classmethod
	def manual_login(
		cls,
		client_id:str,
		client_secret:str,
		redirect_uri:str,
		user_agent:str,
		scopes:List[str],
	) -> 'User':
		client = Reddit(
			client_id=client_id,
			client_secret=client_secret,
			user_agent=user_agent,
			redirect_uri=redirect_uri,
		)

		print("> go to this url and login")
		print(client.auth.url(
			scopes=scopes,
			state="fuck you",
		))
		code = input("code > ")
		client.auth.authorize(code)
		token = client._authorized_core._authorizer.access_token

		return cls(
			"manual",
			token,
		)


	@property
	def headers(self):
		return {
			"accept": "*/*",
			"apollographql-client-name": "mona-lisa",
			"apollographql-client-version": "0.0.1",
			"authorization": f"Bearer {self.token}",
			"content-type": "application/json",
			"sec-fetch-dest": "empty",
			"sec-fetch-mode": "cors",
			"sec-fetch-site": "same-site",
		}

	
	@property
	def cooldown(self):
		return self._next_time - time()

	async def put(self, color:int, x:int, y:int) -> bool:
		self.logger.info("putting [%d] at %d|%d", color, x, y)
		async with aiohttp.ClientSession() as sess:
			async with sess.post(self.URL, headers=self.headers, data=get_payload(x=x, y=y, c=color)) as res:
				answ = await res.json()
				self.logger.debug("set-pixel response: %s", str(answ))
		if "data" in answ and answ['data']:
			for act in answ["data"]["act"]["data"]:
				if "nextAvailablePixelTimestamp" in act['data']:
					self._next_time = act['data']['nextAvailablePixelTimestamp']
					return True
		if "errors" in answ and answ['errors']:
			for err in answ['errors']:
				if 'extensions' in err:
					if 'nextAvailablePixelTs' in err['extensions']:
						self._next_time = err['extensions']['nextAvailablePixelTs'] / 1000
						return False

class Pool:
	users : List[User]

	def __init__(self):
		self.users = list()

	def __iter__(self):
		return iter(self.users)

	def __len__(self):
		return len(self.users)

	@property
	def any(self) -> bool:
		return any(u.cooldown <= 0 for u in self)

	def best(self) -> User:
		"""Returns the user with the shortest cooldown (or no cooldown at all)"""
		cd = None
		usr = None
		for u in self:
			if u.cooldown <= 0:
				return u
			if cd is None or u.cooldown < cd:
				cd = u.cooldown
				usr = u
		return usr

	def add_user(self, u:User):
		self.users.append(u)

	def remove_user(self, n:str):
		users = [u for u in users if u.name != n]
		
	async def put(self, color:RedditColor, x:int, y:int):
		for u in self.users:
			if u.cooldown <= 0:
				await u.put(color, x, y)
				return True
		return False
