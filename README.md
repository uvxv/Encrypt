# Encrypt

<p align="center">
	<a href="https://github.com/uvxv/Encrypt/actions/workflows/security-audit.yml"><img src="https://github.com/uvxv/Encrypt/actions/workflows/security-audit.yml/badge.svg" alt="Python Security Audit"></a>
	<a href="https://github.com/uvxv/Encrypt/releases"><img src="https://img.shields.io/github/v/release/uvxv/Encrypt?label=release" alt="Latest Release"></a>
</p>

A lightweight CLI folder encryption and decryption tool built with Python using **AES-256-GCM** and **scrypt** key derivation (`pycryptodome`).

## Features

- **Authenticated AES-256-GCM encryption:** Protects confidentiality and integrity with a per-file random 16-byte salt, 12-byte nonce, and 16-byte GCM authentication tag (48 bytes total overhead — no Base64 bloat).
- **Any-length passwords:** Derives a 256-bit key via `scrypt` instead of requiring a fixed 16-character key. Passwords are hidden while typing and confirmed during encryption.
- **Streaming I/O:** Processes files in 1 MiB chunks so large files use minimal RAM.
- **Crash-safe atomic writes:** Writes to a temporary file first and only replaces/removes the original after encryption or GCM authentication succeeds.
- **Interactive & CLI modes:** Run with no arguments for guided prompts (double-click friendly), or pass flags (`-e`, `-d`, `-p`) for scripting.
- **Standalone Windows executable:** Available as a single `encrypt.exe` with no Python installation required.

## Quick Start (Windows Executable)

1. Download `encrypt.exe` from the [Releases](https://github.com/uvxv/Encrypt/releases) page.
2. Double-click `encrypt.exe` for interactive mode, or run it from PowerShell / Command Prompt.

## Running from Source

### Prerequisites
- Python 3.10+
- `pycryptodome`

### Setup & Run
```bash
git clone https://github.com/uvxv/Encrypt.git
cd Encrypt
pip install -r requirements.txt
python encrypt.py
```

## Usage

### Interactive Mode
Run `encrypt.exe` (or `python encrypt.py`) with no arguments:

```text
Encrypt v2.0.0 - Folder Encryption/Decryption Tool (AES-256-GCM)

Select whether to encrypt or decrypt a folder (e/d, or q to quit): e
Enter the folder path: "C:\Users\You\Documents\MyFolder"
Enter the password:
Confirm the password:
Encrypted: example.txt

Done: 1 encrypted, 0 skipped, 0 failed.
Press Enter to exit...
```


### Command-Line Arguments
```powershell
# Encrypt a folder (prompts securely for password + confirmation)
encrypt.exe -e "C:\Users\You\Documents\MyFolder"

# Decrypt a folder (prompts securely for password)
encrypt.exe -d "C:\Users\You\Documents\MyFolder"

# Non-interactive scripting mode
encrypt.exe -e "C:\Users\You\Documents\MyFolder" -p "your-strong-password"
encrypt.exe -d "C:\Users\You\Documents\MyFolder" -p "your-strong-password"

# Show version or help
encrypt.exe --version
encrypt.exe --help
```

## Building the Standalone Executable

For the smallest executable, build inside a clean virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install pyinstaller pycryptodome
.\.venv\Scripts\python.exe -m PyInstaller --onefile --clean --icon="$PWD\favicon.ico" --workpath build --distpath dist --specpath build encrypt.py
```

The standalone executable will be generated at `dist/encrypt.exe`.

## Project Structure

```text
Encrypt/
├── .github/workflows/
│   └── security-audit.yml  # Bandit, pip-audit & crypto integrity CI workflow
├── encrypt.py              # Interactive & flag-based CLI for folder encryption/decryption
├── moduleAES.py            # AES-256-GCM + scrypt streaming encryption helpers (AESfile, AEStxt)
├── requirements.txt        # Python runtime dependencies
├── favicon.ico             # Icon embedded into the Windows executable
└── README.md               # Project documentation
```

## Important Notes

- **v2.0.0 format change:** Files encrypted with v2.0.0 use the `ENC2` AES-256-GCM binary format and are **not** compatible with v1.0.0 `.aes` files (which used AES-128-ECB + Base64). Decrypt any v1.0.0 files with v1.0.0 before upgrading.
- **No password recovery:** Keep a backup of important data and store your password safely — encrypted files cannot be recovered without the original password.
