<?php

$temporaryPath = $_FILES["file"]["tmp_name"];
$serverFilename = bin2hex(random_bytes(16)) . ".bin";
$destination = __DIR__ . "/uploads/" . $serverFilename;

move_uploaded_file($temporaryPath, $destination);

