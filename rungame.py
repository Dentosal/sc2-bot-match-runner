#!/usr/bin/env python3
# for usage run: ./rungame.py --help

PROCESS_POLL_INTERVAL = 3 # seconds

from pathlib import Path
import random
import time
import json
import argparse
import subprocess as sp
import shutil

from repocache import RepoCache
import read_replay

class ImageName:
    @staticmethod
    def make(repocache, repos):
        return "sc2_" + ".".join([f"{repocache.repo_name(repo)}__{repocache.latest_hash(repo)}" for repo in repos]).lower()

    @staticmethod
    def parse(name):
        assert name.startswith("sc2_")
        name = name[4:]
        return [namedtuple(**zip(("repo", "commit_hash"), repo.rsplit("__", 1))) for repo in name.split(".")]

def copy_contents(from_directory: Path, to_directory: Path):
    for path in from_directory.iterdir():
        fn = shutil.copy if path.is_file() else shutil.copytree
        fn(path, to_directory)

def prepend_all(prefix, container):
    return [r for item in container for r in [prefix, item]]

def create_empty_dir(path):
    p = Path(path)
    if p.exists():
        shutil.rmtree(p)
    p.mkdir(parents=True)
    return p

def fetch_repositories(matches, containers_dir, repocache, noupdate):
    """Clone repos and create match folders"""

    for i_match, repos in enumerate(matches):
        container = containers_dir / f"match{i_match}"
        for i, repo in enumerate(repos):
            repo_path = repocache.get(repo, pull=(not noupdate))
            shutil.copytree(repo_path, container / f"repo{i}")

def collect_bot_info(matches, containers_dir):
    botinfo_by_match = []
    for i_match, repos in enumerate(matches):
        botinfo_by_match.append([])
        container = containers_dir / f"match{i_match}"
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
    return botinfo_by_match

def main():
    TIME_START_MS = int(time.time()*1000) # milliseconds

    parser = argparse.ArgumentParser(description="Automatically run sc2 matches and collect results.")
    parser.add_argument("--noupdate", action="store_true", help="do not update cached repositories")
    time_group = parser.add_mutually_exclusive_group()
    time_group.add_argument("--realtime", action="store_true", help="run in realtime mode")
    time_group.add_argument("--step-time-limit", nargs=1, default=None, help="step time limit in realtime seconds")
    parser.add_argument("--game-time-limit", nargs=1, default=None, help="game time limit in game seconds")
    parser.add_argument("map_name", type=str, help="map name")
    parser.add_argument("repo", type=str, nargs="+", help="a list of repositories")
    args = parser.parse_args()

    if len(args.repo) % 2 != 0:
        exit(f"There must be even number of repositories ({len(args.repo)} is odd).")

    for repo in args.repo:
        if not repo.startswith("https://"):
            print(f"Please use https url to repo, and not {repo}")
            exit(2)

    sp.run(["./downloadlinuxpackage.sh"], check=True)

    sc2_linux_dir = Path("StarCraftII").resolve(strict=True)
    if (not (sc2_linux_dir / "Maps").exists()) or list((sc2_linux_dir / "Maps").iterdir()) == []:
        print("Error: Linux SC2 directory doesn't contain any maps")
        exit(2)

    containers_dir = create_empty_dir("containers")
    result_dir = create_empty_dir(Path("results") / str(TIME_START_MS))

    start_all = time.time()
    start = start_all

    repocache = RepoCache()

    matches = [
        [args.repo[i], args.repo[i+1]]
        for i in range(0, len(args.repo), 2)
    ]

    print("Fetching repositiories...")
    start = time.time()
    fetch_repositories(matches, containers_dir, repocache, noupdate=args.noupdate)
    print(f"Ok ({time.time() - start:.2f}s)")


    print("Collecting bot info...")
    start = time.time()
    botinfo_by_match = collect_bot_info(matches, containers_dir)
    races_by_match = [[b["race"] for b in info] for info in botinfo_by_match]
    print(f"Ok ({time.time() - start:.2f}s)")

    print("Starting games...")
    start = time.time()
    docker_images = sp.check_output(["docker", "image", "ls", "--format", "{{.Repository}}"]).decode("utf-8").split("\n")
    for i_match, repos in enumerate(matches):
        container = containers_dir / f"match{i_match}"

        copy_contents(Path("template_container"), container)

        image_name = ImageName.make(repocache, repos)
        process_name =  f"sc2_match{i_match}"


        sp.run(["docker", "rm", process_name], cwd=container, check=False)

        if image_name not in docker_images: # is this image is already built?
            sp.run(["docker", "build", "-t", image_name, "."], cwd=container, check=True)

        env = {
            "sc2_match_id": str(i_match),
            "sc2_map_name": args.map_name,
            "sc2_races": ",".join(races_by_match[i_match]),
        }

        if args.step_time_limit is not None:
            env["sc2_step_time_limit"] = str(float(args.step_time_limit[0]))

        if args.game_time_limit is not None:
            env["sc2_game_time_limit"] = str(float(args.game_time_limit[0]))

        # TODO: args.realtime

        sp.run([
            "docker", "run", "-d",
            *prepend_all("--env", [f"{k}={v}" for k,v in env.items()]),
            "--mount", ",".join(map("=".join, {
                "type": "bind",
                "source": str(sc2_linux_dir),
                "destination": "/StarCraftII",
                "readonly": "true",
                "consistency": "cached"
            }.items())),
            "--mount", ",".join(map("=".join, {
                "type": "bind",
                "source": str(result_dir.resolve(strict=True)),
                "destination": "/replays",
                "readonly": "false",
                "consistency": "consistent"
            }.items())),
            "--name", process_name,
            image_name
        ], cwd=container, check=True)

    print(f"Ok ({time.time() - start:.2f}s)")

    print("Running game...")
    start = time.time()
    while True:
        docker_process_ids = sp.check_output([
            "docker", "ps", "-q",
            "--filter", f"volume={sc2_linux_dir}"
        ]).split()

        if len(docker_process_ids) == 0:
            break

        time.sleep(PROCESS_POLL_INTERVAL)

    print(f"Ok ({time.time() - start:.2f}s)")

    print("Collecting results...")
    start = time.time()
    winners = []
    record_ok = []
    for i_match, repos in enumerate(matches):
        winner_info = None

        for i, repo in enumerate(repos):
            try:
                replay_winners = read_replay.winners(result_dir / f"{i_match}_{i}.SC2Replay")
            except FileNotFoundError:
                print(f"Process match{i_match}:repo{i} didn't record a replay")
                continue

            if winner_info is None:
                winner_info = replay_winners
            elif winner_info != replay_winners:
                print(f"Conflicting winner information (match{i_match}:repo{i})")
                print(f"({replay_winners !r})")
                print(f"({winner_info !r})")


        if winner_info is None:
            print(f"No replays were recorded by either client (match{i_match})")
            record_ok.append(False)
            winners.append(None)
            continue

        # TODO: Assumes player_id == (repo_index + 1)
        # Might be possible to at least try to verify this assumption
        for player_id, victory in winner_info.items():
            assert player_id >= 1
            if victory:
                winners.append(player_id - 1)
                break
        else: # Tie
            winners.append(None)
        record_ok.append(True)

    result_data = [
        {
            "record_ok": record_ok[i_match],
            "winner": winners[i_match],
            "repositories": matches[i_match]
        }
        for i_match in range(len(matches))
    ]

    with open(result_dir / "results.json", "w") as f:
        json.dump(result_data, f)

    print(f"Ok ({time.time() - start:.2f}s)")

    print(f"Completed (total {time.time() - start_all:.2f}s)")


if __name__ == "__main__":
    main()
