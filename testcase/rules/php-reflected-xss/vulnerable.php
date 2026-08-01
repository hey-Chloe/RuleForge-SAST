<?php

$name = $_GET["name"] ?? "";
$comment = $_POST["comment"] ?? "";
$message = $_REQUEST["message"] ?? "";

echo $name;
print $comment;
echo $message;

