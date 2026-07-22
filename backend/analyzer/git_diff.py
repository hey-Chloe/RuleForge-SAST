from git import Repo


def get_commit_diff(
        repo_path,
        old_commit,
        new_commit
):

    repo = Repo(repo_path)


    diff = repo.git.diff(
        old_commit,
        new_commit
    )


    return diff



if __name__ == "__main__":


    result = get_commit_diff(
        "../../",
        "HEAD~1",
        "HEAD"
    )


    print(result)