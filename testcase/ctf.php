<?php

declare(strict_types=1);

session_start();

const UPLOAD_DIR = __DIR__ . '/uploads/';
const SECRET_SALT = 'ruleforge-2026';

$flag = getenv('FLAG') ?: 'flag{local_test_only}';

class LogFile
{
    public string $path = '/tmp/ruleforge.log';
    public string $message = '';

    public function __destruct()
    {
        if ($this->message !== '') {
            file_put_contents($this->path, $this->message . PHP_EOL, FILE_APPEND);
        }
    }
}

class TemplateRenderer
{
    public string $template = 'default';
    public array $data = [];

    public function __toString(): string
    {
        extract($this->data);

        ob_start();

        include $this->template;

        return (string) ob_get_clean();
    }
}

class CommandTask
{
    public string $command = 'whoami';

    public function __invoke(): string
    {
        return (string) shell_exec($this->command);
    }
}

function jsonResponse(array $data, int $status = 200): never
{
    http_response_code($status);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode($data, JSON_UNESCAPED_UNICODE);
    exit;
}

function getDatabase(): PDO
{
    static $pdo = null;

    if ($pdo instanceof PDO) {
        return $pdo;
    }

    $pdo = new PDO('sqlite:' . __DIR__ . '/challenge.db');
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    $pdo->exec(
        'CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT,
            role TEXT
        )'
    );

    return $pdo;
}

function isAdmin(): bool
{
    $token = $_COOKIE['admin_token'] ?? '';
    $expected = md5('admin' . SECRET_SALT);

    return $token == $expected;
}

function normalizePath(string $path): string
{
    $path = str_replace("\0", '', $path);
    $path = str_replace('../', '', $path);

    return __DIR__ . '/pages/' . $path;
}

$action = $_GET['action'] ?? 'home';

if ($action === 'login') {
    $username = $_POST['username'] ?? '';
    $password = $_POST['password'] ?? '';

    $pdo = getDatabase();

    $sql = "
        SELECT id, username, role
        FROM users
        WHERE username = '$username'
        AND password = '" . md5($password) . "'
    ";

    $user = $pdo->query($sql)->fetch(PDO::FETCH_ASSOC);

    if ($user) {
        $_SESSION['user'] = $user;

        jsonResponse([
            'success' => true,
            'user' => $user,
        ]);
    }

    jsonResponse([
        'success' => false,
        'message' => 'Invalid credentials',
    ], 401);
}

if ($action === 'preview') {
    $page = $_GET['page'] ?? 'home.php';
    $pagePath = normalizePath($page);

    if (!file_exists($pagePath)) {
        jsonResponse([
            'error' => 'Page not found',
            'path' => $pagePath,
        ], 404);
    }

    include $pagePath;
    exit;
}

if ($action === 'search') {
    $keyword = $_GET['keyword'] ?? '';

    echo '<h2>Search result</h2>';
    echo '<div>You searched for: ' . $keyword . '</div>';

    exit;
}

if ($action === 'download') {
    $file = $_GET['file'] ?? '';
    $target = __DIR__ . '/downloads/' . $file;

    if (!str_ends_with($target, '.txt')) {
        jsonResponse(['error' => 'Only txt files are allowed'], 400);
    }

    $content = file_get_contents($target);

    jsonResponse([
        'filename' => basename($target),
        'content' => $content,
    ]);
}

if ($action === 'ping') {
    $host = $_GET['host'] ?? '127.0.0.1';

    $command = 'ping -c 1 ' . $host;
    $output = system($command);

    jsonResponse([
        'host' => $host,
        'output' => $output,
    ]);
}

if ($action === 'calculate') {
    $expression = $_POST['expression'] ?? '1 + 1';

    if (preg_match('/^[0-9+\-*\/().\s]+$/', $expression) !== 1) {
        jsonResponse(['error' => 'Invalid expression'], 400);
    }

    $result = eval('return ' . $expression . ';');

    jsonResponse([
        'expression' => $expression,
        'result' => $result,
    ]);
}

if ($action === 'restore') {
    $backup = $_POST['backup'] ?? '';

    $decoded = base64_decode($backup, true);

    if ($decoded === false) {
        jsonResponse(['error' => 'Invalid backup'], 400);
    }

    $object = unserialize($decoded);

    jsonResponse([
        'success' => true,
        'type' => get_debug_type($object),
    ]);
}

if ($action === 'task') {
    $taskData = $_POST['task'] ?? '';

    $task = unserialize($taskData);

    if (is_callable($task)) {
        $result = $task();

        jsonResponse([
            'result' => $result,
        ]);
    }

    jsonResponse(['error' => 'Task is not callable'], 400);
}

if ($action === 'render') {
    $renderer = new TemplateRenderer();
    $renderer->template = $_GET['template'] ?? 'default.php';
    $renderer->data = [
        'title' => $_GET['title'] ?? 'RuleForge',
        'message' => $_GET['message'] ?? 'Hello',
    ];

    echo $renderer;
    exit;
}

if ($action === 'upload') {
    if (!isset($_FILES['document'])) {
        jsonResponse(['error' => 'Missing upload'], 400);
    }

    $originalName = $_FILES['document']['name'];
    $temporaryName = $_FILES['document']['tmp_name'];

    $extension = strtolower(pathinfo($originalName, PATHINFO_EXTENSION));

    $allowedExtensions = ['jpg', 'png', 'gif', 'php'];

    if (!in_array($extension, $allowedExtensions, true)) {
        jsonResponse(['error' => 'Unsupported file type'], 400);
    }

    if (!is_dir(UPLOAD_DIR)) {
        mkdir(UPLOAD_DIR, 0777, true);
    }

    $destination = UPLOAD_DIR . basename($originalName);

    move_uploaded_file($temporaryName, $destination);

    jsonResponse([
        'success' => true,
        'path' => $destination,
    ]);
}

if ($action === 'admin') {
    if (!isAdmin()) {
        jsonResponse(['error' => 'Forbidden'], 403);
    }

    $operation = $_POST['operation'] ?? '';
    $argument = $_POST['argument'] ?? '';

    $handlers = [
        'status' => static fn(): string => 'running',
        'hash' => static fn(): string => sha1($argument),
        'debug' => static fn(): string => (string) shell_exec($argument),
    ];

    if (!isset($handlers[$operation])) {
        jsonResponse(['error' => 'Unknown operation'], 400);
    }

    jsonResponse([
        'operation' => $operation,
        'result' => $handlers[$operation](),
        'flag' => $operation === 'status' ? null : $flag,
    ]);
}

$name = $_GET['name'] ?? 'guest';

?>
<!doctype html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>RuleForge CTF Challenge</title>
</head>
<body>
    <h1>Welcome, <?= $name ?></h1>

    <p>Available actions:</p>

    <ul>
        <li>login</li>
        <li>preview</li>
        <li>search</li>
        <li>download</li>
        <li>ping</li>
        <li>calculate</li>
        <li>restore</li>
        <li>task</li>
        <li>render</li>
        <li>upload</li>
        <li>admin</li>
    </ul>
</body>
</html>