<?php

$expression = $_GET["expression"] ?? "";
$result = eval($expression);

echo $result;

