import hashlib
import os

# Known malicious SHA-256 hashes (includes the safe EICAR test file hash)
MALWARE_HASHES = {
    "275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f": "EICAR-Test-File"
}

def get_sha256(file_path):
    sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    except (PermissionError, OSError):
        return None

def scan_directory(folder_path):
    print(f"Scanning: {folder_path}\n")
    infected_count = 0

    for root, _, files in os.walk(folder_path):
        for file in files:
            full_path = os.path.join(root, file)
            file_hash = get_sha256(full_path)

            if file_hash in MALWARE_HASHES:
                threat_name = MALWARE_HASHES[file_hash]
                print(f"[ALERT] Threat detected: {full_path} ({threat_name})")
                infected_count += 1

    print(f"\nScan complete. Threats found: {infected_count}")

if __name__ == "__main__":
    target_folder = input("Enter folder path to scan: ").strip('"')
    if os.path.isdir(target_folder):
        scan_directory(target_folder)
    else:
        print("Invalid folder path.")
