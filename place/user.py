import os
import aiohttp
from praw import reddit
from aioauth_client import OAuth2Client #https://aliev.me/aioauth
import rauth
import json
from time import time
from typing import List, Optional
import logging

from aioconsole import ainput
from place.colors import RedditColor

def get_payload(x:int, y:int, c:int):
	return """{"operationName":"setPixel","variables":{"input":{"actionName":"r/replace:set_pixel","PixelMessageData":{"coordinate":{"x":%d,"y":%d},"colorIndex":%d,"canvasIndex":%d}}},"query":"mutation setPixel($input: ActInput!) {\\n act(input: $input) {\\n data {\\n ... on BasicMessage {\\n id\\n data {\\n ... on GetUserCooldownResponseMessageData {\\n nextAvailablePixelTimestamp\\n __typename\\n }\\n ... on SetPixelResponseMessageData {\\n timestamp\\n __typename\\n }\\n __typename\\n }\\n __typename\\n }\\n __typename\\n }\\n __typename\\n }\\n}\\n"}""" % (x, y, c, 0)

_ALL_SCOPES = ["account", "creddits", "edit", "flair", "history", "identity", "livemanage", "modconfig", "modcontributors", "modflair", "modlog", "modmail", "modnote", "modothers", "modposts", "modself", "modwiki", "mysubreddits", "privatemessages", "read", "report", "save", "structuredstyles", "submit", "subscribe", "vote", "wikiedit", "wikiread"]

class UnauthorizedError(Exception):
	pass

class User:
	name : str
	token : str
	refresh : Optional[str]
	next : Optional[int]

	URL = "https://gql-realtime-2.reddit.com/query"

	def __init__(
		self,
		name:str,
		token:str,
		refresh:Optional[str] = None,
		next:Optional[int] = None,
	):
		self.logger = logging.getLogger(f"user({name})")
		self.name = name
		self.token = token
		self.refresh = refresh
		self.next = next

	def as_dict(self):
		return {
			"name": self.name,
			"token": self.token,
			"refresh": self.refresh or "null",
			"next": self.next or "null"
		}

	def __str__(self):
		return json.dumps(self.as_dict())

	async def refresh(self):
		if not self.refresh or self.refresh == "null": # TODO remove literal 'null'
			raise UnauthorizedError("No refresh token")
		async with aiohttp.ClientSession() as sess:
			async with sess.post(
				"https://www.reddit.com/api/v1/access_token",
				data={"grant_type":"refresh_token", "refresh_token":self.refresh}
			) as res:
				data = await res.json()
				self.token = data['access_token']

	@classmethod
	async def manual_login(
		cls,
		client_id:str,
		client_secret:str,
		redirect_uri:str,
		user_agent:str,
		scopes:List[str],
	) -> 'User':
		client = OAuth2Client(
			client_id=client_id,
			client_secret=client_secret,
			authorize_url=redirect_uri,
		)
		print("> go to this url and login")
		print(await client.get_authorize_url(
			scopes=scopes,
			state="ifthereisafloodofnewplayers",
		))
		code = ainput("code > ")
		token, provider = await client.get_access_token(code, redirect_uri=redirect_uri)

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
		return (self.next or 0) - time()

	async def put(self, color:int, x:int, y:int) -> bool:
		self.logger.info("putting [%s] at %d|%d", RedditColor(color), x, y)
		async with aiohttp.ClientSession() as sess:
			async with sess.post(self.URL, headers=self.headers, data=get_payload(x=x, y=y, c=color)) as res:
				answ = await res.json()
				self.logger.debug("set-pixel response: %s", str(answ))
		if 'success' in answ and not answ['success'] \
		and 'error' in answ and answ['error'] \
		and 'reason' in answ['error'] and answ['error']['reason'] == 'UNAUTHORIZED':
			raise UnauthorizedError(str(answ))
		if "data" in answ and answ['data']:
			for act in answ["data"]["act"]["data"]:
				if "nextAvailablePixelTimestamp" in act['data']:
					self.next = act['data']['nextAvailablePixelTimestamp'] / 1000
					if self.next - time() > 60 * 60 * 24 * 31:
						raise UnauthorizedError("Rate limited: cooldown too long")
					return True
		if "errors" in answ and answ['errors']:
			for err in answ['errors']:
				if 'extensions' in err:
					if 'nextAvailablePixelTs' in err['extensions']:
						self.next = err['extensions']['nextAvailablePixelTs'] / 1000
						return False

class Pool:
	users : List[User]

	def __init__(self, storage="pool.json"):
		self.users = list()
		if os.path.isfile(storage):
			with open(storage) as f:
				data = json.load(f)
			for el in data:
				self.users.append(
					User(
						el["name"],
						el["token"],
						el["refresh"] if "refresh" in el and el["refresh"] != "null" else None,
						el["next"] if "next" in el and el["next"] != "null" else None,
					)
				)

	def __iter__(self):
		return iter(self.users)

	def __len__(self):
		return len(self.users)

	def serialize(self, storage="pool.json"):
		with open(storage, "w") as f:
			json.dump([ u.as_dict() for u in self.users ], f, default=str, indent=2)

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
		self.serialize()

	def remove_user(self, n:str):
		self.users = [u for u in self.users if u.name != n]
		self.serialize()
		
	async def put(self, color:RedditColor, x:int, y:int):
		for u in self.users:
			if u.cooldown <= 0:
				await u.put(color, x, y)
				return True
		return False
