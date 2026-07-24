from analyzer.patch_verify import verify_patch


result = verify_patch(

    "./target_repo",

    "5c2ef4e",

    "f565423",

    "./target_repo/testcase",

    "../rules/php-unserialize.yaml"

)


print(result)