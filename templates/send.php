<?php
error_reporting(0);
$nombre = $_POST['nombre'];
$correo_electronico= $_POST['email'];
$opinion=$_POST['mensaje'];
$header .= "X-Mailer: PHP/" . phpversion() . " \r\n";
$header .= "Mime-Version: 1.0 \r\n";
$header .= "Content-Type: text/plain";

$mensaje = "Este mensaje fue enviado por " . $nombre . " \r\n";
$mensaje .="danos tu opinion".$_POST['opinion'] . " \r\n";
$mensaje .= "Enviado el " . date('d/m/Y', time());

$para = "hola@nodux.ec";
$asunto = 'MENSAJE DESDE NODUX COMPROBANTES ELECTRONICOS';

@mail($para, $asunto, utf8_decode($mensaje), $header);

echo 'mensaje enviado correctamente';

?> 
