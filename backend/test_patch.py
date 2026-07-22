from analyzer.patch_verify import verify_patch


result = verify_patch(

    "../",

    "cf5eef6",

    "243a1d8",

    "../testcase",

    "../rules/php-unserialize.yaml"

)


print(result)