import json
from pathlib import Path

source = Path("ARS110-SKILL KONF.json")
destination = Path("ARS110-SKILL KONF_SAFE.json")

with source.open("r", encoding="utf-8") as file:
    data = json.load(file)


def remove_credentials(obj):
    if isinstance(obj, dict):
        # Ta bort hela autentiseringsblock
        obj.pop("auth", None)

        # Ta bort känsliga fält
        for key in list(obj.keys()):
            if key.lower() in (
                "password", "passwd", "username",
                "token", "secret", "authorization"
            ):
                del obj[key]
            else:
                remove_credentials(obj[key])

    elif isinstance(obj, list):
        for item in obj:
            remove_credentials(item)


remove_credentials(data)

with destination.open("w", encoding="utf-8") as file:
    json.dump(data, file, indent=2, ensure_ascii=False)

print("Säker kopia skapad:", destination)