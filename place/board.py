import json
from io import BytesIO
import os
from PIL import Image
import numpy as np
import websocket
import aiohttp
import logging

from place.user import UnauthorizedError

HEIGHT = 1000
WIDTH = 2000

class PixelMap:
	board : np.ndarray
	
	def __init__(self):
		self.board = np.zeros((HEIGHT, WIDTH), dtype="int32")
		self.logger = logging.getLogger("PixelMap")

	def __getitem__(self, key):
		return self.board[key]

	async def fetch(self, token:str, attempts:int = 100): #credits: https://github.com/rdeepak2002/reddit-place-script-2022
		self.logger.info("fetching board")

		ws = websocket.create_connection(
			"wss://gql-realtime-2.reddit.com/query", origin="https://hot-potato.reddit.com"
		)
		ws.send(
			json.dumps(
				{
					"type": "connection_init",
					"payload": {"Authorization": "Bearer " + token},
				}
			)
		)
		data = json.loads(ws.recv())
		self.logger.debug(str(data))
		if 'payload' in data and data['payload']['message'].startswith('401'):
			raise UnauthorizedError(str(data))

		ws.send(
			json.dumps(
				{
					"id": "1",
					"type": "start",
					"payload": {
						"variables": {
							"input": {
								"channel": {
									"teamOwner": "AFD2022",
									"category": "CONFIG",
								}
							}
						},
						"extensions": {},
						"operationName": "configuration",
						"query": "subscription configuration($input: SubscribeInput!) {\n  subscribe(input: $input) {\n    id\n    ... on BasicMessage {\n      data {\n        __typename\n        ... on ConfigurationMessageData {\n          colorPalette {\n            colors {\n              hex\n              index\n              __typename\n            }\n            __typename\n          }\n          canvasConfigurations {\n            index\n            dx\n            dy\n            __typename\n          }\n          canvasWidth\n          canvasHeight\n          __typename\n        }\n      }\n      __typename\n    }\n    __typename\n  }\n}\n",
					},
				}
			)
		)
		try:
			data = json.loads(ws.recv())
			self.logger.debug(data)
			if 'payload' in data and data['payload']['message'].startswith('401'):
				raise UnauthorizedError(str(data))
		except json.decoder.JSONDecodeError:
			raise UnauthorizedError(str(data))
		ws.send(
			json.dumps(
				{
					"id": "2",
					"type": "start",
					"payload": {
						"variables": {
							"input": {
								"channel": {
									"teamOwner": "AFD2022",
									"category": "CANVAS",
									"tag": "0",
								}
							}
						},
						"extensions": {},
						"operationName": "replace",
						"query": "subscription replace($input: SubscribeInput!) {\n  subscribe(input: $input) {\n    id\n    ... on BasicMessage {\n      data {\n        __typename\n        ... on FullFrameMessageData {\n          __typename\n          name\n          timestamp\n        }\n        ... on DiffFrameMessageData {\n          __typename\n          name\n          currentTimestamp\n          previousTimestamp\n        }\n      }\n      __typename\n    }\n    __typename\n  }\n}\n",
					},
				}
			)
		)

		file = ""
		for _i in range(attempts):
			temp = json.loads(ws.recv())
			self.logger.debug(data)
			if 'payload' in data and data['payload']['message'].startswith('401'):
				raise UnauthorizedError(str(data))
			if temp["type"] == "data":
				msg = temp["payload"]["data"]["subscribe"]
				if msg["data"]["__typename"] == "FullFrameMessageData":
					file = msg["data"]["name"]
					break

		ws.close()

		async with aiohttp.ClientSession() as sess:
			async with sess.get(file) as res:
				file_data = BytesIO(await res.read())

		file_data.seek(0)
		image = Image.open(file_data)

		self.board = np.subtract(np.array(image, dtype='int32'), 1)
		self.logger.info("downloaded board : %s", file)
		os.remove("board.txt")
		np.savetxt("board.txt", self.board, fmt="%d")
