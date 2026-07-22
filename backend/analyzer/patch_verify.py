from git import Repo

from engine.semgrep_runner import run_semgrep

from analyzer.evaluator import evaluate_fix

from analyzer.git_diff import get_commit_diff



def checkout_commit(repo_path, commit):

    repo = Repo(repo_path)

    repo.git.checkout(commit)



def verify_patch(
        repo_path,
        old_commit,
        new_commit,
        target,
        rule
):


    # 1. 获取diff

    diff = get_commit_diff(
        repo_path,
        old_commit,
        new_commit
    )


    # 2. checkout旧版本

    checkout_commit(
        repo_path,
        old_commit
    )


    before = run_semgrep(
        target,
        rule
    )


    # 3. checkout新版本

    checkout_commit(
        repo_path,
        new_commit
    )


    after = run_semgrep(
        target,
        rule
    )


    # 4.评估

    evaluation = evaluate_fix(
        before,
        after
    )


    return {

        "diff":
        diff,


        "before":
        before,


        "after":
        after,


        "evaluation":
        evaluation

    }