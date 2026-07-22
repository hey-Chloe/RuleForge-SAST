from semgrep_runner import scan


result = scan(
    "../../tests/test.php",
    "../../rules/php-unserialize.yaml"
)


print(result)
