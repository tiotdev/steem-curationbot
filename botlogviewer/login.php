<?php
	session_start();
	include 'config.php'; //Include config (pw and paths)
    if (isset($_POST['login-submit'])) 
    {
	    if (isset($_POST['passwd'])) {
			$passwd = $_POST['passwd'];
			if ($passwd == $passwdfrontend) {
					$_SESSION['is_auth'] = true;
					header('location: index.php');
					exit;
				}
				else {
					$error = "Invalid Password. Please try again.";
				}
			}
			else {
				$error = "Invalid Password. Please try again.";
			}
		}
?>
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>Travelfeed</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.0/css/bootstrap.min.css" integrity="sha384-9gVQ4dYFwwWSjIDZnLEWnxCjeSWFphJiwGPXr1jddIhOegiu1FwO5qRGvFXOdJZ4" crossorigin="anonymous">
    <link rel="stylesheet" href="login.css">
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.1.0/js/bootstrap.min.js" integrity="sha384-uefMccjFJAIv6A+rW+L4AHf99KvxDjWSu1z9VI8SKNVmz4sk7buKt/6v9KI65qnm" crossorigin="anonymous"></script>
  </head>
  <body class="text-center">
    <div class="container">
    <form class="form-signin" method="post" action="">
    <h1 class="h3 mb-3 font-weight-normal">Please sign in</h1>
    <?php
			if (isset($error)) {
				echo "<div class='alert alert-danger'>$error</div>";
			}
		?>
    <label for="inputpassword" class="sr-only">Password</label>
    <input type="Password" name="passwd" id="passwd" class="form-control" placeholder="Password" required>
    <button class="btn btn-lg btn-primary btn-block" name="login-submit" id="login-submit" type="submit">Sign in</button>
    </form>
    </div>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.1.0/js/bootstrap.min.js" integrity="sha384-uefMccjFJAIv6A+rW+L4AHf99KvxDjWSu1z9VI8SKNVmz4sk7buKt/6v9KI65qnm" crossorigin="anonymous"></script>
  </body>
</html>