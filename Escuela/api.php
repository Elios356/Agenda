<?php
header("Content-Type: application/json");
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: GET, POST, DELETE");
header("Access-Control-Allow-Headers: Content-Type");

$host = "localhost";
$user = "root";
$pass = "TU_PASSWORD";
$db   = "sistema_usuarios";

$conn = new mysqli($host, $user, $pass, $db);

if ($conn->connect_error) {
    http_response_code(500);
    echo json_encode(["error" => "Error de conexión"]);
    exit;
}

$method = $_SERVER['REQUEST_METHOD'];

switch ($method) {

    case "GET":

        $sql = "SELECT nombre, edad, categoria FROM usuarios ORDER BY id DESC";
        $result = $conn->query($sql);

        if (!$result) {
            echo json_encode([]);
            exit;
        }

        $usuarios = $result->fetch_all(MYSQLI_ASSOC);
        echo json_encode($usuarios);

    break;

    case "POST":

        $input = json_decode(file_get_contents("php://input"), true);

        if (!isset($input["nombre"], $input["edad"], $input["categoria"])) {
            http_response_code(400);
            echo json_encode(["error"=>"Datos incompletos"]);
            exit;
        }

        $nombre = trim($input["nombre"]);
        $edad = intval($input["edad"]);
        $categoria = trim($input["categoria"]);

        if ($nombre === "" || $edad <= 0) {
            http_response_code(400);
            echo json_encode(["error"=>"Datos inválidos"]);
            exit;
        }

        $stmt = $conn->prepare(
            "INSERT INTO usuarios (nombre, edad, categoria) VALUES (?, ?, ?)"
        );

        $stmt->bind_param("sis", $nombre, $edad, $categoria);

        if ($stmt->execute()) {
            echo json_encode(["status"=>"success"]);
        } else {
            http_response_code(500);
            echo json_encode(["error"=>"No se pudo guardar"]);
        }

        $stmt->close();

    break;

    case "DELETE":

        if ($conn->query("TRUNCATE TABLE usuarios")) {
            echo json_encode(["status"=>"deleted"]);
        } else {
            http_response_code(500);
            echo json_encode(["error"=>"No se pudo borrar"]);
        }

    break;

    default:
        http_response_code(405);
        echo json_encode(["error"=>"Método no permitido"]);
}

$conn->close();
?>