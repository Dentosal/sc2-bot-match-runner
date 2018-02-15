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

        owner, name = url.replace("+", "").rsplit("/")[-2:]
        while "__" in owner:
            owner = owner.replace("__", "_")
        return f"{owner}__{name}"

    def latest_hash(self, url):
        return sp.check_output(["git", "rev-parse", "HEAD"], cwd=self.PATH).strip().decode("utf-8")

    def _clone(self, name, url):
        sp.run(
            ["git", "clone", url, name],
            cwd=self.PATH,
            check=True, stdout=sp.DEVNULL, stderr=sp.DEVNULL
        )

    def _pull(self, name):
        sp.run(
            ["git", "pull"],
            cwd=(self.PATH / name),
            check=True, stdout=sp.DEVNULL, stderr=sp.DEVNULL
        )

    def _download(self, name, url, pull=True):
        if (self.PATH / name).exists():
            if pull:
                self._pull(name)
        else:
            self._clone(name, url)

    def get(self, url, pull=True):
        name = RepoCache.repo_name(url)
        self._download(name, url, pull)
        return self.PATH / name

    def get_cached(self, url):
        return (self.PATH / RepoCache.repo_name(url)).resolve(strict=True)
