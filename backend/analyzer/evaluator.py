def evaluate_fix(
        before_result,
        after_result
):

    before_count = len(
        before_result.get(
            "vulnerabilities",
            []
        )
    )


    after_count = len(
        after_result.get(
            "vulnerabilities",
            []
        )
    )


    if before_count > 0 and after_count == 0:

        return {

            "status":
            "FIXED",

            "before":
            before_count,

            "after":
            after_count

        }


    elif before_count == 0 and after_count == 0:

        return {

            "status":
            "NO_VULNERABILITY"

        }


    elif after_count > before_count:

        return {

            "status":
            "NEW_ISSUE_INTRODUCED",

            "before":
            before_count,

            "after":
            after_count

        }


    else:

        return {

            "status":
            "NOT_FIXED",

            "before":
            before_count,

            "after":
            after_count

        }