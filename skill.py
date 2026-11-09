
import json
import os
import getpass
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# RESTCONF-inställningar
USERNAME = os.getenv("RESTCONF_USERNAME", "admin")
PASSWORD = os.getenv("RESTCONF_PASSWORD") or getpass.getpass(
    "Ange RESTCONF-lösenord: "
)

VERIFY_TLS = False

COLLECTION_FILE = "ARS110-SKILL KONF_SAFE.json"

HEADERS = {
    "Content-Type": "application/yang-data+json",
    "Accept": "application/yang-data+json"
}


def load_collection():
    """Läser konfigurationerna från Postman-exporten."""
    with open(COLLECTION_FILE, "r", encoding="utf-8") as file:
        collection = json.load(file)

    return collection["item"]


def configure_device(session, item):
    """Skickar ett separat RESTCONF PATCH-anrop."""

    request_data = item["request"]

    if request_data["method"].upper() != "PATCH":
        return None

    url = request_data["url"]["raw"]

    body = request_data.get("body", {}).get("raw")

    if not body:
        print("[SKIP] Ingen JSON-konfiguration:", item["name"])
        return None

    try:
        payload = json.loads(body)

        response = session.patch(
            url,
            json=payload,
            headers=HEADERS,
            timeout=15,
            verify=VERIFY_TLS
        )

        if response.ok:
            print(
                "[OK]",
                item["name"],
                "HTTP",
                response.status_code
            )
            return True

        print(
            "[FEL]",
            item["name"],
            "HTTP",
            response.status_code
        )
        print(response.text[:300])
        return False

    except (requests.RequestException, ValueError) as error:
        print("[FEL]", item["name"], error)
        return False


def main():
    session = requests.Session()
    session.auth = (USERNAME, PASSWORD)

    try:
        configurations = load_collection()
    except (OSError, json.JSONDecodeError, KeyError) as error:
        print("Kunde inte läsa Postman-filen:", error)
        return

    success = 0
    failed = 0

    print("\n=== SKILLA - RESTCONF ===\n")

    for item in configurations:
        result = configure_device(session, item)

        if result is True:
            success += 1
        elif result is False:
            failed += 1

    print("\n=== RESULTAT ===")
    print("Lyckade anrop:", success)
    print("Misslyckade anrop:", failed)

    session.close()


if __name__ == "__main__":
    main()
