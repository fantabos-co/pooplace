import asyncio
import logging
import numpy as np

from time import time
from typing import List
from dataclasses import dataclass

from aioconsole import ainput
from quart import Quart, request

from place.board import PixelMap
from place.user import Pool, User
from place.colors import RedditColor
from place.webform import LANDING, FORM_OK

MAP_UPDATE_INTERVAL = 60 #Will request a map update every MAP_UPDATE_INTERVAL seconds
CLIENT_ID = ""
CLIENT_SECRET = ""
REDIRECT_URI = "https://fantabos.co/msauth"

logger = logging.getLogger(__file__)

APP = Quart(__name__)
POOL = Pool()

@APP.route("/", methods=["GET"])
async def landing():
	return LANDING

@APP.route("/", methods=["POST"])
async def form_data():
	form = await request.form
	POOL.add_user(User(form['username'], form['token']))
	logging.info("received user from web app : %s", form['username'])
	return FORM_OK

async def process_board(users: Pool, pixels: np.ndarray, oX:int, oY:int, board: PixelMap) -> int:
	size = pixels.shape
	count = 0
	for px in range(size[0]):
		for py in range(size[1]):
			if board[oX + px][oY + py] != pixels[px][py]:
				# get shortest cooldown in pool
				usr = users.best()
				if usr.cooldown > 0:
					return count
				# try to fill this pixel
				if await usr.put(pixels[px][py], oX + px, oY + py):
					count += 1
	return count

async def run(users: Pool, pixels: np.ndarray, oX:int, oY:int, board: PixelMap):
	last_sync = 0
	while True:
		if len(users) <= 0:
			logger.warn("no available users")
			await asyncio.sleep(60)
			continue
		usr = users.best()
		if usr.cooldown > 0:
			logger.info("sleeping %d", usr.cooldown)
			await asyncio.sleep(usr.cooldown)
		if time() - last_sync > MAP_UPDATE_INTERVAL:
			await board.fetch(usr.token) #doesnt matter whose token we use
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

async def main():
	board = PixelMap()
	pixels = np.loadtxt("input.txt", dtype='int32')
	offsetX = int(sys.argv[1])
	offsetY = int(sys.argv[2])

	loop = asyncio.get_event_loop()

	board_task = loop.create_task(run(POOL, pixels, offsetX, offsetY, board))
	users_task = loop.create_task(gen_users(POOL))

	APP.run(host="127.0.0.1", port=42069, loop=loop)

	# await asyncio.gather(board_task, users_task)
	board_task = asyncio.get_event_loop().create_task(run(pool, pixels, offsetX, offsetY, board))
	users_task = asyncio.get_event_loop().create_task(gen_users(pool))

	await asyncio.gather(board_task, users_task)

	# await u.put(RedditColor.TEST, 320, 350)

	# await board.fetch(u.token)

	# print(board.board.shape)
	# np.savetxt("board.txt", board.board, fmt='%d')

if __name__ == "__main__":
	import logging
	import sys
	logging.basicConfig(level=logging.DEBUG)

	asyncio.run(main())
