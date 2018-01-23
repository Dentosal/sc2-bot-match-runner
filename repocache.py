import string

from pathlib import Path
import subprocess as sp

class RepoCache(object):
    PATH = Path("repocache/")
    def __init__(self):
        if not self.PATH.exists():
            self.PATH.mkdir()
        assert self.PATH.is_dir()

    @staticmethod
    def repo_name(url):
        if url.endswith("/"):
            url = url[:-1]

        if url.endswith(".git"):
            url = url[:-4]

        owner, name = url.rsplit("/")[-2:]
        while "__" in owner:
            owner = owner.replace("__", "_")
        return f"{owner}__{name}"

    def _clone(self, name, url):
        print("CLONE")
        sp.run(
            ["git", "clone", url, name],
            cwd=self.PATH,
            check=True, stdout=sp.DEVNULL, stderr=sp.DEVNULL
        )

    def _pull(self, name):
        print("PULL")
        sp.run(
            ["git", "pull"],
            cwd=(self.PATH / name),
            check=True, stdout=sp.DEVNULL, stderr=sp.DEVNULL
        )

    def _ensure_newest(self, name, url):
        if (self.PATH / name).exists():
            self._pull(name)
        else:
            self._clone(name, url)

    def get(self, url):
        name = RepoCache.repo_name(url)
        self._ensure_newest(name, url)
        return self.PATH / name
