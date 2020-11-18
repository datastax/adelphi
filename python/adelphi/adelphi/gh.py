# Functionality necessary to create a feature branch + pull request on Github

import os
import os.path
import uuid

from github import Github, InputGitAuthor

# We're assuming any storage repo will be created after the converstion to "main"
MAIN_BRANCH_NAME = "main"

def build_github(repouser, repotoken):
    return Github(repouser, repotoken)

def build_repository(gh, repouser, reponame):
    repo = "/".join([repouser, reponame])
    return gh.get_repo(repo)

def build_branch(gh, repo, author_name):
    main_branch = repo.get_branch(MAIN_BRANCH_NAME)
    branch_name = "_".join([author_name, str(uuid.uuid4())])
    repo.create_git_ref(ref="refs/heads/" + branch_name, sha=main_branch.commit.sha)
    return branch_name

def commit_schemas(gh, repo, schemadir, branch_name, author_name):
    author_obj = gh.get_user(author_name)
    for schema in os.listdir(schemadir):
        repo_path = "/".join([author_obj.login, schema])
        schema_file_path = os.path.join(schemadir,schema)
        schema_str = open(schema_file_path).read()
        repo.create_file(path=repo_path, message="Schema " + schema, content=schema_str, branch=branch_name, author=InputGitAuthor(author_obj.name, author_obj.email))

def build_pull_request(repo, branch_name, author_name):
    repo.create_pull(title = "Schemas for user " + author_name, body = "Schemas for user " + author_name, base = MAIN_BRANCH_NAME, head = branch_name)
