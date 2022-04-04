
import browser_cookie3
import jwt
import json

def get_token() -> str():
	print("How it works:")
	print("Log in to reddit from your preferred browser. This will look through your cookies and get the token needed to access it.")
	print("You can verify that the source is harmless yourself, but use a throwaway account if it makes you feel safer.")
	print("Please note that accounts with unverified emails get longer waiting times (I think).")
	while True:
		print("1: Chrome")
		print("2: Firefox")
		print("3: Opera")
		print("4: Edge (you are so fucking gay lmao)")
		print("5: Chromium")
		print("6: Brave")
		print("Other browsers are not currently supported.")
		print("Input 0 to go back.")

		print("What browser do you want to extract cookies from?")
		
		i = input("Input a number: ")
		if i == 0:
			return None
		elif i == 1:
			jar = browser_cookie3.chrome()
		elif i == 2:
			jar = browser_cookie3.firefox()
		elif i == 3:
			jar = browser_cookie3.opera()
		elif i == 4:
			jar = browser_cookie3.edge()
		elif i == 5:
			jar = browser_cookie3.chromium()
		elif i == 6:
			jar = browser_cookie3.brave()
		else:
			print("Invalid number, try again.")
			continue
		
		#get jwt encoded token
		token:str = None
		for cookie in jar:
			if cookie.domain == ".reddit.com" and cookie.name == "token_v2":
				return cookie.value

		#check that valid cookie was found
		if token is None:
			input("Error: we could not find a valid token_v2 among the selected browser's cookies. Ensure you are logged in, then press ENTER to try again.")
			continue

		#decode jwt
		token = json.loads(jwt.decode(token, options={"verify_signature": False}))["sub"] #we don't care about the signature, so we don't need a key
		
		print(token)
		
		return token