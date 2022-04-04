LANDING = """
<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<meta property="og:type" content="website">
	<meta property="og:title" content="place | pooblic.org" />
	<meta property="og:description" content="place automation tools for block game community" />
	<meta property="og:url" content="https://pooblic.org/place" />
	<meta property="og:image" content="https://cdn.pooblic.org/logo.gif" />
	<meta property="og:image:alt" content="Pooblic" />
	<meta property="og:image:type" content="image/gif" />
	<meta property="og:image:width" content="512" />
	<meta property="og:image:height" content="512" />
	<title>r/place token donations</title>
	<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">
</head>
<body>
	<div class="container d-flex justify-content-center align-items-center h-100">
		<div class="col col-6">
			<div class="card" style="width: 18rem;">
				<img class="card-img-top" src="https://cdn.pooblic.org/placelogo.webp" alt="9b9t r/place logo">
				<div class="card-body">
					<h5 class="card-title">Donate your r/place actions</h5>
					<p class="card-text">Share with us your pixels to work on something bigger!</p>
					<p class="card-text">Network currently holds <b>{users}</b> users</p>
					<div class="float-end">
						<a href="https://pooblic.org/place/auth" class="btn btn-primary" role="button" aria-disabled="true">feed in an account</a>
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
	<title>r/place token donations</title>
	<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">
</head>
<body>
	<div class="container d-flex justify-content-center align-items-center h-100">
		<div class="col col-6">
			<div class="card" style="width: 18rem;">
				<img class="card-img-top" src="https://cdn.pooblic.org/placelogo.webp" alt="9b9t r/place logo">
				<div class="card-body">
					<h5 class="card-title">Success</h5>
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
	<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">
</head>
<body>
	<div class="container d-flex justify-content-center align-items-center h-100">
		<div class="col col-6">
			<div class="card" style="width: 18rem;">
				<img class="card-img-top" src="https://cdn.pooblic.org/placelogo.webp" alt="9b9t r/place logo">
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

