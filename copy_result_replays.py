import argparse
import platform
assert platform.system() == "Darwin", "Currently only supported on macOS"

import json
import shutil
from pathlib import Path

import repocache

def resolve_dir(args):
    accounts_dir = (Path().home() / "Library/Application Support/Blizzard/StarCraft II/Accounts").resolve(strict=True)

    if args.account_id:
        account_id = args.account_id
    else:
        accounts = list(accounts_dir.iterdir())
        if len(accounts) == 0:
            print("No accounts found")
            exit(2)
        elif len(accounts) > 1:
            print("Please specify account_id")
            exit(2)
        else:
            account_id = accounts[0]

    servers_dir = (accounts_dir / account_id).resolve(strict=True)

    if args.server_id:
        server_id = args.server_id
    else:
        servers = [n for n in servers_dir.iterdir() if n.suffix != ".txt" and n.name != "Hotkeys"]
        if len(servers) == 0:
            print(f"No servers found for account {account_id}")
            exit(2)
        elif len(servers) > 1:
            print("Please specify server_id")
            exit(2)
        else:
            server_id = servers[0]

    server_dir = (servers_dir / server_id).resolve(strict=True)
    return (server_dir / "Replays" / "Multiplayer").resolve(strict=True)

def copy_replays(args, target_dir):
    source_dir = Path("results")

    rc = repocache.RepoCache()

    for timestamp_dir in source_dir.iterdir():
        if args.timestamp and timestamp_dir.name != args.timestamp[0]:
            continue

        with open(timestamp_dir / "results.json") as f:
            results = json.load(f)

        for i_match, result in enumerate(results):
            if not result["record_ok"]:
                print(f"WARNING: Missing record for match{i_match} in {timestamp_dir}")
                print("=> Not copying")
                continue

            names = []
            for repo_url in result["repositories"]:
                with open(rc.get_cached(repo_url) / "botinfo.json") as f:
                    names.append(json.load(f)["name"])

            target_path = target_dir / f"{timestamp_dir.name}_{'_vs_'.join(names)}.SC2Replay"
            shutil.copy2(timestamp_dir / f"{i_match}_0.SC2Replay", target_path)

            # WIP:
            # if args.use_bot_names:
            #     import re
            #
            #     with open(target_path, "rb") as f:
            #         replay = f.read()
            #
            #     for i, foo_name in enumerate(re.findall(br"foo\d{5}", replay)):
            #         assert foo_name in replay
            #         print(foo_name, bytes(names[i], "utf-8")[:8])
            #         replay = replay.replace(foo_name, bytes(names[i], "utf-8")[:8])
            #
            #     with open(target_path, "wb") as f:
            #         f.write(replay)
            #
            #     print(target_path)


def main(args):
    target_dir = resolve_dir(args)
    copy_replays(args, target_dir)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Move and rename SC2 replay files")
    parser.add_argument("account_id", nargs="?", help="Account id")
    parser.add_argument("server_id", nargs="?", help="Server id")
    parser.add_argument("--timestamp", nargs=1, default=None, help="specify run timestamp. Defaults to all timestamps.")
    # parser.add_argument("--use-bot-names", action="store_true", help="Use correct bot names in the replay")
    args = parser.parse_args()

    main(args)
