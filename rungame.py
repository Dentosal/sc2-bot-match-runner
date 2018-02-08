#!python3
# usage: ./rungame.py [args] repo1 repo2

from pathlib import Path
import random
import time
import json
import argparse
import subprocess as sp
import shutil

from repocache import RepoCache
import read_replay

def copy_contents(from_directory: Path, to_directory: Path):
    for path in from_directory.iterdir():
        fn = shutil.copy if path.is_file() else shutil.copytree
        fn(path, to_directory)

def prepend_all(prefix, container):
    return [r for item in container for r in [prefix, item]]

def main():
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument("--realtime", action="store_true", help="run in realtime mode")
    parser.add_argument("map_name", type=str, help="map name")
    parser.add_argument("repo", type=str, nargs="+", help="a list of repositories")
    args = parser.parse_args()

    if len(args.repo) != 2:
        exit("There must be exactly two repositories.")

    for repo in args.repo:
        if not repo.startswith("https://"):
            print(f"Please use https url to repo, and not {repo}")
            exit(2)

    # TODO: args.realtime

    # Create empty containers/ directory (removes the old one)
    containers = Path("containers")
    if containers.exists():
        shutil.rmtree(containers)
    containers.mkdir()

    # Create empty results/ directory (removes the old one)
    results = Path("results")
    if results.exists():
        shutil.rmtree(results)
    results.mkdir()

    # Create empty results/ directory (removes the old one)
    replays = Path("replays")
    if replays.exists():
        shutil.rmtree(replays)
    replays.mkdir()

    start_all = time.time()
    start = start_all

    repocache = RepoCache()

    MATCHES = [[args.repo[0], args.repo[1]]]

    # Clone repos and create match folders
    print("Fetching repositiories...")
    for i_match, repos in enumerate(MATCHES):
        container = containers / f"match{i_match}"
        for i, repo in enumerate(repos):
            repo_path = repocache.get(repo)
            shutil.copytree(repo_path, container / f"repo{i}")

    print(f"Ok ({time.time() - start:.2f}s)")

    # Collect bot info
    botinfo_by_match = []
    for i_match, repos in enumerate(MATCHES):
        botinfo_by_match.append([])
        container = containers / f"match{i_match}"
        for i, repo in enumerate(repos):
            botinfo_file = container / f"repo{i}" / "botinfo.json"

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

            botinfo_by_match[-1].append(botinfo)

    races_by_match = [[b["race"] for b in info] for info in botinfo_by_match]

    processes = []
    start = time.time()
    print("Starting games...")
    for i_match, repos in enumerate(MATCHES):
        container = containers / f"match{i_match}"

        # stdout_log = open(container / "stdout.log", "a")
        # stderr_log = open(container / "stderr.log", "a")
        # stdout=stdout_log, stderr=stderr_log, cwd=container

        copy_contents(Path("template_container"), container)
        shutil.copytree(Path("/Users/dento/Desktop/python-sc2"), container / "python-sc2")
        # HACK: using mount would be better, but it doesn't work is so slow that
        #       it just seems to block forever.
        # shutil.copytree(Path("StarCraftII"), container / "StarCraftII")

        image_name =  f"sc2_repo{0}_vs_repo{1}_image"
        process_name =  f"sc2_repo{0}_vs_repo{1}"

        sp.run(["docker", "rm", process_name], cwd=container, check=False)
        sp.run(["docker", "build", "-t", image_name, "."], cwd=container, check=True)
        sp.run([
            "docker", "run", "-d",
            "--env", f"sc2_match_id={i_match}",
            "--env", f"sc2_map_name={args.map_name}",
            "--env", f"sc2_races={','.join(races_by_match[i_match])}",
            "--mount", ",".join(map("=".join, {
                "type": "bind",
                "source": str(Path("StarCraftII").resolve(strict=True)),
                "destination": "/StarCraftII",
                "readonly": "true",
                "consistency": "cached"
            }.items())),
            "--mount", ",".join(map("=".join, {
                "type": "bind",
                "source": str(Path("replays").resolve(strict=True)),
                "destination": "/replays",
                "readonly": "false",
                "consistency": "consistent"
            }.items())),
            "--name", process_name,
            image_name
        ], cwd=container, check=True)

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
            print(f"Process  match{i} terminated with non-zero exit code ({rc})")

    print(f"Ok ({time.time() - start:.2f}s)")

    exit()

    start = time.time()
    print("Collecting results...")
    winner_info = None
    for i_match, repos in enumerate(MATCHES):
        rp = containers / f"repo{i}" / "replay.SC2Replay"
        try:
            winners = read_replay.winners(rp)
        except FileNotFoundError:
            print(f"Process repo{i} didn't record a replay")
            continue

        if winner_info is None:
            winner_info = winners
        else:
            if winner_info != winners:
                print(f"Conflicting winner information (repo{i})")
                print(f"({winners !r})")

    if winner_info is None:
        print("No replays were recorded by any process")
        exit(1)

    # TODO: Assumes player_id == repo_index
    # Might be possible to at least try to verify this assumption
    winner_id = [player_id for player_id, victory in winner_info.items() if victory][0]

    result_name = "+".join([RepoCache.repo_name(n) for n in args.repo])
    result_dir = Path("results") / result_name

    result_dir.mkdir(parents=True)

    with open(result_dir / "result.json", "w") as f:
        json.dump({"winner": f"repo{winner_id}"}, f)

    print(f"Ok ({time.time() - start:.2f}s)")

    print(f"Completed (total {time.time() - start_all:.2f}s)")


if __name__ == "__main__":
    main()
