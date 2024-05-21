import random
import requests
import base64

from github import Github, Auth


def get_repo(token, repo_name, repo_owner):
    auth = Auth.Token(token)
    # See here for authentication for private hostname
    # https://pygithub.readthedocs.io/en/stable/introduction.html#very-short-tutorial:~:text=Very%20short
    g = Github(auth=auth)
    repo = g.get_repo(f"{repo_owner}/{repo_name}")
    return repo


def get_latest_sha(token, repo_name, repo_owner):
    branch = get_repo(token, repo_name, repo_owner).get_branch("main")
    return branch.commit.sha


def create_new_branch(token: str, branch_name: str, repo_name: str, repo_owner: str):
    '''
    Creates a github branch with the given name
    '''
    sha = get_latest_sha(token=token, repo_name=repo_name, repo_owner=repo_owner)
    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': f'Bearer {token}',
        'X-GitHub-Api-Version': '2022-11-28'
    }
    data = {
        'ref': f'refs/heads/{branch_name}',
        'sha': sha
    }
    url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/git/refs'
    response = requests.post(url, headers=headers, json=data)
    return response


def create_new_graphing_pr(
        repo_name: str,
        repo_owner: str,
        token: str,
        graph_title: str,
        graphing_file_full_path: str,
        new_code: str) -> str:
    '''
    Creates a pull request in the given repo containing the new code. The file to add
    to is specified by graphing_file_full_path and the title of the pr is given by
    graph_title.

    Returns the url of the pull request.
    '''
    branch_name = graph_title.strip().replace(' ', '-').lower() + \
        f'-{random.randrange(1000, 9999)}'

    create_new_branch(
        token=token, branch_name=branch_name, repo_name=repo_name, repo_owner=repo_owner
    )
    repo = get_repo(token=token, repo_name=repo_name, repo_owner=repo_owner)
    contents = repo.get_contents(graphing_file_full_path, ref='main')
    decoded_content = base64.b64decode(contents.content).decode('utf-8')
    new_code = '\n\n' + new_code
    repo.update_file(
        path=contents.path,
        message="Add graphing function",
        content=decoded_content + new_code,
        sha=contents.sha,
        branch=branch_name
    )
    pr = repo.create_pull(
        base="main",
        head=branch_name,
        title=f"Add graph: {graph_title}",
        body='This PR was automatically generated for adding graphing functionality.'
    )
    return pr._html_url.value