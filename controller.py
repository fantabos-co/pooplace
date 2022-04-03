import asyncio
import logging
from aioauth_client import OAuth2Client
import numpy as np

from time import time
from uuid import uuid4

import rauth
from aioconsole import ainput
from quart import Quart, request, redirect

from place.board import PixelMap
from place.user import Pool, UnauthorizedError, User
from place.webform import LANDING, FORM_OK, FORM_NOK

MAP_UPDATE_INTERVAL = 60 #Will request a map update every MAP_UPDATE_INTERVAL seconds
CLIENT_ID = "wLPQSYwEJdUXfnrXTsUyfQ"
CLIENT_SECRET = "YfpikK-FvwBc_D7929X4MoXJv2bo5w"
REDIRECT_URI = "https://pooblic.org/place"

CLIENT = rauth.service.OAuth2Service(
	name="reddit",
	client_id=CLIENT_ID,
	client_secret=CLIENT_SECRET,
	access_token_url="https://ssl.reddit.com/api/v1/access_token",
	authorize_url="https://ssl.reddit.com/api/v1/authorize"
)

logger = logging.getLogger(__file__)

APP = Quart(__name__)
POOL = Pool()

@APP.route("/", methods=["GET"])
async def landing():
	if 'code' in request.args:
		user = "unk"	
		# when user is redirected back after authorizing:
		code = request.args["code"]
		try:
			response = CLIENT.get_access_token(
				auth=(CLIENT.client_id, CLIENT.client_secret),
				data=dict(
					grant_type="authorization_code",
					code=code,
					redirect_uri=REDIRECT_URI
				)
			)
			logger.info(str(response.content))
			token = response.content["access_token"]
			POOL.add_user(User(user, token))
			logging.info("received user from web app : %s", user)
			return FORM_OK
		except KeyError as e:
			logging.warning("failed to get access token : %s", str(e))
			return FORM_NOK
	else:
		# return LANDING
		authorize_url = CLIENT.get_authorize_url(
			response_type="code",
			scope="identity",
			state=str(uuid4()),
			redirect_uri=REDIRECT_URI
		)
		return redirect(authorize_url)

@APP.route("/", methods=["POST"])
async def form_data():
	if 'code' in request.args:
		user = "unk"	
		# when user is redirected back after authorizing:
		code = request.args["code"]
		try:
			response = CLIENT.get_access_token(
				auth=(CLIENT.client_id, CLIENT.client_secret),
				data=dict(
					grant_type="authorization_code",
					code=code,
					redirect_uri=REDIRECT_URI
				)
			)
			logger.debug(str(response.content))
			token = response.content["access_token"]
		except KeyError as e:
			logger.error("error getting access token : %s", str(e))
			return FORM_NOK
	else:
		form = await request.form
		user = form['username']
		token = form['token']

	POOL.add_user(User(user, token))
	logging.info("received user from web app : %s", user)
	return FORM_OK

async def process_board(users: Pool, pixels: np.ndarray, oX:int, oY:int, board: PixelMap) -> int:
	size = pixels.shape
	count = 0
	for px in range(size[0]):
		for py in range(size[1]):
			if pixels[px][py] == -1:
				continue
			if board[oX + px][oY + py] != pixels[px][py]:
				# get shortest cooldown in pool
				usr = users.best()
				if usr.cooldown > 0:
					return count
				# try to fill this pixel
				try:
					if await usr.put(pixels[px][py], oX + px, oY + py):
						count += 1
				except UnauthorizedError as e:
					logger.error("Unauthorized %s : %s [%s]", usr.name, usr.token, str(e))
					users.remove_user(usr.name)
					return count
	return count

async def run(users: Pool, pixels: np.ndarray, oX:int, oY:int, board: PixelMap):
	last_sync = 0
	while True:
		if len(users) <= 0:
			logger.warning("no available users")
			await asyncio.sleep(60)
			continue
		usr = users.best()
		if usr.cooldown > 0:
			logger.info("sleeping %d", usr.cooldown)
			await asyncio.sleep(usr.cooldown)
		if time() - last_sync > MAP_UPDATE_INTERVAL:
			try:
				await board.fetch(usr.token) #doesnt matter whose token we use
			except UnauthorizedError as e:
				logger.error("Unauthorized %s : %s [%s]", usr.name, usr.token, str(e))
				users.remove_user(usr.name)
				continue
			last_sync = time()
		modified = await process_board(users, pixels, oX, oY, board)
		logger.info("changed %d pixels", modified)
		if modified <= 0:
			await asyncio.sleep(1) #sleep for 1 second if nothing happened

async def gen_users(users: Pool):
	while True:
		_ = await ainput("|login?>")

		name = await ainput("|name> ")
		token = await ainput("|token> ")

		users.add_user(User(name, token))

if __name__ == "__main__":
	import logging
	import sys
	logging.basicConfig(level=logging.DEBUG)

	print(CLIENT.get_authorize_url(
		scopes=['identity'],
		state="ifthereisafloodofnewplayers",
	))

	board = PixelMap()
	pixels = np.loadtxt("input.txt", dtype='int32')
	offsetX = int(sys.argv[1])
	offsetY = int(sys.argv[2])

	loop = asyncio.get_event_loop()

	board_task = loop.create_task(run(POOL, pixels, offsetX, offsetY, board))
	users_task = loop.create_task(gen_users(POOL))

	APP.run(host="127.0.0.1", port=52691, loop=loop)

	# https://www.reddit.com/api/v1/authorize?client_id=wLPQSYwEJdUXfnrXTsUyfQ&duration=permanent&redirect_uri=https%3A%2F%2Fpooblic.org%2Fplace&response_type=code&scope=identity&state=ifthereisafloodofnewplayers
