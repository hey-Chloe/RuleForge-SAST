<?php

$xmlInput = $_POST["xml"] ?? "";
libxml_disable_entity_loader(false);
$document = simplexml_load_string($xmlInput);

echo $document->asXML();

