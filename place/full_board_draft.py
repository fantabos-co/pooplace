import time
from PIL import Image
import json
from websocket import create_connection
from io import BytesIO
import logging
import asyncio
import aiohttp
import requests
import numpy as np

from websocket import create_connection
from websocket._exceptions import WebSocketConnectionClosedException

from place.user import User
from place.static.query import CFG_QUERY, REP_QUERY
from place.colors import RedditColor
from place.user import UnauthorizedError

logger = logging.getLogger()

def get_board(access_token_in):
	logger.debug("Connecting and obtaining board images")
	while True:
		try:
			ws = create_connection(
				"wss://gql-realtime-2.reddit.com/query",
				origin="https://hot-potato.reddit.com",
			)
			break
		except Exception:
			logger.error(
				"Failed to connect to websocket, trying again in 30 seconds..."
			)
			time.sleep(30)
	ws.send(
		json.dumps(
			{
				"type": "connection_init",
				"payload": {"Authorization": "Bearer " + access_token_in},
			}
		)
	)
	while True:
		try:
			msg = ws.recv()
		except WebSocketConnectionClosedException as e:
			raise UnauthorizedError("socket already closed", refreshable=True)
		if msg is None:
			logger.error("Reddit failed to acknowledge connection_init")
			exit()
		if msg.startswith('{"type":"connection_ack"}'):
			logger.debug("Connected to WebSocket server")
			break
	logger.debug("Obtaining Canvas information")
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
					"query": CFG_QUERY
				},
			}
		)
	)
	while True:
		canvas_payload = json.loads(ws.recv())
		if canvas_payload["type"] == "data":
			canvas_details = canvas_payload["payload"]["data"]["subscribe"]["data"]
			logger.debug("Canvas config: {}", canvas_payload)
			break
	canvas_sockets = []
	canvas_count = len(canvas_details["canvasConfigurations"])
	for i in range(0, canvas_count):
		canvas_sockets.append(2 + i)
		logger.debug("Creating canvas socket {}", canvas_sockets[i])
		ws.send(
			json.dumps(
				{
					"id": str(2 + i),
					"type": "start",
					"payload": {
						"variables": {
							"input": {
								"channel": {
									"teamOwner": "AFD2022",
									"category": "CANVAS",
									"tag": str(i),
								}
							}
						},
						"extensions": {},
						"operationName": "replace",
						"query": REP_QUERY
					},
				}
			)
		)
	imgs = []
	logger.debug("A total of {} canvas sockets opened", len(canvas_sockets))
	while len(canvas_sockets) > 0:
		temp = json.loads(ws.recv())
		logger.debug("Waiting for WebSocket message")
		if temp["type"] == "data":
			logger.debug("Received WebSocket data type message")
			msg = temp["payload"]["data"]["subscribe"]
			if msg["data"]["__typename"] == "FullFrameMessageData":
				logger.debug("Received full frame message")
				img_id = int(temp["id"])
				logger.debug("Image ID: {}", img_id)
				if img_id in canvas_sockets:
					logger.debug("Getting image: {}", msg["data"]["name"])
					imgs.append(Image.open(
								BytesIO(
									requests.get(
										msg["data"]["name"],
										stream=True,
									).content
								)
							)
					)

					canvas_sockets.remove(img_id)
					logger.debug(
						"Canvas sockets remaining: {}", len(canvas_sockets)
					)	
	for i in range(0, canvas_count - 1): #wtf is this
		ws.send(json.dumps({"id": str(2 + i), "type": "stop"}))
	ws.close()

	board=np.stack(
		(
			np.stack((imgs[0], imgs[1]), axis=1), 
			np.stack((imgs[2], imgs[3]), axis=1)
		), axis=0
	)

logging.basicConfig(level=logging.DEBUG)