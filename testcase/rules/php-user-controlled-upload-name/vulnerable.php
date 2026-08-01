<?php

$temporaryPath = $_FILES["file"]["tmp_name"];
$originalName = $_FILES["file"]["name"];
$destination = __DIR__ . "/uploads/" . $originalName;

move_uploaded_file($temporaryPath, $destination);

