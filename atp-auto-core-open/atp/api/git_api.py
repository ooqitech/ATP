
import gitlab

from atp.config.load_config import load_config
from atp.env import RUNNING_ENV

_config = load_config(RUNNING_ENV)


class GitlabAPI(object):
    def __init__(self):
        self.gl = gitlab.Gitlab(_config.GIT_URL, _config.GIT_PRIVATE_TOKEN)

    def get_all_projects(self):
        projects = self.gl.projects.list(all=True)
        result_list = []
        for project in projects:
            result_list.append(project.ssh_url_to_repo)
        return result_list

    def get_project_branches(self, userspace_name):
        project = self.gl.projects.get(userspace_name)
        branches_name_list = []
        for branch in project.branches.list():
            branches_name_list.append(branch.name)
        return branches_name_list

if __name__ == '__main__':
    git = GitlabAPI()
    print(git.get_all_projects())
