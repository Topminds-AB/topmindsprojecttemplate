"""Access the assigned API-KEYS share with a normal service-owned Psono session."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import threading
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import nacl.encoding
import nacl.exceptions
import nacl.bindings
import nacl.signing
import nacl.utils
from nacl.public import Box, PrivateKey, PublicKey
from nacl.secret import SecretBox


ROOT = Path(__file__).resolve().parents[1]
SERVICE_USER = "svc-agents-dev@psono.localhost"
SETTING_NAMES = (
    "PSONO_AGENT_SERVER_URL",
    "PSONO_AGENT_API_KEY_ID",
    "PSONO_AGENT_API_PRIVATE_KEY_HEX",
    "PSONO_AGENT_API_SECRET_KEY_HEX",
    "PSONO_AGENT_SERVER_PUBLIC_KEY_HEX",
    "PSONO_AGENT_SERVER_SIGNATURE_HEX",
    "PSONO_AGENT_FOLDER_ID",
)
SAFE_ENV_NAMES = {
    "PATH", "SystemRoot", "WINDIR", "TEMP", "TMP", "USERPROFILE",
    "APPDATA", "LOCALAPPDATA", "HOME",
}
UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
_WRITE_LOCK = threading.RLock()


class PsonoError(RuntimeError):
    """A sanitized client, configuration, or API error."""


class PsonoAccessError(PsonoError):
    """Psono denied a requested object."""


def _dotenv(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        name = name.strip()
        if name in SETTING_NAMES:
            values[name] = value.strip().strip('"').strip("'")
    return values


@dataclass(frozen=True)
class Config:
    server_url: str
    api_key_id: str
    api_private_key_hex: str
    api_secret_key_hex: str
    server_public_key_hex: str
    server_signature_hex: str
    folder_id: str

    @classmethod
    def load(cls, env_file: Path | None = None) -> "Config":
        file_values = _dotenv(env_file or ROOT / ".env")
        values = {name: os.environ.get(name, file_values.get(name, "")) for name in SETTING_NAMES}
        missing = [name for name, value in values.items() if not value]
        if missing:
            raise PsonoError("missing configuration: " + ", ".join(missing))
        try:
            for name in (
                "PSONO_AGENT_API_PRIVATE_KEY_HEX",
                "PSONO_AGENT_API_SECRET_KEY_HEX",
                "PSONO_AGENT_SERVER_PUBLIC_KEY_HEX",
                "PSONO_AGENT_SERVER_SIGNATURE_HEX",
            ):
                bytes.fromhex(values[name])
            if len(bytes.fromhex(values["PSONO_AGENT_API_SECRET_KEY_HEX"])) != SecretBox.KEY_SIZE:
                raise ValueError
            if len(bytes.fromhex(values["PSONO_AGENT_SERVER_PUBLIC_KEY_HEX"])) != PublicKey.SIZE:
                raise ValueError
            if len(bytes.fromhex(values["PSONO_AGENT_SERVER_SIGNATURE_HEX"])) != nacl.bindings.crypto_sign_PUBLICKEYBYTES:
                raise ValueError
            if not UUID_RE.fullmatch(values["PSONO_AGENT_FOLDER_ID"]):
                raise ValueError
            if not values["PSONO_AGENT_SERVER_URL"].startswith("https://"):
                raise ValueError
        except (ValueError, TypeError):
            raise PsonoError("invalid PSONO_AGENT_* configuration format") from None
        return cls(
            values["PSONO_AGENT_SERVER_URL"].rstrip("/"),
            values["PSONO_AGENT_API_KEY_ID"],
            values["PSONO_AGENT_API_PRIVATE_KEY_HEX"],
            values["PSONO_AGENT_API_SECRET_KEY_HEX"],
            values["PSONO_AGENT_SERVER_PUBLIC_KEY_HEX"],
            values["PSONO_AGENT_SERVER_SIGNATURE_HEX"],
            values["PSONO_AGENT_FOLDER_ID"],
        )


def _encrypt(value: str | bytes, key: bytes) -> dict[str, str]:
    nonce = nacl.utils.random(SecretBox.NONCE_SIZE)
    box = SecretBox(key)
    encrypted = box.encrypt(value.encode() if isinstance(value, str) else value, nonce)
    return {"text": encrypted[SecretBox.NONCE_SIZE :].hex(), "nonce": nonce.hex()}


def _decrypt(text: str, nonce: str, key: bytes) -> bytes:
    return SecretBox(key).decrypt(bytes.fromhex(text), bytes.fromhex(nonce))


def _decrypt_hex_key(text: str, nonce: str, key: bytes) -> bytes:
    return bytes.fromhex(_decrypt(text, nonce, key).decode("ascii"))


class PsonoAgent:
    """One authenticated session; decrypted entry values remain in process memory."""

    def __init__(self, config: Config, consumer_root: Path = ROOT):
        self.config = config
        self.consumer_root = consumer_root
        self.token: str | None = None
        self.session_key: bytes | None = None
        self.user_secret_key: bytes | None = None
        self._items: dict[str, dict[str, Any]] = {}
        self._folder: dict[str, Any] | None = None
        self._share_id: str | None = None
        self._share_key: bytes | None = None
        self._share_ciphertext: tuple[str, str] | None = None
        self._share_write_date: str | None = None
        self._configured_root_reference = False

    @property
    def folder_id(self) -> str:
        return self.config.folder_id

    @property
    def share_id(self) -> str | None:
        return self._share_id

    @classmethod
    def from_env(cls, env_file: Path | None = None) -> "PsonoAgent":
        consumer_root = env_file.resolve().parent if env_file else ROOT
        return cls(Config.load(env_file), consumer_root=consumer_root)

    def __enter__(self) -> "PsonoAgent":
        self.connect()
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def _request(self, method: str, path: str, body: dict[str, Any] | None = None) -> tuple[int, dict[str, Any]]:
        data: bytes | None = None
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = "Token " + self.token
        if body is not None:
            if self.session_key:
                encrypted = _encrypt(json.dumps(body, separators=(",", ":")), self.session_key)
                body = {"text": encrypted["text"], "nonce": encrypted["nonce"]}
            data = json.dumps(body, separators=(",", ":")).encode("utf-8")
        request = Request(self.config.server_url + path, data=data, headers=headers, method=method)
        try:
            with urlopen(request, timeout=30) as response:
                result = json.loads(response.read().decode("utf-8"))
                status = response.status
        except HTTPError as error:
            if error.code in (403, 404):
                raise PsonoAccessError(f"Psono denied {method} {path} (HTTP {error.code})") from None
            if error.code == 400 and method == "GET" and path.startswith("/secret/"):
                if self._is_permission_denial(error.read()):
                    raise PsonoAccessError(f"Psono denied {method} {path} (permission check)") from None
            raise PsonoError(f"Psono {method} {path} failed (HTTP {error.code})") from None
        except (URLError, TimeoutError, OSError) as error:
            raise PsonoError(f"Psono {method} {path} connection failed ({type(error).__name__})") from None
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise PsonoError(f"Psono {method} {path} returned invalid JSON") from None
        if self.session_key:
            try:
                result = json.loads(_decrypt(result["text"], result["nonce"], self.session_key))
            except (KeyError, ValueError, TypeError, nacl.exceptions.CryptoError):
                raise PsonoError(f"Psono {method} {path} response could not be verified/decrypted") from None
        return status, result

    def _is_permission_denial(self, body: bytes) -> bool:
        try:
            error_data = json.loads(body.decode("utf-8"))
            if self.session_key:
                error_data = json.loads(_decrypt(
                    error_data["text"], error_data["nonce"], self.session_key
                ))
            def contains_code(value: Any) -> bool:
                if value == "NO_PERMISSION_OR_NOT_EXIST":
                    return True
                if isinstance(value, dict):
                    return any(contains_code(child) for child in value.values())
                if isinstance(value, list):
                    return any(contains_code(child) for child in value)
                return False
            return contains_code(error_data)
        except (KeyError, ValueError, TypeError, UnicodeDecodeError, json.JSONDecodeError, nacl.exceptions.CryptoError):
            return False

    def connect(self) -> None:
        if self.token:
            return
        try:
            session_private = PrivateKey.generate()
            session_public = session_private.public_key.encode(encoder=nacl.encoding.HexEncoder).decode()
            info = json.dumps({
                "api_key_id": self.config.api_key_id,
                "session_public_key": session_public,
                "device_description": "Psono Agent " + os.environ.get("COMPUTERNAME", "service"),
            }, separators=(",", ":"))
            signed = nacl.signing.SigningKey(
                self.config.api_private_key_hex, encoder=nacl.encoding.HexEncoder
            ).sign(info.encode("utf-8"))
            _, login = self._request("POST", "/api-key/login/", {
                "info": info,
                "signature": signed.signature.hex(),
            })
            verify_key = nacl.signing.VerifyKey(
                self.config.server_signature_hex, encoder=nacl.encoding.HexEncoder
            )
            verify_key.verify(login["login_info"].encode("utf-8"), bytes.fromhex(login["login_info_signature"]))
            server_public = PublicKey(login["server_session_public_key"], encoder=nacl.encoding.HexEncoder)
            clear = Box(session_private, server_public).decrypt(
                bytes.fromhex(login["login_info"]), bytes.fromhex(login["login_info_nonce"])
            )
            session = json.loads(clear.decode("utf-8"))
            user = session["user"]
            if user.get("username", "").casefold() != SERVICE_USER.casefold():
                raise PsonoError("authenticated account does not match the pinned service identity")
            if session.get("api_key_restrict_to_secrets"):
                raise PsonoError("configured API key is restricted to specific secrets")
            api_secret = bytes.fromhex(self.config.api_secret_key_hex)
            self.user_secret_key = _decrypt_hex_key(
                user["secret_key"], user["secret_key_nonce"], api_secret
            )
            self.session_key = bytes.fromhex(session["session_secret_key"])
            self.token = session["token"]
            self._verify_server_info()
        except PsonoError:
            self.close()
            raise
        except (KeyError, ValueError, TypeError, nacl.exceptions.CryptoError, json.JSONDecodeError):
            self.close()
            raise PsonoError("Psono session handshake failed validation") from None

    def _verify_server_info(self) -> None:
        saved_token, saved_key = self.token, self.session_key
        self.token = None
        self.session_key = None
        try:
            _, response = self._request("GET", "/info/")
            info_text = response["info"]
            verify_hex = response["verify_key"]
            signature_hex = response["signature"]
            if verify_hex.lower() != self.config.server_signature_hex.lower():
                raise PsonoError("Psono server signature key did not match configured key")
            nacl.signing.VerifyKey(verify_hex, encoder=nacl.encoding.HexEncoder).verify(
                info_text.encode("utf-8"), bytes.fromhex(signature_hex)
            )
            info = json.loads(info_text)
            if info.get("public_key", "").lower() != self.config.server_public_key_hex.lower():
                raise PsonoError("Psono server public key did not match configured key")
        except PsonoError:
            raise
        except (KeyError, ValueError, TypeError, nacl.exceptions.CryptoError, json.JSONDecodeError):
            raise PsonoError("Psono server information signature check failed") from None
        finally:
            self.token, self.session_key = saved_token, saved_key

    def close(self) -> None:
        if self.token and self.session_key:
            try:
                self._request("POST", "/authentication/logout/", {})
            except PsonoError:
                pass
        self.token = None
        self.session_key = None
        self.user_secret_key = None
        self._items.clear()
        self._folder = None
        self._share_id = None
        self._share_key = None
        self._share_ciphertext = None
        self._share_write_date = None
        self._configured_root_reference = False

    def _load_share(self) -> tuple[dict[str, Any], dict[str, Any]]:
        if self._folder is not None and self._share_id and self._share_key and self._share_ciphertext:
            _, current = self._request("GET", f"/share/{self._share_id}/")
            cipher = (current.get("data", ""), current.get("data_nonce", ""))
            if cipher != self._share_ciphertext or current.get("write_date") != self._share_write_date:
                self._share_ciphertext = cipher
                self._share_write_date = current.get("write_date")
                self._folder = json.loads(_decrypt(cipher[0], cipher[1], self._share_key))
                self._items.clear()
            return current, self._folder

        _, datastores = self._request("GET", "/datastore/")
        root = None
        for datastore in datastores.get("datastores", []):
            if datastore.get("type") != "password":
                continue
            _, data = self._request("GET", f"/datastore/{datastore['id']}/")
            key = _decrypt_hex_key(
                data["secret_key"], data["secret_key_nonce"], self.user_secret_key
            )
            root = json.loads(_decrypt(data["data"], data["data_nonce"], key))
            break
        if root is None:
            raise PsonoError("service account password datastore was not available")

        references: list[tuple[dict[str, Any], str, bytes]] = []
        share_index = root.get("share_index", {})
        def walk(node: dict[str, Any]) -> None:
            node_share = node.get("share_id")
            if node_share:
                index = share_index.get(node_share, {})
                key_hex = node.get("share_secret_key") or index.get("secret_key")
                if key_hex:
                    references.append((node, node_share, bytes.fromhex(key_hex)))
            for child in node.get("folders", []):
                walk(child)
            for child in node.get("items", []):
                if isinstance(child, dict) and child.get("folders"):
                    walk(child)
        walk(root)

        selected = next(
            (ref for ref in references if ref[0].get("id") == self.config.folder_id
             or ref[0].get("share_id") == self.config.folder_id),
            None,
        )
        self._configured_root_reference = bool(selected)
        if selected is None and self.config.folder_id in share_index:
            key_hex = share_index[self.config.folder_id].get("secret_key")
            if key_hex:
                selected = (None, self.config.folder_id, bytes.fromhex(key_hex))
                self._configured_root_reference = True
        if selected is None:
            raise PsonoError("configured shared-folder ID was not found in the service datastore")
        _, self._share_id, self._share_key = selected
        _, share = self._request("GET", f"/share/{self._share_id}/")
        if not share.get("rights", {}).get("read") or not share.get("rights", {}).get("write"):
            raise PsonoError("configured shared folder does not have both read and write rights")
        self._share_ciphertext = (share["data"], share["data_nonce"])
        self._share_write_date = share.get("write_date")
        self._folder = json.loads(_decrypt(share["data"], share["data_nonce"], self._share_key))
        return share, self._folder

    def _target_folder(self, root: dict[str, Any]) -> dict[str, Any]:
        wanted = self.config.folder_id
        candidates: list[dict[str, Any]] = []
        def walk(node: dict[str, Any]) -> None:
            if node.get("id") == wanted or node.get("share_id") == wanted:
                candidates.append(node)
            for child in node.get("folders", []):
                walk(child)
        walk(root)
        if not candidates:
            # A datastore reference confirmed this ID as the root of the resolved share.
            if self._configured_root_reference:
                return root
            raise PsonoError("configured folder was not present in the share data")
        if len(candidates) != 1:
            raise PsonoError("configured folder ID is ambiguous")
        return candidates[0]

    def list_entries(self) -> list[dict[str, str]]:
        _, root = self._load_share()
        folder = self._target_folder(root)
        self._items = {}
        result: list[dict[str, str]] = []
        def walk(node: dict[str, Any]) -> None:
            for item in node.get("items", []):
                if item.get("deleted"):
                    continue
                if "secret_id" not in item or "secret_key" not in item:
                    continue
                self._items[item["secret_id"]] = item
                result.append({
                    "id": item["secret_id"],
                    "name": str(item.get("name", "")),
                    "type": str(item.get("type", "")),
                    "folder_id": str(node.get("id", self.config.folder_id)),
                })
            for child in node.get("folders", []):
                walk(child)
        walk(folder)
        return result

    def read_entry(self, secret_id: str) -> dict[str, Any]:
        if secret_id not in self._items:
            self.list_entries()
        item = self._items.get(secret_id)
        if item is None:
            raise PsonoAccessError("secret is not present in the assigned shared folder")
        _, data = self._request("GET", f"/secret/{secret_id}/")
        clear = _decrypt(data["data"], data["data_nonce"], bytes.fromhex(item["secret_key"]))
        return json.loads(clear.decode("utf-8"))

    def secret(self, secret_id: str) -> dict[str, Any]:
        """Compatibility alias for consumers that call an entry a secret."""
        return self.read_entry(secret_id)

    def read_selected(self, title: str) -> str:
        """Return the unique entry's password field without printing or persisting it."""
        matches = [entry for entry in self.list_entries() if entry["name"] == title]
        if len(matches) != 1:
            raise PsonoError("selected entry title was not unique in the assigned folder")
        content = self.read_entry(matches[0]["id"])
        password_fields = [
            value for name, value in content.items()
            if name.endswith("_password") and isinstance(value, str) and value
        ]
        if len(password_fields) != 1:
            raise PsonoError("selected entry did not contain exactly one password field")
        return password_fields[0]

    def confirm_server_denies(self, secret_id: str) -> None:
        """Issue a real API read for a supplied boundary ID and require a denial."""
        if not UUID_RE.fullmatch(secret_id):
            raise PsonoError("boundary secret ID must be a verified UUID")
        try:
            self._request("GET", f"/secret/{secret_id}/")
        except PsonoAccessError:
            return
        raise PsonoError("Psono server allowed the boundary secret read")

    def run_selected(self, selections: Iterable[tuple[str, str, str]], command: list[str]) -> int:
        if not command:
            raise PsonoError("a child command is required")
        child_env = {name: value for name, value in os.environ.items() if name in SAFE_ENV_NAMES}
        for env_name, secret_id, field in selections:
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", env_name):
                raise PsonoError("invalid child environment variable name")
            value = self.read_entry(secret_id).get(field)
            if not isinstance(value, str) or not value:
                raise PsonoError(f"selected field {field} is missing or empty")
            child_env[env_name] = value
        return subprocess.call(
            command,
            env=child_env,
            cwd=self.consumer_root,
            shell=False,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )

    def create_application_password(self, payload: dict[str, Any]) -> str:
        with _WRITE_LOCK:
            return self._create_application_password(payload)

    def _create_application_password(self, payload: dict[str, Any]) -> str:
        title = payload.get("name")
        password = payload.get("password")
        notes = payload.get("notes", "")
        if not isinstance(title, str) or not title.strip() or not isinstance(password, str) or not password:
            raise PsonoError("put requires non-empty name and password strings")
        if not isinstance(notes, str):
            raise PsonoError("put notes must be a string")
        share, root = self._load_share()
        folder = self._target_folder(root)
        if not share.get("rights", {}).get("write"):
            raise PsonoError("configured shared folder is not writable")
        existing_titles: set[str] = set()
        def collect_titles(node: dict[str, Any]) -> None:
            existing_titles.update(
                str(entry.get("name", "")).casefold()
                for entry in node.get("items", []) if not entry.get("deleted")
            )
            for child in node.get("folders", []):
                collect_titles(child)
        collect_titles(folder)
        if title.casefold() in existing_titles:
            raise PsonoError("an entry with this title already exists in the assigned folder")
        _, latest = self._request("GET", f"/share/{self._share_id}/")
        if ((latest.get("data"), latest.get("data_nonce")) != self._share_ciphertext
                or latest.get("write_date") != self._share_write_date):
            raise PsonoError("shared folder changed; refusing to write from a stale copy")

        secret_key = nacl.utils.random(SecretBox.KEY_SIZE)
        link_id = str(uuid.uuid4())
        secret_data = {
            "application_password_title": title,
            "application_password_password": password,
            "application_password_notes": notes,
        }
        encrypted = _encrypt(json.dumps(secret_data, separators=(",", ":")), secret_key)
        _, created = self._request("PUT", "/secret/", {
            "data": encrypted["text"],
            "data_nonce": encrypted["nonce"],
            "link_id": link_id,
            "parent_share_id": self._share_id,
        })
        secret_id = created.get("secrets_id") or created.get("secret_id")
        if not secret_id:
            raise PsonoError("Psono did not return the created secret ID")

        self._load_share()
        if ((latest.get("data"), latest.get("data_nonce")) != self._share_ciphertext
                or latest.get("write_date") != self._share_write_date):
            raise PsonoError("shared folder changed after secret creation; no share data was overwritten")
        item = {
            "id": link_id,
            "type": "application_password",
            "name": title,
            "secret_id": secret_id,
            "secret_key": secret_key.hex(),
        }
        folder.setdefault("items", []).append(item)
        encrypted_share = _encrypt(json.dumps(root, separators=(",", ":")), self._share_key)
        _, updated = self._request("PUT", "/share/", {
            "share_id": self._share_id,
            "data": encrypted_share["text"],
            "data_nonce": encrypted_share["nonce"],
        })
        self._share_ciphertext = (encrypted_share["text"], encrypted_share["nonce"])
        self._share_write_date = updated.get("write_date")
        self._items.clear()
        return secret_id


def _selection(text: str) -> tuple[str, str, str]:
    env_name, separator, reference = text.partition("=")
    title, field_sep, field = reference.rpartition(":")
    if not separator or not field_sep or not title or not field:
        raise argparse.ArgumentTypeError("expected ENV_NAME=ENTRY_TITLE:FIELD")
    return env_name, title, field


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", type=Path, help="use an existing consumer root .env")
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("status", help="show only service identity and configured folder metadata")
    sub.add_parser("list", help="list metadata for entries in the assigned shared folder")
    run = sub.add_parser("run", help="inject selected fields directly into a child process")
    run.add_argument("--with", dest="selections", action="append", type=_selection, default=[])
    run.add_argument("command", nargs=argparse.REMAINDER)
    put = sub.add_parser("put", help="create an Application Password from JSON read on stdin")
    args = parser.parse_args(argv)
    try:
        with PsonoAgent.from_env(args.env_file) as client:
            if args.action == "status":
                print(json.dumps({"service_user": SERVICE_USER, "folder_id": client.config.folder_id}, separators=(",", ":")))
                return 0
            if args.action == "list":
                for entry in client.list_entries():
                    print(json.dumps(entry, ensure_ascii=False, separators=(",", ":")))
                return 0
            if args.action == "run":
                command = args.command[1:] if args.command and args.command[0] == "--" else args.command
                entries = client.list_entries()
                selections: list[tuple[str, str, str]] = []
                for env_name, title, field in args.selections:
                    matches = [entry for entry in entries if entry["name"] == title]
                    if len(matches) != 1:
                        raise PsonoError("selected entry title was not unique in the assigned folder")
                    selections.append((env_name, matches[0]["id"], field))
                return client.run_selected(selections, command)
            body = json.load(sys.stdin)
            secret_id = client.create_application_password(body)
            print(json.dumps({"created": True, "secret_id": secret_id}, separators=(",", ":")))
            return 0
    except (PsonoError, OSError, json.JSONDecodeError) as error:
        message = str(error) if isinstance(error, PsonoError) else "invalid JSON input or local file access failed"
        print(f"psono_agent: {message}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
