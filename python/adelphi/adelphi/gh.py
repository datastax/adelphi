# Copyright DataStax, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# Functionality necessary to create a feature branch + pull request on Github

import logging
import os
import os.path
import uuid

from github import Github, InputGitAuthor

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('adelphi')

# We're assuming any storage repo will be created after the converstion to "main"
MAIN_BRANCH_NAME = "main"

def build_github(token):
    log.info("Repository token: " + token)
    return Github(token)

def build_repository(gh, repo_name):
    log.info("Repository name: " + repo_name)
    return gh.get_repo(repo_name)

def build_branch(gh, repo, author_name):
    main_branch = repo.get_branch(MAIN_BRANCH_NAME)
    branch_name = "_".join([author_name, str(uuid.uuid4())])
    repo.create_git_ref(ref="refs/heads/" + branch_name, sha=main_branch.commit.sha)
    return branch_name

def commit_schemas(gh, repo, schema_dir, branch_name, author_name):
    author_obj = gh.get_user(author_name)
    for schema in os.listdir(schema_dir):
        repo_path = "/".join([author_obj.login, schema])
        schema_file_path = os.path.join(schema_dir,schema)
        schema_str = open(schema_file_path).read()
        repo.create_file(path=repo_path, message="Schema " + schema, content=schema_str, branch=branch_name, author=InputGitAuthor(author_obj.name, author_obj.email))

def build_pull_request(repo, branch_name, author_name):
    repo.create_pull(title = "Schemas for user " + author_name, body = "Schemas for user " + author_name, base = MAIN_BRANCH_NAME, head = branch_name)
