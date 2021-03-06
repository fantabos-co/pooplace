import os
import aiohttp
import json
from time import time
from typing import List, Optional
import logging
from uuid import uuid4

from aioconsole import ainput
from place.colors import RedditColor
from ..controller import CLIENT_ID, CLIENT_SECRET, USER_AGENT

def get_payload(x:int, y:int, c:int):
	return """{"operationName":"setPixel","variables":{"input":{"actionName":"r/replace:set_pixel","PixelMessageData":{"coordinate":{"x":%d,"y":%d},"colorIndex":%d,"canvasIndex":%d}}},"query":"mutation setPixel($input: ActInput!) {\\n act(input: $input) {\\n data {\\n ... on BasicMessage {\\n id\\n data {\\n ... on GetUserCooldownResponseMessageData {\\n nextAvailablePixelTimestamp\\n __typename\\n }\\n ... on SetPixelResponseMessageData {\\n timestamp\\n __typename\\n }\\n __typename\\n }\\n __typename\\n }\\n __typename\\n }\\n __typename\\n }\\n}\\n"}""" % (x, y, c, 0)

class UnauthorizedError(Exception):
	refreshable : bool
	def __init__(self, message:str, refreshable:bool=True):
		super().__init__(message)
		self.refreshable = refreshable

class User:
	id : str
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
		id:Optional[str] = None,
	):
		self.id = id or str(uuid4())
		self.logger = logging.getLogger(f"user({name})")
		self.name = name
		self.token = token
		self.refresh = refresh
		self.next = next

	def as_dict(self):
		return {
			"id": self.id,
			"name": self.name,
			"token": self.token,
			"refresh": self.refresh or None,
			"next": self.next or None
		}

	def __str__(self):
		return json.dumps(self.as_dict())

	async def get_username(self):
		async with aiohttp.ClientSession() as sess:
			async with sess.get(
				"https://oauth.reddit.com/api/v1/me",
				headers={"User-Agent": USER_AGENT, "Authorization": f"bearer {self.token}"},
			) as res:
				data = await res.json()
		self.name = data['subreddit']['display_name_prefixed']
		return self.name

	async def refresh_token(self):
		if not self.refresh or self.refresh == "null": # TODO remove literal 'null'
			self.logger.debug("could not fine refresh token for %s", self.name)
			raise UnauthorizedError("No refresh token")
		gayson = {
			'grant_type': 'refresh_token',
			'refresh_token': self.refresh
		}
		async with aiohttp.ClientSession() as sess:
			async with sess.post(
				"https://www.reddit.com/api/v1/access_token",
				data=gayson,
				headers={'User-Agent': USER_AGENT},
				auth=aiohttp.BasicAuth(login=CLIENT_ID, password=CLIENT_SECRET),
			) as res:
				data = await res.json()
				self.logger.debug(data)
				self.token = data['access_token']
		await self.get_username() # make sure new token is valid
		self.logger.info(f"refreshed user {self.name}")
		
	@property
	def headers(self):
		return { #the header is stolen from the other bot, so we saw it fitting to reuse their client name.
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
					if self.next and self.next - time() > 60 * 60 * 24 * 31:
						raise UnauthorizedError("Rate limited: cooldown too long", refreshable=False)
					return True
		if "errors" in answ and answ['errors']:
			for err in answ['errors']:
				if 'extensions' in err:
					if 'nextAvailablePixelTs' in err['extensions']:
						self.next = err['extensions']['nextAvailablePixelTs'] / 1000
						if self.next and self.next - time() > 60 * 60 * 24 * 31:
							raise UnauthorizedError("Rate limited: cooldown too long", refreshable=False)
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
						id=el["id"] if "id" in el else None,
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

	@property
	def ready(self) -> int:
		"""Returns how many users are ready to place"""
		return sum(1 for u in self.users if u.cooldown <= 0)

	def best(self) -> User:
		"""Returns the user with the shortest cooldown"""
		cd = None
		usr = None
		for u in self:
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