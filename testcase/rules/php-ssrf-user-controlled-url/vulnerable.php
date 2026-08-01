<?php

$getUrl = $_GET["url"] ?? "";
$postUrl = $_POST["url"] ?? "";
$requestUrl = $_REQUEST["url"] ?? "";

$firstResponse = file_get_contents($getUrl);
$curlHandle = curl_init($postUrl);
$secondResponse = file_get_contents($requestUrl);

echo $firstResponse . $secondResponse;
curl_close($curlHandle);

