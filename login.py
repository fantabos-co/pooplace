import asyncio
import logging
from place.user import User

ID = "wLPQSYwEJdUXfnrXTsUyfQ"
SECRET = "YfpikK-FvwBc_D7929X4MoXJv2bo5w"

async def main():
	u = User.manual_login(
		client_id="wLPQSYwEJdUXfnrXTsUyfQ",
		client_secret="YfpikK-FvwBc_D7929X4MoXJv2bo5w",
		user_agent="python:placebot:v1.0",
		redirect_uri="https://pooblic.org/place",
		scopes=['identity'],
	)

	print(f"> logged in : {u.token}")

	x = 320
	y = 320
	c = 27

	await u.put(c, x, y)

	await asyncio.sleep(2)
	print("> bye")

logging.basicConfig(level=logging.DEBUG)
asyncio.run(main())