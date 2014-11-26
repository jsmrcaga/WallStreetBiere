<?php

require_once "vendor/autoload.php";

use \Payutc\Client\AutoJsonClient;
use \Payutc\Client\JsonException;

function getProducts() {
    $datas = array();
    
    $c = new AutoJsonClient("https://assos.utc.fr/buckutt/", "CATALOG");
    
    $result = $c->loginApp(array("key" => 'PICASSO_KEY'));
    
    // Fun_id = 2 => PICASSO
    $result = $c->getProductsByCategories(array("fun_ids" => array(2)));
    
    foreach ($result as $category) {
        switch($category->name) {
        case("Bières bouteilles"):
            foreach($category->products as $product) {
                array_push($datas, array('id' => $product->id, 'name' => $product->name, 'stock' => $product->stock, 'price' => $product->price));
            }
            break;
    
        case("Bières pression"):
            foreach($category->products as $product) {
                array_push($datas, array('id' => $product->id, 'name' => $product->name, 'stock' => $product->stock, 'price' => $product->price));
            }
            break;
        }
    };

    return $datas;
}

function saveOriginalValues() {
    $save = "save.origin";
    if(file_exists($save)) {
        echo "original fail already exist : manually check it to know if you can overwrite it";
        echo "continue..?(y/n) ";
        
        $line = trim(fgets(STDIN));

        if(strcmp($line, "o") == 0) {
            saveOriginalValues();
        }
    } else {
        $fd = fopen($save, 'w');
        fwrite($fd, serialize(getProducts()));
        fclose($fd);
    }
}

saveOriginalValues();

//foreach (getProducts() as $r) {
//    echo var_dump($r);
//}


?>
