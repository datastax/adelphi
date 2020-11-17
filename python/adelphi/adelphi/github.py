# Functionality necessary to create a feature branch + pull request on Github

import os
import time

from github import Github

def build_github(repouser, repotoken):
    return Github(repouser, repotoken)

def build_repository(gh, repouser, reponame):
    repo = "/".join([repouser, reponame])
    return gh.get_repo(repo)

def build_branch(gh, repo, author):
    main_branch = repo.get_branch("main")
    # TODO: prolly should replace this with a legit UUID at some point
    branch_name = "_".join([author, str(time.time())])
    repo.create_git_ref(ref="refs/heads/" + branch_name, sha=main_branch.commit.sha)
    return branch_name

def commit_schemas(gh, repo, schemadir, branch_name, author):
    author_name = gh.get_user(author).login
    for schema in os.listdir(schemadir):
        repo_path = "/".join([author_name, schema])
        schema_file_path = "/".join([schemadir,schema])
        schema_str = open(schema_file_path).read()
        repo.create_file(path=repo_path, message="Schema " + schema, content=schema_str, branch=branch_name)
