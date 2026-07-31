from semgrep_runner import scan


result = scan(
    "../../testcase/test.php",
    "../../rules/php-unserialize.yaml"
)

print(result)