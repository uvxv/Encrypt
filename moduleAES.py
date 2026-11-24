import base64
from contextlib import suppress
import os
import tempfile
# Using actively maintained pycryptodome (shares the Crypto namespace with legacy pycrypto)
from Crypto.Cipher import AES  # nosec B413
from Crypto.Protocol.KDF import scrypt  # nosec B413
from Crypto.Random import get_random_bytes  # nosec B413

MAGIC = b"ENC2"
SALT_SIZE = 16
NONCE_SIZE = 12
TAG_SIZE = 16
KEY_SIZE = 32  # AES-256
HEADER_SIZE = len(MAGIC) + SALT_SIZE + NONCE_SIZE  # 32 bytes
CHUNK_SIZE = 1024 * 1024  # 1 MiB

# scrypt parameters (N=2^14, r=8, p=1 -> ~16 MiB RAM, fast per-file derivation)
SCRYPT_N = 2**14
SCRYPT_R = 8
SCRYPT_P = 1


class DecryptionError(ValueError):
    """Raised when decryption fails due to an invalid format, wrong password, or tampered data."""


# For secure derivation of the key
def _derive_key(password: str, salt: bytes) -> bytes:
    if not password:
        raise ValueError("Password cannot be empty")
    return scrypt(
        password.encode("utf-8"),
        salt,
        key_len=KEY_SIZE,
        N=SCRYPT_N,
        r=SCRYPT_R,
        p=SCRYPT_P,
    )


class AEStxt:
    @staticmethod
    def encryption(password: str, text: str) -> bytes:
        salt = get_random_bytes(SALT_SIZE)
        nonce = get_random_bytes(NONCE_SIZE)
        header = MAGIC + salt + nonce
        key = _derive_key(password, salt)

        # Generate the ciphertext and authentication tag
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        cipher.update(header)
        ciphertext, tag = cipher.encrypt_and_digest(text.encode("utf-8"))
        return base64.b64encode(header + ciphertext + tag)

    @staticmethod
    def decryption(password: str, token: bytes | str) -> str:
        try:
            raw = base64.b64decode(token)
        except Exception as exc:
            raise DecryptionError("Invalid Base64 ciphertext") from exc

        if len(raw) < HEADER_SIZE + TAG_SIZE or raw[: len(MAGIC)] != MAGIC:
            raise DecryptionError("Invalid or unsupported encrypted data format")

        header = raw[:HEADER_SIZE]
        salt = header[len(MAGIC) : len(MAGIC) + SALT_SIZE]
        nonce = header[len(MAGIC) + SALT_SIZE : HEADER_SIZE]
        ciphertext = raw[HEADER_SIZE:-TAG_SIZE]
        tag = raw[-TAG_SIZE:]

        key = _derive_key(password, salt)
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        cipher.update(header)
        try:
            plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        except ValueError as exc:
            raise DecryptionError("Incorrect password or corrupted data") from exc
        return plaintext.decode("utf-8")


def _cleanup_temp(tmp_path: str) -> None:
    if os.path.exists(tmp_path):
        with suppress(OSError):
            os.remove(tmp_path)


class AESfile:
    @staticmethod
    def encrypt_file(src_path: str, dst_path: str, password: str) -> None:
        """Stream-encrypt src_path to dst_path using AES-256-GCM with an atomic temp file."""
        salt = get_random_bytes(SALT_SIZE)
        nonce = get_random_bytes(NONCE_SIZE)
        header = MAGIC + salt + nonce
        key = _derive_key(password, salt)

        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        cipher.update(header)

        target_dir = os.path.dirname(os.path.abspath(dst_path)) or "."
        with open(src_path, "rb") as src_file:
            fd, tmp_path = tempfile.mkstemp(prefix=".enc_", suffix=".tmp", dir=target_dir)
            try:
                with os.fdopen(fd, "wb") as dst_file:
                    dst_file.write(header)
                    while True:
                        chunk = src_file.read(CHUNK_SIZE)
                        if not chunk:
                            break
                        dst_file.write(cipher.encrypt(chunk))
                    dst_file.write(cipher.digest())
                    dst_file.flush()
                    os.fsync(dst_file.fileno())
            except BaseException:
                _cleanup_temp(tmp_path)
                raise

        try:
            os.replace(tmp_path, dst_path)
            os.remove(src_path)
        except BaseException:
            _cleanup_temp(tmp_path)
            raise

    @staticmethod
    def decrypt_file(src_path: str, dst_path: str, password: str) -> None:
        """Stream-decrypt and authenticate src_path to dst_path; leaves src_path intact on failure."""
        file_size = os.path.getsize(src_path)
        if file_size < HEADER_SIZE + TAG_SIZE:
            raise DecryptionError("File is too small or not a valid v2 .aes file")

        ciphertext_len = file_size - HEADER_SIZE - TAG_SIZE
        target_dir = os.path.dirname(os.path.abspath(dst_path)) or "."

        with open(src_path, "rb") as src_file:
            header = src_file.read(HEADER_SIZE)
            if len(header) != HEADER_SIZE or header[: len(MAGIC)] != MAGIC:
                raise DecryptionError("Unsupported or corrupted .aes file header")

            salt = header[len(MAGIC) : len(MAGIC) + SALT_SIZE]
            nonce = header[len(MAGIC) + SALT_SIZE : HEADER_SIZE]
            key = _derive_key(password, salt)

            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
            cipher.update(header)

            fd, tmp_path = tempfile.mkstemp(prefix=".dec_", suffix=".tmp", dir=target_dir)
            try:
                with os.fdopen(fd, "wb") as dst_file:
                    remaining = ciphertext_len
                    while remaining > 0:
                        chunk = src_file.read(min(CHUNK_SIZE, remaining))
                        if not chunk:
                            raise DecryptionError("Unexpected end of file during decryption")
                        dst_file.write(cipher.decrypt(chunk))
                        remaining -= len(chunk)

                    tag = src_file.read(TAG_SIZE)
                    if len(tag) != TAG_SIZE:
                        raise DecryptionError("Missing authentication tag")

                    try:
                        cipher.verify(tag)
                    except ValueError as exc:
                        raise DecryptionError("Incorrect password or corrupted file") from exc

                    dst_file.flush()
                    os.fsync(dst_file.fileno())
            except BaseException:
                _cleanup_temp(tmp_path)
                raise

        try:
            os.replace(tmp_path, dst_path)
            os.remove(src_path)
        except BaseException:
            _cleanup_temp(tmp_path)
            raise
