from analyzer.evaluator import evaluate_fix



before = {

    "vulnerabilities":[

        {
            "rule":
            "php-dangerous-unserialize"
        }

    ]

}



after = {

    "vulnerabilities":[]

}



result = evaluate_fix(
    before,
    after
)


print(result)