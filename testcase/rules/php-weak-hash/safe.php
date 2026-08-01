<?php

$password = $_POST["password"] ?? "";
$passwordHash = password_hash($password, PASSWORD_ARGON2ID);
$checksum = hash("sha256", $password);

echo $passwordHash . $checksum;

