<?php

$sessionCode = random_int(100000, 999999);
$resetToken = bin2hex(random_bytes(32));

echo $sessionCode . $resetToken;

