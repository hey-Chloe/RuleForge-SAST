<?php

$payload = $_GET["payload"] ?? "{}";
$data = json_decode($payload, true, 512, JSON_THROW_ON_ERROR);

echo json_encode($data, JSON_UNESCAPED_UNICODE);

