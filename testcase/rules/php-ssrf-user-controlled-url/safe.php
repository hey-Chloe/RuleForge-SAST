<?php

$healthUrl = "https://status.example.com/health";
$apiUrl = "https://api.example.com/v1/status";

$healthResponse = file_get_contents($healthUrl);
$curlHandle = curl_init($apiUrl);

echo $healthResponse;
curl_close($curlHandle);

