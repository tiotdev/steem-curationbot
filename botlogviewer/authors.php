<?php
session_start();
include 'config.php'; //Include config (pw and paths)
if (!isset($_SESSION["is_auth"])) {
	header("location: login.php");
	exit;
}
else if (isset($_REQUEST['logout']) && $_REQUEST['logout'] == "true") {
	unset($_SESSION['is_auth']);
	session_destroy();
	header("location: login.php");
	exit;
}
?>
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>Author Log - TravelFeed</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.0/css/bootstrap.min.css" integrity="sha384-9gVQ4dYFwwWSjIDZnLEWnxCjeSWFphJiwGPXr1jddIhOegiu1FwO5qRGvFXOdJZ4" crossorigin="anonymous">
    <link rel="stylesheet" href="page.css">
  </head>
  <body>
  <nav class="navbar navbar-expand-md navbar-dark bg-dark fixed-top">
      <a class="navbar-brand" href="#">Travelfeed</a>
      <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarsExampleDefault" aria-controls="navbarsExampleDefault" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarsExampleDefault">
        <ul class="navbar-nav mr-auto">
          <li class="nav-item">
            <a class="nav-link" href="index.php">Post Log</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="pylog.php">Bot Log</a>
          </li>
          <li class="nav-item active">
            <a class="nav-link" href="#">Author Log <span class="sr-only">(current)</span></a>
          </li>
        </ul>
          <a class="text-light" href="/?logout=true">Logout</a> 
     </div>
    </nav>

    <main role="main" class="container">
      <div class="starter-template">
        <h1>Recent Author Log</h1>
        <p>Authors who have received advertisement by the @de-travelfeed bot</p>
        <div class="card bg-faded bg-dark text-success"><div class="card-body">     
        <p class="card-text">
        <?php
        $file = file($authorlist);
        $file = array_reverse($file);
        foreach($file as $f){ echo "<a class='text-success' href='https://steemit.com/@".$f."' target='_blank'>@".$f."</a><br />";
        }
        ?>
        </p>
        </div>
        </div>
        </div>
    </main>
<script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.1.0/js/bootstrap.min.js" integrity="sha384-uefMccjFJAIv6A+rW+L4AHf99KvxDjWSu1z9VI8SKNVmz4sk7buKt/6v9KI65qnm" crossorigin="anonymous"></script>
  </body>
</html>