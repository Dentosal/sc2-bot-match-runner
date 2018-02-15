## SC2 Bot Match Runner

Tournament runner scripts for running Starcraft II Bots in different Git repos
against each other. The repos are expected to contain a fork of the
[`python-sc2-bot-template`](https://github.com/Dentosal/python-sc2-bot-template).

### Setup

```
pip3 install -r requirements.txt
```

### Running a match

Run the runner script like this:

```
python3 rungame.py <map_name> <repo1> <repo2>
```

For example

```
export REPO1="https://github.com/raimohanska/python-sc2-bot-template.git"
export REPO2="https://github.com/raimohanska/python-sc2-bot-template.git"
python3 rungame.py "Abyssal Reef" $REPO1 $REPO2
```
