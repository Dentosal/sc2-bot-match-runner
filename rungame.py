#!python3
# usage: ./rungame.py [args] repo1 repo2

from pathlib import Path
import random
import time
import json
import argparse
import subprocess as sp
import shutil

import sc2

from repocache import RepoCache
import read_replay

def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--realtime', action='store_true', help='run in realtime mode')
    parser.add_argument('map_name', type=str, help='map name')
    parser.add_argument('repo', type=str, nargs="+", help='a list of repositories')
    args = parser.parse_args()

    if len(args.repo) != 2:
        exit("There must be exactly two repositories.")

    for repo in args.repo:
        if not repo.startswith("https://"):
            print(f"Please use https url to repo, and not {repo}")
            exit(2)

    # args.realtime

    portconfig = sc2.portconfig.Portconfig()

    # Create empty containers/ directory (removes the old one)
    containers = Path("containers")
    if containers.exists():
        shutil.rmtree(containers)
    containers.mkdir()

    start_all = time.time()
    start = start_all

    repocache = RepoCache()

    # Clone repos
    print("Fetching repositiories...")
    for i, repo in enumerate(args.repo):
        repo_path = repocache.get(repo)
        container = containers / f"repo{i}"
        shutil.copytree(repo_path, container)
    print(f"Ok ({time.time() - start:.2f}s)")

    # Collect bot info
    botinfo_by_repo_index = []
    for i, repo in enumerate(args.repo):
        container = containers / f"repo{i}"
        botinfo_file = container / "botinfo.json"

        if not botinfo_file.exists():
            print(f"File botinfo.json is missing for repo{i}")
            exit(3)

        with open(botinfo_file) as f:
            botinfo = json.load(f)

        REQUIRED_KEYS = {"race": str, "name": str}
        for k, t in REQUIRED_KEYS.items():
            if k not in botinfo or not isinstance(botinfo[k], t):
                print(f"Invalid botinfo.json for repo{i}:")
                print(f"Key '{k}' missing, or type is not {t !r}")
                exit(3)

        botinfo_by_repo_index.append(botinfo)

    races_arg = ",".join(b["race"] for b in botinfo_by_repo_index)

    processes = []
    start = time.time()
    print("Starting game...")
    for i, repo in enumerate(args.repo):
        container = containers / f"repo{i}"

        botinfo = botinfo_by_repo_index[i]

        cmd_args = ["python3", "start_bot.py"]
        if i == 0:
            cmd_args.append("--master")
        cmd_args += [args.map_name, races_arg, portconfig.as_json]

        stdout_log = open(container / "stdout.log", "a")
        stderr_log = open(container / "stderr.log", "a")
        p = sp.Popen(cmd_args, stdout=stdout_log, stderr=stderr_log, cwd=container)
        processes.append(p)

    print(f"Ok ({time.time() - start:.2f}s)")

    start = time.time()
    print("Running game...")
    while True:
        return_codes = []
        for i, p in enumerate(processes):
            return_code = p.poll()
            if return_code is None:
                continue
            return_codes.append(return_code)

        if len(return_codes) == len(processes):
            break

        time.sleep(1)

    for i, rc in enumerate(return_codes):
        if rc != 0:
            print(f"Process repo{i} terminated with non-zero exit code ({rc})")

    print(f"Ok ({time.time() - start:.2f}s)")


    start = time.time()
    print("Collecting results...")
    winner_info = None
    for i, repo in enumerate(args.repo):
        rp = containers / f"repo{i}" / "replay.SC2Replay"
        winners = read_replay.winners(rp)
        if winner_info is None:
            winner_info = winners
        else:
            if winner_info != winners:
                print(f"Conflicting winner information (repo{i})")
                print(f"({winners !r})")

    result_name = "+".join([RepoCache.repo_name(n) for n in args.repo])
    result_dir = Path("Results") / result_name

    result_dir.mkdir(parents=True)

    with open(result_dir / "result.json", "w") as f:
        json.dump(winner_info, f)

    print(f"Ok ({time.time() - start:.2f}s)")

    print(f"Completed (total {time.time() - start_all:.2f}s)")


if __name__ == '__main__':
    main()
