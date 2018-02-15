import os
import sys
from pathlib import Path
import shlex

import sc2


portconfig = sc2.portconfig.Portconfig()
gameid = os.environ["sc2_match_id"]

commands = [
    [
        "cd" # home directory
    ], [
        "cd", "repo"
    ], [
        "python3", "start_bot.py",
        os.environ["sc2_map_name"],
        os.environ["sc2_races"],
        portconfig.as_json,
    ]
]

if "sc2_step_time_limit" in os.environ:
    commands[-1] += ["--step-time-limit", os.environ["sc2_step_time_limit"]]
if "sc2_game_time_limit" in os.environ:
    commands[-1] += ["--game-time-limit", os.environ["sc2_game_time_limit"]]

if os.fork() == 0:
    commands[-1] += ["--master"]
    commands[-1] += ["--log-path", f"/replays/{gameid}_0.log"]
    commands[-1] += ["--replay-path", f"/replays/{gameid}_0.SC2Replay"]
    os.execlp("runuser", "-l", "user0", "-c", " && ".join(" ".join(shlex.quote(c) for c in cmd) for cmd in commands))
else:
    # HACK: Delay the joining client so the host has time to start up
    import time; time.sleep(5)

    commands[-1] += ["--log-path", f"/replays/{gameid}_1.log"]
    commands[-1] += ["--replay-path", f"/replays/{gameid}_1.SC2Replay"]
    os.execlp("runuser", "-l", "user1", "-c", " && ".join(" ".join(shlex.quote(c) for c in cmd) for cmd in commands))
