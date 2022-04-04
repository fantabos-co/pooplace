import asyncio
import logging
import numpy as np

from logging import StreamHandler, getLogger, Formatter, LogRecord, DEBUG, INFO, WARNING, ERROR, CRITICAL
from logging.handlers import RotatingFileHandler
from termcolor import colored

from typing import Dict
from time import time
from uuid import uuid4
import json

import aiohttp
import rauth
from rauth.service import OAuth2Service, process_token_request
from aioconsole import ainput
from quart import Quart, request, redirect
from quart.logging import default_handler, serving_handler

from place.board import PixelMap
from place.user import Pool, UnauthorizedError, User
from place.static.webform import LANDING, FORM_OK, FORM_NOK

class RefreshableOAuth2Service(OAuth2Service):
	def get_access_token(self,
						 method='POST',
						 decoder=rauth.utils.parse_utf8_qsl,
						 key=None,
						 **kwargs):
		r = self.get_raw_access_token(method, **kwargs)
		access_token, refresh_token = process_token_request(r, decoder, *(key or ["access_token", "refresh_token"]))
		return access_token, refresh_token

DISPATCHER_MAX_SLEEP = 60
MAP_UPDATE_INTERVAL = 15 #Will request a map update every MAP_UPDATE_INTERVAL seconds
CLIENT_ID = "3031IeKHSaGKW8xyWyYdrA"
CLIENT_SECRET = "WIjkxcenQttaXKGRXbL1o1jWpUxIpw"
REDIRECT_URI = "https://pooblic.org/place"

CLIENT = RefreshableOAuth2Service(
	name="reddit",
	client_id=CLIENT_ID,
	client_secret=CLIENT_SECRET,
	access_token_url="https://ssl.reddit.com/api/v1/access_token",
	authorize_url="https://ssl.reddit.com/api/v1/authorize"
)

logger = logging.getLogger(__file__)

APP = Quart(__name__)
POOL = Pool()

logging.getLogger('quart.app').removeHandler(default_handler)
logging.getLogger('quart.app').removeHandler(serving_handler)

@APP.route("/", methods=["GET"])
async def landing():
	if 'code' in request.args:
		# user = "unk" #TODO fetch acc name	
		# when user is redirected back after authorizing:
		code = request.args["code"]
		try:
			# session = CLIENT.get_auth_session(data={"code":code, "grant_type":"authorization_code", "redirect_uri":REDIRECT_URI})
			# response = session.access_token
			# sess
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
			u = User(str(uuid4()), access_token, refresh_token)
			POOL.add_user(u)
			logging.info("received user from web app : %s", u)
			return FORM_OK
		except KeyError as e:
			logging.warning("failed to get access token : %s", str(e))
			return FORM_NOK
	else:
		return LANDING.format(users=len(POOL))

@APP.route("/auth", methods=["GET"])
async def auth_url():
		# return LANDING
		authorize_url = CLIENT.get_authorize_url(
			response_type="code",
			scope="identity",
			state=str(uuid4()),
			redirect_uri=REDIRECT_URI,
			duration='permanent',
		)
		return redirect(authorize_url)

async def process_board(users: Pool, pixels: np.ndarray, oX:int, oY:int, board: PixelMap) -> int:
	size = pixels.shape
	count = 0
	for px in range(size[1]):
		for py in range(size[0]):
			if pixels[py][px] == -1:
				continue
			if board[oY + py][oX + px] != pixels[py][px]:
				logger.debug(f"comparing {oX+px}, {oY+py} with {px}, {py}")
			# get shortest cooldown in pool
				usr = users.best()
				if usr.cooldown > 0:
					return count
				# try to fill this pixel
				try:
					if await usr.put(pixels[py][px], oX + px, oY + py):
						count += 1
				except UnauthorizedError as e:
					logger.error("Unauthorized %s : %s [%s]", usr.name, usr.token, str(e))
					try:
						await usr.refresh_token()
						POOL.serialize()
					except Exception:
						logger.exception("Failed to refresh user %s", usr)
						users.remove_user(usr.name)
					return count
	return count

async def run(users: Pool, pixels: np.ndarray, oX:int, oY:int, board: PixelMap):
	last_sync = 0
	while True:
		try:
			if len(users) <= 0:
				logger.warning("no available users")
				await asyncio.sleep(10)
				continue
			usr = users.best()
			if usr.cooldown > 0:
				actual_sleep = min(usr.cooldown, DISPATCHER_MAX_SLEEP)
				logger.info("sleeping %d (%d)", actual_sleep, usr.cooldown)
				await asyncio.sleep(actual_sleep)

				continue
			if time() - last_sync > MAP_UPDATE_INTERVAL:
				try:
					await board.fetch(usr.token) #doesnt matter whose token we use
				except UnauthorizedError as e:
					logger.error("Unauthorized %s : %s [%s]", usr.name, usr.token, str(e))
					try:
						await usr.refresh_token()
						POOL.serialize()
					except Exception:
						logger.exception("Failed to refresh user %s", usr)
						users.remove_user(usr.name)
						continue
				last_sync = time()
			modified = await process_board(users, pixels, oX, oY, board)
			POOL.serialize()
			logger.info("changed %d pixels", modified)
			if modified <= 0:
				await asyncio.sleep(MAP_UPDATE_INTERVAL - (time() - last_sync)) #sleep for 1 second if nothing happened
		except Exception:
			logger.exception("uncaught exception")
			await asyncio.sleep(5)

async def gen_users(users: Pool):
	while True:
		_ = await ainput("|login?>")

		name = await ainput("|name> ")
		token = await ainput("|token> ")

		users.add_user(User(name, token))


class ColorFormatter(Formatter):
	def __init__(self, fmt:str):
		self.fmt : str = fmt
		self.formatters : Dict[int, Formatter] = {
			DEBUG: Formatter(colored(fmt, color='grey')),
			INFO: Formatter(colored(fmt)),
			WARNING: Formatter(colored(fmt, color='yellow')),
			ERROR: Formatter(colored(fmt, color='red')),
			CRITICAL: Formatter(colored(fmt, color='red', attrs=['bold'])),
		}

	def format(self, record:LogRecord) -> str:
		if record.exc_text: # jank way to color the stacktrace but will do for now
			record.exc_text = colored(record.exc_text, color='grey', attrs=['bold'])
		fmt = self.formatters.get(record.levelno)
		if fmt:
			return fmt.format(record)
		return Formatter().format(record) # This should never happen!

def setup_logging(name:str, color:bool=True, level=INFO) -> None:
	logger = getLogger()
	logger.setLevel(level)
	# create file handler which logs even debug messages
	fh = RotatingFileHandler(f'log/{name}.log', maxBytes=1048576, backupCount=5) # 1MB files
	fh.setLevel(level)
	# create console handler with a higher log level
	ch = StreamHandler()
	ch.setLevel(max(INFO, level)) # so we never show DEBUG on stdout
	# create formatter and add it to the handlers
	file_formatter = Formatter("[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s", "%b %d %Y %H:%M:%S")
	print_formatter = ColorFormatter("> %(message)s") if color else Formatter("> %(message)s")
	fh.setFormatter(file_formatter)
	ch.setFormatter(print_formatter)
	# add the handlers to the logger
	logger.addHandler(fh)
	logger.addHandler(ch)

if __name__ == "__main__":
	import logging
	import sys

	setup_logging("pooblic-placebot", level=DEBUG)

	board = PixelMap()
	pixels = np.loadtxt("input.txt", dtype='int32') # TODO invert x and y
	offsetX = int(sys.argv[1])
	offsetY = int(sys.argv[2])

	loop = asyncio.get_event_loop()

	board_task = loop.create_task(run(POOL, pixels, offsetX, offsetY, board))
	# users_task = loop.create_task(gen_users(POOL))

	APP.run(host="127.0.0.1", port=52691, loop=loop, use_reloader=False)
