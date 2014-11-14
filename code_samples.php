<?php
// Get all data about a product (knowing its id)

$c = new AutoJsonClient("https://assos.utc.fr/buckutt/", "CATALOG");
$result = $c->loginApp(array("key" => '44682eb98b373105b99511d3ddd0034f'));
$result = $c->getProduct(array("fun_id" => 2, "obj_id" => getPrices()[0]["id"]));
var_dump($result);


// Get image
// 3396 => Cafe_id
$result = $c->getImage64(array("img_id" => 3396));
var_dump($result);

// Serialize and unserialize
unserialize(serialize(getProducts()));

?>
