#https://www.reddit.com/r/changelog/comments/ynxg8/reddit_change_oauth_2_bearer_token_support_for_all/
#https://www.reddit.com/r/redditdev/comments/bf1yrg/reddits_bearer_token/
#https://github.com/x89/Shreddit
#https://praw.readthedocs.io/en/stable/getting_started/authentication.html

from typing import List
from place import User, fucking_payload, fucking_user
from time import sleep

class Pool:
	users : List[User]

	def __init__(self):
		self.users = list()

	def add_user(self, u:User):
		self.users.append(u)

	def remove_user(self, n:str):
		users = [u for u in users if u.name != n]
		
	def put(self, color:int, x:int, y:int):
		for u in self.users:
			if u.cooldown <= 0:
				u.put(color, x, y)
				return True
		return False

def loop(p: Pool):
	while True:
		if p.put(1, 1, 1):
			print("colored pixel [1, 1]")
		sleep(10)

if __name__ == "main":
	p = Pool()

	u = fucking_user()
	p.add_user(u)

	# TODO make more

	loop(p)