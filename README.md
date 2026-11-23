# Encrypt

A lightweight CLI-based folder encryption and decryption tool built with Python and AES-128 (`pycryptodome`).

## Features

- **Recursive folder processing:** Encrypts or decrypts all files inside a directory and its subdirectories.
- **AES-128 encryption:** Encrypts file contents using AES (ECB mode with PKCS7 padding and Base64 encoding) and appends a `.aes` extension.
- **Safe re-runs:** Skips files that are already encrypted (`.aes`) when encrypting, and skips non-`.aes` files when decrypting.
- **Password verification:** Detects invalid passwords during decryption before overwriting files.
- **Standalone executable:** Available as a single Windows `.exe` with no Python installation required.

## Quick Start (Windows Executable)

1. Download `encrypt.exe` from the [Releases](https://github.com/uvxv/Encrypt/releases) page.
2. Double-click `encrypt.exe` or run it from PowerShell / Command Prompt.

## Running from Source

### Prerequisites
- Python 3.8+
- `pycryptodome`

### Setup & Run
```bash
git clone https://github.com/uvxv/Encrypt.git
cd Encrypt
pip install pycryptodome
python encrypt.py
```

## Usage

When launched, follow the interactive prompts:

```text
This program is to encrypt/decrypt the folders

Select whether to encrypt of decrypt a folder (e/d): e
Enter the absolute folder path: C:\Users\You\Documents\MyFolder
Enter the password: my16charpassword
Encrypted the file example.txt
Press any key to exit...
```

- Enter **`e`** to encrypt all unencrypted files in the folder (adds `.aes` to each filename).
- Enter **`d`** to decrypt all `.aes` files in the folder (restores the original filenames).
- Provide the **absolute path** to a directory (not an individual file).
- Use a password that is **exactly 16 characters** long.

## Building the Standalone Executable

To package `encrypt.py` into a single Windows executable yourself:

```powershell
pip install pyinstaller pycryptodome
python -m PyInstaller --onefile --clean --icon=favicon.ico encrypt.py
```

Or rebuild directly from the saved spec file:

```powershell
python -m PyInstaller encrypt.spec
```

The standalone executable will be generated at `dist/encrypt.exe`.

## Project Structure

```text
Encrypt/
├── encrypt.py       # Interactive CLI entry point for folder encryption/decryption
├── moduleAES.py     # AES encryption/decryption helpers (AESfile, AEStxt)
├── favicon.ico      # Icon embedded into the Windows executable
├── encrypt.spec     # PyInstaller build configuration
└── README.md        # Project documentation
```

## Important Notes

- **Password length:** Passwords must be **exactly 16 characters** (128-bit AES key).
- **In-place modification:** Files are encrypted and decrypted in place. Always keep a backup of important files and store your password safely — lost passwords cannot be recovered.
- **Security note:** This tool uses AES in ECB mode and is best suited for lightweight personal or educational use rather than high-security production encryption.
