
import json
import os
import getpass
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

USERNAME = os.getenv("RESTCONF_USERNAME", "admin")
PASSWORD = os.getenv("RESTCONF_PASSWORD") or getpass.getpass(
    "Ange RESTCONF-lösenord: "
)

VERIFY_TLS = False

COLLECTION_FILE = "ARS110-SKILL KONF_SAFE.json"

HEADERS = {
    "Accept": "application/yang-data+json"
}


def load_collection():
    """Läser förväntad konfiguration från Postman."""
    with open(COLLECTION_FILE, "r", encoding="utf-8") as file:
        collection = json.load(file)

    return collection["item"]


def contains_expected(actual, expected):
    """Kontrollerar om förväntade värden finns i GET-svaret."""

    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            return False

        for key, value in expected.items():
            if key not in actual:
                return False

            if not contains_expected(actual[key], value):
                return False

        return True

    if isinstance(expected, list):
        if not isinstance(actual, list):
            return False

        for expected_item in expected:
            found = any(
                contains_expected(actual_item, expected_item)
                for actual_item in actual
            )

            if not found:
                return False

        return True

    return actual == expected


def check_device(session, url, expected, name):
    """Hämtar konfigurationen via RESTCONF GET."""

    try:
        response = session.get(
            url,
            headers=HEADERS,
            timeout=15,
            verify=VERIFY_TLS
        )

        if not response.ok:
            print(
                "[FEL]",
                name,
                "HTTP",
                response.status_code
            )
            return False

        actual = response.json()

        if contains_expected(actual, expected):
            print("[GODKÄND]", name)
            return True

        print("[UNDERKÄND]", name)
        return False

    except (requests.RequestException, ValueError) as error:
        print("[FEL]", name, error)
        return False


def main():
    session = requests.Session()
    session.auth = (USERNAME, PASSWORD)

    try:
        configurations = load_collection()
    except (OSError, json.JSONDecodeError, KeyError) as error:
        print("Kunde inte läsa Postman-filen:", error)
        return

    # Samla konfigurationer per enhet och RESTCONF-sökväg.
    resources = {}

    for item in configurations:
        request_data = item["request"]

        if request_data["method"].upper() != "PATCH":
            continue

        url = request_data["url"]["raw"]
        body = request_data.get("body", {}).get("raw")

        if not body:
            continue

        try:
            expected = json.loads(body)
        except json.JSONDecodeError:
            continue

        resources.setdefault(url, []).append(
            (item["name"], expected)
        )

    passed = 0
    failed = 0

    print("\n=== ROBERT - RESTCONF-KONTROLL ===\n")

    for url, checks in resources.items():

        try:
            response = session.get(
                url,
                headers=HEADERS,
                timeout=15,
                verify=VERIFY_TLS
            )

            if not response.ok:
                print("[FEL] GET", url, response.status_code)
                failed += len(checks)
                continue

            actual = response.json()

            for name, expected in checks:
                if contains_expected(actual, expected):
                    print("[GODKÄND]", name)
                    passed += 1
                else:
                    print("[UNDERKÄND]", name)
                    failed += 1

        except (requests.RequestException, ValueError) as error:
            print("[FEL]", url, error)
            failed += len(checks)

    print("\n=== SLUTRESULTAT ===")
    print("Godkända kontroller:", passed)
    print("Underkända kontroller:", failed)

    if failed == 0:
        print("RESULTAT: GODKÄND")
    else:
        print("RESULTAT: FEL I KONFIGURATIONEN")

    session.close()


if __name__ == "__main__":
    main()
