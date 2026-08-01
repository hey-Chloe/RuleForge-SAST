<?php

$password = $_POST["password"] ?? "";
$legacyPasswordHash = md5($password);
$legacyToken = sha1($password);

echo $legacyPasswordHash . $legacyToken;

