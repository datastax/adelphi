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

from github import Github

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('adelphi')

# We're assuming any storage repo will be created after the conversion to "main"
MAIN_BRANCH_NAME = "main"

ORIGIN_REPO = "datastax/adelphi-schemas"

def build_github(token):
    return Github(token)

def build_origin_repo(gh):
    return gh.get_repo(ORIGIN_REPO)

def build_branch(gh, repo):
    main_branch = repo.get_branch(MAIN_BRANCH_NAME)
    branch_name = "_".join([gh.get_user().login, str(uuid.uuid4())])
    repo.create_git_ref(ref="refs/heads/" + branch_name, sha=main_branch.commit.sha)
    return branch_name

def commit_schemas(gh, repo, schema_dir, branch_name):
    curr_user_name = gh.get_user().login
    for schema in os.listdir(schema_dir):
        repo_path = "/".join([curr_user_name, schema])
        schema_file_path = os.path.join(schema_dir, schema)
        schema_str = open(schema_file_path).read()
        repo.create_file(path=repo_path, message="Schema " + schema, content=schema_str, branch=branch_name)

def build_pull_request(gh, origin_repo, branch_name):
    curr_user_name = gh.get_user().login
    title_str = "Schemas for user {}".format(curr_user_name)
    origin_repo.create_pull(title = title_str, body = title_str, base = MAIN_BRANCH_NAME, head = ":".join([curr_user_name, branch_name]))
