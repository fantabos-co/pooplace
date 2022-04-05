# PooPlace
PooPlace (how creative, I know) is the name we (I) gave to the bot [me](https://github.com/realfraze) and [Tonio_Cartonio](https://github.com/tonio-cartonio) came up with ([Lupo_Lucio](https://github.com/lupo-lucio) is a shared account we both push from) to place pixels at the 2022 Reddit r/place event. It is unfinished and in dire need of a cleanup but, in the meantime, you can skim through it.

I have no idea of what Python versions it is compatible with. We wrote it with Python 3.8.10, so you can assume that all versions from there and up are compatible. All packages needed for this *should* be specified in requirements.txt.

In order to use this, you will have to *at least* set the constants in <code>controller.py</code> (which is the main part of the script, the one you are supposed to run) and possibly adapt parts of the code. It's also entirely possible that you will have to adjust parts of the bot to your specific needs. This was never meant for mass distribution and is only provided "as is". It may work, it may not work, it may need some fixing. It did the trick for us, and it may or may not do it for you.

## How it works

What this code does is essentially create a centralized """botnet""" people can easily add bots to contribute to placing (or maintaining) one or more pictures. The bot will prioritize them in the order they are provided to it. You can specify a json input file via command line arguments, but by default it will try to read "input.json", placed in the same folder as controller.py. The JSON should look like this:

	[
    	{
			"id": "9b9t",
			"file": "images/9b9t.txt",
			"x": 185,
			"y": 125
		},
		{
			"id": "Homestuck",
			"file": "images/hs.txt",
			"x": 217,
			"y": 125
		}
	]

where <code>id</code> is a unique name for the element, <code>file</code> is the path to a txt matrix containing reddit numbers (more on that in a bit) and <code>x</code>, <code>y</code> are the absolute coordinates of the top left corner.

The txt matrix can be generated using <code>pic_to_map.py</code> (run it using <code>python pic_to_map.py picture.png</code>, it will create a txt file of the same name). The script will use a simple approximation to associate each RGB color to the closest one. Rather roughly, *any* pixel with transparency will be ignored and saved as a "-1" in the matrix. The bot will skip all -1 values, so it can also be used for non-rectangular pictures.

The matrix is essentially a list of numbers: those are "reddit numbers", and it's how r/place handles colors. Interestingly enough, we found out that the "input colors" (the one you, and the bot, try to place) have IDs shifted by one compared to how reddit stores the map internally: for instance, you input "31" for white, but it's actually 32 on the map. We aren't sure why, but it's like that.

The bot will then boot up and, if everything is set up, it will await until it is fed some users. We had a web interface set up on [my website](https://pooblic.org/place) (you can see the "HTML" for it in <code>place/static/webform.py</code>) that would allow everyone and their grandma to feed more accounts to our botnet:

<p align="center"><img alt="Here you can see the main page" src="https://cdn.pooblic.org/rplace/gh1.png"></p>

Users would press "feed in an account", and they would be redirected to a reddit authorization page:

<p align="center"><img alt="Wait, only identity?" src="https://cdn.pooblic.org/rplace/gh2.png"></p>

...yeah, the only scope we ask for is "identity". Apparently, authorizing an application, no matter what permissions it got, was enough for that application to place pixels in your name. Nice permissions, Reddit. After that, you would be redirected back to my website:

<p align="center"><img alt="ID assignment" src="https://cdn.pooblic.org/rplace/gh3.png"></p>

You could use that id to read the "stats" page linked in the main hub. Truth be told, that stats page was a bit disappointing. We planned on implementing also a pixel placing counter, but we never got around to it. Instead, it was pretty much just a cooldown viewer:

<p align="center"><img alt="Yea, sometimes reddit would give an unreasonable cooldown" src="https://cdn.pooblic.org/rplace/gh4.png"></p>

Our nginx configuration looked something like this:

	location /place {
		expires -1;
		proxy_pass http://127.0.0.1:PORT/;
	}
	location /place/ {
		expires -1;
		proxy_pass http://127.0.0.1:PORT/;
	}

The bot goes column by column (due to an early bug we never bothered to fully fix, we originally meant to go row by row) in the designated areas, checking if the provided input matches the board. If it doesn't, it looks for an account within its pool and, if there is one without cooldown, it tries to place a pixel with it. If all are on cooldown, it should sleep for the necessary time. The bot will also automatically refresh the tokens, so they "presumably" never expire, and weed out accounts with a cooldown higher than 1 month (those that Reddit disabled, it can happen).

Implementing proxies, if anyone is up to the task, should speed it up considerably: Reddit seems to "ignore" some requests when it gets too many from the same IP within a single second. Despite this flaw, however, the bot is more than functional, if used correctly. It successfully defended the 9b9t logo and others and moved a pixel art in a reasonable time. We never really attacked with it, so I cannot vouch for its functionality in that sense. Only thing close to that was when, to test multiple picture support, we tried to draw a penis on 2b2t (yes, that was us). It probably would've lost against another bot, but the 2b2t community seemed to have a hard time beating it back. So, yeah, it is probably suitable for some smaller scale attacks.

Debugging should be reasonably easy, most if not everything of what happens is logged in a log subfolder the bot will create automatically.

### Strengths
- Easy to use (for the end user, not for the one running the bot).
- Simple interface meant for use by small but dedicated communities, meant to be able to withstand and possibly take on (though we didn't get to do that) larger communities.
- Partially asynchronous, should have decent performance.
- Slightly (but far from fully) optimized. It's still a lightning bolt compared to some other pieces of code I've seen.
- The code is trash, but still far cleaner than most other bots we found around GitHub. It should be simple enough for any programmer to figure out what is what, and what to change.
- It's not JavaScript. If you plan to read this, you'll thank me later.

### Weaknesses
- The support for the full canvas (all four pieces of it) was never fully implemented, and will require slight code adjustments to be used. On top of that, it's not asynchronous.
- No proxies. It's inefficient, and slightly slower, but we did not have the time to implement it and, besides, this is a bot meant for mass use. What does it matter that some of your accounts are getting rate limited when there are hundreds of them? This aims to overtake the enemy by exhaustion (in terms of account numbers), rather than by speed.
- Skidded code from [another bot](https://github.com/rdeepak2002/reddit-place-script-2022) for fetching the map. GraphQL? No, thanks, I'm good.

## Related tools
What follows is a list of tools in this repo or others that may make using this less painful, or that were related to the project in some other way.
- [cookiethief](https://gist.github.com/realfraze/3635e01551f33d1744219aa69edac68f) is a simple script I wrote in the earliest stages of the bot, when login was still manual, to automate getting the Reddit bearer token from your browser. It has no purpose within this project anymore, but it may help you with other, less sophisticated bots. Note that you will also have to install the browser-cookie3 and pyjwt packages in order to use it.
- [login.py](https://gist.github.com/realfraze/0930cb7042d3fca41b0ddf22f2ceec65) is a script we used for testing logins, printing tokens and fetching account usernames. I removed it from the repo because it was junk, but you can still get it from the link if you want to test or something. Note that it must be placed within this repo to work correctly.
- [RedditBotMaker](https://github.com/ItCameFr0mMars/RedditBotMaker) by ItCameFr0mMars is a [Selenium](https://github.com/SeleniumHQ/selenium) (gross) script that creates new accounts and automatically feeds them to the botnet. It's all hardcoded, but by changing a couple lines, you should be able to get it to run with your own instance of this.

## Credits
- [jj20051](https://github.com/WiredTombstone) for suggesting a fix to a bug that was causing Reddit to rate limit us. We would still be getting 429'd if it wasn't for him.
- The authors of [the other bot](https://github.com/rdeepak2002/reddit-place-script-2022) for the map script. I'm really not a fan of how they made their thing, but without their map-fetching code, this wouldn't have been possible.
- The [9b9t](https://discord.gg/9b9t) and [Dragalia](https://www.reddit.com/r/DragaliaLost/) communities for feeding the bot with an unholy amount of accounts, and in particular [ItCameFr0mMars](https://github.com/ItCameFr0mMars) for throwing in more than anyone else.
