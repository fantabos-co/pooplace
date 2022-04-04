import time
from PIL import Image
import json
from websocket import create_connection
from io import BytesIO
import logging
import aiohttp

logger = logging.getLogger(_)

async def get_board(access_token_in):
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
		msg = ws.recv()
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
					"query": "subscription configuration($input: SubscribeInput!) {\n  subscribe(input: $input) {\n    id\n    ... on BasicMessage {\n      data {\n        __typename\n        ... on ConfigurationMessageData {\n          colorPalette {\n            colors {\n              hex\n              index\n              __typename\n            }\n            __typename\n          }\n          canvasConfigurations {\n            index\n            dx\n            dy\n            __typename\n          }\n          canvasWidth\n          canvasHeight\n          __typename\n        }\n      }\n      __typename\n    }\n    __typename\n  }\n}\n",
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
						"query": "subscription replace($input: SubscribeInput!) {\n  subscribe(input: $input) {\n    id\n    ... on BasicMessage {\n      data {\n        __typename\n        ... on FullFrameMessageData {\n          __typename\n          name\n          timestamp\n        }\n        ... on DiffFrameMessageData {\n          __typename\n          name\n          currentTimestamp\n          previousTimestamp\n        }\n      }\n      __typename\n    }\n    __typename\n  }\n}\n",
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
					async with aiohttp.ClientSession() as sess:
						async with sess.get(msg["data"]["name"]) as res:
							imgs.append(
								(
									img_id,
									Image.open(
										BytesIO(await res.read())
									),
								)
							)
					canvas_sockets.remove(img_id)
					logger.debug(
						"Canvas sockets remaining: {}", len(canvas_sockets)
					)

	for i in range(0, canvas_count - 1):
		ws.send(json.dumps({"id": str(2 + i), "type": "stop"}))

	ws.close()

	new_img_width = (
		max(map(lambda x: x["dx"], canvas_details["canvasConfigurations"]))
		+ canvas_details["canvasWidth"]
	)
	logger.debug("New image width: {}", new_img_width)
	new_img_height = (
		max(map(lambda x: x["dy"], canvas_details["canvasConfigurations"]))
		+ canvas_details["canvasHeight"]
	)
	logger.debug("New image height: {}", new_img_height)

	new_img = Image.new("RGB", (new_img_width, new_img_height))
	for idx, img in enumerate(sorted(imgs, key=lambda x: x[0])):
		logger.debug("Adding image (ID {}): {}", img[0], img[1])
		dx_offset = int(canvas_details["canvasConfigurations"][idx]["dx"])
		dy_offset = int(canvas_details["canvasConfigurations"][idx]["dy"])
		new_img.paste(img[1], (dx_offset, dy_offset))

	return new_img