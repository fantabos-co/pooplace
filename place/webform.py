LANDING = """
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
				<img class="card-img-top" src="https://cdn.pooblic.org/logo.gif" alt="pooblic logo">
				<div class="card-body">
					<h5 class="card-title">Donate your r/place actions</h5>
					<p class="card-text">Share with us your pixels to work on something bigger!</p>
					<form method="post">
						<div class="form-group">
							<input class="mb-2 form-control" type="text" name="username" placeholder="name (must be unique)"/>
							<input class="mb-2 form-control" type="text" name="token" placeholder="token"/>
						</div>
						<div class="float-end">
						<button type="submit" class="btn btn-primary">Submit</button>
						</div>
					</form>
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
				<img class="card-img-top" src="https://cdn.pooblic.org/logo.gif" alt="pooblic logo">
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
				<img class="card-img-top" src="https://cdn.pooblic.org/logo.gif" alt="pooblic logo">
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

