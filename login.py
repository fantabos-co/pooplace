import asyncio
import json
from uuid import uuid4

from controller import RefreshableOAuth2Service

import aiohttp

CLIENT_ID = "TM-OCvEMWrOCGFiGnI2qTg"
CLIENT_SECRET = "PzNdWD2UJaUD5yiaLUwOj_9gXcHpfg"
REDIRECT_URI = "https://fantabos.co/msauth"

CLIENT = RefreshableOAuth2Service(
	name="reddit",
	client_id=CLIENT_ID,
	client_secret=CLIENT_SECRET,
	access_token_url="https://ssl.reddit.com/api/v1/access_token",
	authorize_url="https://ssl.reddit.com/api/v1/authorize"
)

authorize_url = CLIENT.get_authorize_url(
	response_type="code",
	scope="identity",
	state=str(uuid4()),
	redirect_uri=REDIRECT_URI,
	duration='permanent',
)

print("Go to this url and login, copy resulting code")
print(authorize_url)
code = input("code > ")

access_token, refresh_token = CLIENT.get_access_token(
	auth=(CLIENT.client_id, CLIENT.client_secret),
	data=dict(
		grant_type="authorization_code",
		code=code,
		redirect_uri=REDIRECT_URI
	),
	headers={'User-Agent': 'python:placepoop:1.0 (by /u/Exact_Worldliness265)'},
	decoder=json.loads				
)

async def username(token):
	async with aiohttp.ClientSession() as sess:
		async with sess.get(
			"https://oauth.reddit.com/api/v1/me",
			headers={"User-Agent": "python:placepoop:1.0 (by /u/Exact_Worldliness265)", "Authorization": f"bearer {token}"},
		) as res:
			data = await res.json()
			print(json.dumps(data, indent=2))
	return data['display_name_prefixed']

uname = asyncio.run(username(access_token))

print(f"Your username is {uname}")