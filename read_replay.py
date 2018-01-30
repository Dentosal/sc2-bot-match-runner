import json
from mpyq import MPQArchive

def winners(filepath):
    archive = MPQArchive(str(filepath))
    files = archive.extract()
    data = json.loads(files[b"replay.gamemetadata.json"])
    result_by_playerid = {p["PlayerID"]: p["Result"] for p in data["Players"]}
    return {playerid: result=="Win" for playerid, result in result_by_playerid.items()}
