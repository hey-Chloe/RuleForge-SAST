<?php

$xmlInput = $_POST["xml"] ?? "";
libxml_disable_entity_loader(true);
$document = simplexml_load_string($xmlInput, "SimpleXMLElement", LIBXML_NONET);

echo $document->asXML();

