import argparse
import getpass
import os
import sys

from moduleAES import AESfile, DecryptionError

__version__ = "2.0.0"
ENCRYPTED_EXT = ".aes"


def _normalize_path(raw_path: str) -> str:
    return raw_path.strip().strip('"').strip("'")

# Dedcate fucntion for promting pass 
def _prompt_password(prompt: str) -> str:
    if sys.stdin.isatty():
        return getpass.getpass(prompt)
    return input(prompt)


def _get_password(confirm: bool = False) -> str:
    while True:
        password = _prompt_password("Enter the password: ")
        if not password:
            print("Password cannot be empty.")
            continue
        if confirm:
            verify = _prompt_password("Confirm the password: ")
            if password != verify:
                print("Passwords do not match. Please try again.")
                continue
        return password


def _prompt_folder() -> str:
    while True:
        folder_path = _normalize_path(input("Enter the folder path: "))
        if os.path.isdir(folder_path):
            return os.path.abspath(folder_path)
        if os.path.isfile(folder_path):
            print("This is a path to a file. Please enter a folder path.")
        else:
            print("Invalid folder path.")


def _get_self_path() -> str | None:
    try:
        if getattr(sys, "frozen", False):
            return os.path.abspath(sys.executable)
        return os.path.abspath(__file__)
    except OSError:
        return None

# Performs dual similar paths and similar type of file in different paths
def _is_same_file(path_a: str, path_b: str | None) -> bool:
    if not path_b:
        return False
    try:
        return os.path.samefile(path_a, path_b)
    except OSError:
        return False


def folder_encryption(folder_path: str, password: str) -> tuple[int, int, int]:
    encrypted = 0
    skipped = 0
    failed = 0
    self_path = _get_self_path()

    for root, _, files in os.walk(folder_path):
        for file in files:
            src_path = os.path.join(root, file)
            if _is_same_file(src_path, self_path):
                print(f"Skipped self executable: {file}")
                skipped += 1
                continue

            if file.lower().endswith(ENCRYPTED_EXT):
                print(f"Already encrypted: {file}")
                skipped += 1
                continue

            dst_path = src_path + ENCRYPTED_EXT
            if os.path.exists(dst_path):
                print(f"Skipped (target already exists): {file}{ENCRYPTED_EXT}")
                skipped += 1
                continue

            try:
                AESfile.encrypt_file(src_path, dst_path, password)
                print(f"Encrypted: {file}")
                encrypted += 1
            except OSError as exc:
                print(f"Failed to encrypt {file}: {exc}")
                failed += 1

    print(f"\nDone: {encrypted} encrypted, {skipped} skipped, {failed} failed.")
    return encrypted, skipped, failed


def folder_decryption(folder_path: str, password: str) -> tuple[int, int, int]:
    decrypted = 0
    skipped = 0
    failed = 0

    for root, _, files in os.walk(folder_path):
        for file in files:
            src_path = os.path.join(root, file)
            if not file.lower().endswith(ENCRYPTED_EXT):
                print(f"Already decrypted: {file}")
                skipped += 1
                continue

            dst_path = src_path[: -len(ENCRYPTED_EXT)]
            if os.path.exists(dst_path):
                print(f"Skipped (target already exists): {os.path.basename(dst_path)}")
                skipped += 1
                continue

            try:
                AESfile.decrypt_file(src_path, dst_path, password)
                print(f"Decrypted: {file}")
                decrypted += 1
            except DecryptionError as exc:
                print(f"Failed to decrypt {file}: {exc}")
                print("Make sure the password is correct and the file is a valid v2 .aes file.")
                failed += 1
                print(f"\nAborted: {decrypted} decrypted, {skipped} skipped, {failed} failed.")
                return decrypted, skipped, failed
            except OSError as exc:
                print(f"Failed to decrypt {file}: {exc}")
                failed += 1

    print(f"\nDone: {decrypted} decrypted, {skipped} skipped, {failed} failed.")
    return decrypted, skipped, failed


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="encrypt",
        description="Recursively encrypt or decrypt folders using AES-256-GCM.",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("-e", "--encrypt", metavar="FOLDER", help="Encrypt all files in FOLDER")
    mode.add_argument("-d", "--decrypt", metavar="FOLDER", help="Decrypt all .aes files in FOLDER")
    parser.add_argument(
        "-p",
        "--password",
        help="Password (if omitted, you will be prompted securely)",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def _run_interactive() -> int:
    print(f"Encrypt v{__version__} - Folder Encryption/Decryption Tool (AES-256-GCM)\n")

    while True:
        choice = input("Select whether to encrypt or decrypt a folder (e/d, or q to quit): ").strip().lower()
        if choice in ("e", "d"):
            break
        if choice == "q":
            return 0
        print("Invalid choice. Please enter 'e', 'd', or 'q'.")

    folder_path = _prompt_folder()
    password = _get_password(confirm=(choice == "e"))

    if choice == "e":
        _, _, failed = folder_encryption(folder_path, password)
    else:
        _, _, failed = folder_decryption(folder_path, password)

    input("Press Enter to exit...")
    return 1 if failed else 0


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if not args.encrypt and not args.decrypt:
        return _run_interactive()

    target = _normalize_path(args.encrypt or args.decrypt)
    if not os.path.isdir(target):
        print(f"Error: '{target}' is not a valid folder.", file=sys.stderr)
        return 1

    if args.password is not None:
        if not args.password:
            print("Error: Password cannot be empty.", file=sys.stderr)
            return 1
        password = args.password
    else:
        password = _get_password(confirm=bool(args.encrypt))

    if args.encrypt:
        _, _, failed = folder_encryption(os.path.abspath(target), password)
    else:
        _, _, failed = folder_decryption(os.path.abspath(target), password)

    return 1 if failed else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        sys.exit(130)
