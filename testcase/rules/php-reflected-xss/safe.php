<?php

$name = htmlspecialchars($_GET["name"] ?? "", ENT_QUOTES, "UTF-8");
$comment = htmlentities($_POST["comment"] ?? "", ENT_QUOTES, "UTF-8");

echo $name;
print $comment;
echo "固定的安全内容";

