import argparse
import hashlib
import json
import os
from pathlib import Path


SIGNATURES_PATH = Path(__file__).resolve().with_name("signatures.json")


def load_signatures(path=SIGNATURES_PATH):
    try:
        with open(path, "r", encoding="utf-8") as signature_file:
            signatures = json.load(signature_file)
        if not isinstance(signatures, dict):
            raise ValueError("Signature database must contain a JSON object")
        return signatures
    except (OSError, json.JSONDecodeError, ValueError) as error:
        raise RuntimeError(
            f"Unable to load signature database at {path}: {error}"
        ) from error


def get_sha256(file_path):
    sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    except (PermissionError, OSError):
        return None


def scan_directory(folder_path, malware_hashes=None):
    if malware_hashes is None:
        malware_hashes = load_signatures()

    print(f"Scanning: {folder_path}\n")
    infected_count = 0

    for root, _, files in os.walk(folder_path):
        for file in files:
            full_path = os.path.join(root, file)
            file_hash = get_sha256(full_path)

            if file_hash in malware_hashes:
                threat_name = malware_hashes[file_hash]
                print(f"[ALERT] Threat detected: {full_path} ({threat_name})")
                infected_count += 1

    print(f"\nScan complete. Threats found: {infected_count}")
    return infected_count


def main():
    parser = argparse.ArgumentParser(
        description="Scan a directory for files matching known SHA-256 signatures."
    )
    parser.add_argument(
        "--path",
        metavar="PATH",
        help="directory to scan; prompts interactively when omitted",
    )
    args = parser.parse_args()

    target_folder = args.path
    if target_folder is None:
        target_folder = input("Enter folder path to scan: ").strip().strip('"')

    target_folder = os.path.expandvars(os.path.expanduser(target_folder))
    if os.path.isdir(target_folder):
        try:
            scan_directory(target_folder)
        except RuntimeError as error:
            parser.error(str(error))
    else:
        parser.error(f"Invalid folder path: {target_folder}")


if __name__ == "__main__":
    main()
