<?php


$user =
unserialize(
    $_GET["cmd"],
    [
        "allowed_classes"=>false
    ]
);


echo $user;

?>