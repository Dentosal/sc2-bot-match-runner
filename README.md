## SC2 Bot Match Runner

Tournament runner scripts for running Starcraft II Bots in different Git repos
against each other. The repos are expected to contain a fork of the
[`python-sc2-bot-template`](https://github.com/Dentosal/python-sc2-bot-template). Runs matches in parallel 
using docker containers.

### Setup

```
pip3 install -r requirements.txt
```

### Running a match

Run the runner script like this:

```
python3 rungame.py <map_name> <repo1> <repo2> --step-time-limit 2.0 --game-time-limit 1200
```

For example

```
export REPO1="https://github.com/dentosal/python-sc2-bot-template.git"
export REPO2="https://github.com/dentosal/python-sc2-bot.git"
python3 rungame.py "Abyssal Reef LE" $REPO1 $REPO2
```

You can run multiple pairs at once too! The matches will be run in parallel in separate docker containers.

Results will be stored under the `results/<timestamp>` directory. 

Bot logs will be produced into files in this directory in realtime.

Each bot client will create its replay file into this directory after the match is over.
This means that for each match there will be two essentially identical replay files. The runner verifies that
the replays contain the same result.

After all matches have finished, a `results.json` file will be created. It contains the result of all matches.

### Debugging

If running gets stuck, you may want to

```
    docker ps
    docker logs <container_id>
```

### Generating match list from list of repo URLs

```
python3 make_matches.py --type round-robin $REPO1 $REPO2 $REPO3
```

### Viewing match replays

The runner stores match results under `results/<timestamp>` directories. You can easily copy all the match replays
into your StarCraft II installation directory using

```
    python3 copy_result_replays.py <accountid> <serverid>
```

You can find your accountid and serverid as directory names under `~/Library/Application Support/Blizzard/StarCraft II/Accounts`.

Now you can open the replays using the Starcraft UI: they can be found in Replays.
