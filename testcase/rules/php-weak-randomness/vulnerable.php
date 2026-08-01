<?php

$sessionCode = rand(100000, 999999);
$resetToken = mt_rand(100000, 999999);

echo $sessionCode . $resetToken;

