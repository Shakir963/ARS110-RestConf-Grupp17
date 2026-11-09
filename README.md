# ARS110 HT26 – RESTCONF Group Project

## Project description
This project uses Python and RESTCONF to configure and inspect Cisco network devices.

## Project files

- `skill.py` – Applies the network configuration using RESTCONF.
- `robert.py` – Retrieves device information and checks configuration data.
- `requirements.txt` – Lists the required Python packages.
- `ARS110-SKILL KONF_SAFE.json` – Sanitized Postman collection used as configuration input.
- `make_safe.py` – Creates a sanitized copy of the original Postman collection.

## Requirements

- Python 3
- Cisco devices with RESTCONF enabled
- Network connectivity to the management interfaces

## Installation

Install the required package:

```bash
python -m pip install -r requirements.txt
```

## Security

Do not upload files containing passwords, tokens, or other credentials. The original Postman collection is excluded through `.gitignore`.

## Group members

shakir § bilal

