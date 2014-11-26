<?php
require_once "vendor/autoload.php";

use \Payutc\Client\AutoJsonClient;
use \Payutc\Client\JsonException;

$cookie = '';
$r = null;

$c = new AutoJsonClient("https://assos.utc.fr/buckutt/", "GESARTICLE");
$result = $c->loginApp(array("key" => 'PICASSO_KEY'));
$result = $c->setProduct(array(
    "name" => "Cuisse de Jo",
    "parent" => "3",
    "prix" => "0",
    "stock" => "2",
    "alcool" => "0",
    "fun_id" => "2",
    "image" => null,
));

?>
