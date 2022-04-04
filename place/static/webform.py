LANDING = """
<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<meta property="og:type" content="website">
	<meta property="og:title" content="r/place botnet | pooblic.org" />
	<meta property="og:description" content="place automation tools for block game community" />
	<meta property="og:url" content="https://pooblic.org/place" />
	<meta property="og:image" content="https://cdn.pooblic.org/logo.gif" />
	<meta property="og:image:alt" content="Pooblic" />
	<meta property="og:image:type" content="image/gif" />
	<meta property="og:image:width" content="512" />
	<meta property="og:image:height" content="512" />
	<title>r/place botnet | pooblic.org</title>
	<link rel="icon" type="image/x-icon" href="https://cdn.pooblic.org/logo.gif">
	<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">
</head>
<body>
	<nav class="navbar navbar-light bg-light">
		<a class="navbar-brand ps-3" href="https://pooblic.org/place">Pooblic r/place botnet</a>
	</nav>
	<div class="container-fluid d-flex justify-content-center align-items-center h-100">
		<div class="col col-6 pt-2">
			<div class="card">
				<img class="card-img-top" src="https://cdn.pooblic.org/placelogo.png" alt="9b9t r/place logo">
				<div class="card-body">
					<h5 class="card-title">Donate a reddit throwaway</h5>
					<p class="card-text">Share with us your throwaways to work on something bigger!</p>
					<p class="card-text">Network currently holds <b>{users}</b> users (<b>{ready}</b> ready to place)</p>
					<div class="row">
						<div class="col-4">
							<a href="https://pooblic.org/place/stats" class="btn btn-secondary" role="button" aria-disabled="true">check out the stats</a>
						</div>
						<div class="col-4"></div>
						<div class="col-4">
							<a href="https://pooblic.org/place/auth" class="btn btn-primary" ro float-endle="button" aria-disabled="true">feed in an account</a>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</body>
</html>
"""

FORM_OK = """
<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<title>r/place botnet | pooblic.org</title>
	<link rel="icon" type="image/x-icon" href="https://cdn.pooblic.org/logo.gif">
	<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">
</head>
<body>
	<nav class="navbar navbar-light bg-light">
		<a class="navbar-brand ps-3" href="https://pooblic.org/place">Pooblic r/place botnet</a>
	</nav>
	<div class="container-fluid d-flex justify-content-center align-items-center h-100">
		<div class="col col-6 pt-2">
			<div class="card">
				<img class="card-img-top" src="https://cdn.pooblic.org/placelogo.png" alt="9b9t r/place logo">
				<div class="card-body">
					<h5 class="card-title">Success</h5>
					<p>Your user id is <b>{userid}</b>. Use this to keep track of <a href="https://pooblic.org/place/stats">your cooldown</a>!</p>
				</div>
			</div>
		</div>
	</div>
</body>
</html>
"""

FORM_NOK = """
<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<title>r/place token donations</title>
	<link rel="icon" type="image/x-icon" href="https://cdn.pooblic.org/logo.gif">
	<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">
</head>
<body>
	<nav class="navbar navbar-light bg-light">
		<a class="navbar-brand ps-3" href="https://pooblic.org/place">Pooblic r/place botnet</a>
	</nav>
	<div class="container-fluid d-flex justify-content-center align-items-center h-100">
		<div class="col col-6 pt-2">
			<div class="card">
				<img class="card-img-top" src="https://cdn.pooblic.org/placelogo.png" alt="9b9t r/place logo">
				<div class="card-body">
					<h5 class="card-title">Error</h5>
					<p>Reddit might be rate limiting us, please give us some breath (like 5/10 mins)</p>
				</div>
			</div>
		</div>
	</div>
</body>
</html>
"""

ACCOUNT_LINE = """<li><b>{name}</b> : {cooldown:.1f}</li>"""
USER_STATS = """
<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<title>r/place botnet | pooblic.org</title>
	<link rel="icon" type="image/x-icon" href="https://cdn.pooblic.org/logo.gif">
	<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">
</head>
<body>
	<nav class="navbar navbar-light bg-light">
		<a class="navbar-brand ps-3" href="https://pooblic.org/place">Pooblic r/place botnet</a>
	</nav>
	<div class="container-fluid d-flex justify-content-center align-items-center h-100">
		<div class="col col-6 pt-2">
			<div class="card">
				<img class="card-img-top" src="https://cdn.pooblic.org/placelogo.png" alt="9b9t r/place logo">
				<div class="card-body">
					<h5 class="card-title">Accounts:</h5>
					<ul>{accounts}</ul>
				</div>
			</div>
		</div>
	</div>
</body>
</html>
"""

