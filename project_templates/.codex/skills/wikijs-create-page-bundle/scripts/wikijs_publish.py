"""Wiki.js publish helper.

This script provides a thin automation layer for creating and updating Wiki.js
pages through GraphQL and uploading screenshot assets through the `/u` endpoint.

The script is intentionally environment-driven and never hardcodes secrets.
It is designed to be used from Codex and Claude skills.
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
from urllib.parse import urljoin

import requests


DEFAULT_TIMEOUT_SECONDS = 60
DEFAULT_EDITOR = "markdown"
DEFAULT_LOCALE = "en"


@dataclass(frozen=True)
class WikiConfig:
    """Runtime configuration for Wiki.js API access.

    Attributes:
        base_url: Canonical Wiki.js base URL without a trailing slash.
        api_token: Bearer token used for GraphQL and upload requests.
        default_locale: Default locale code for page operations.
        default_editor: Default editor key for page operations.
        timeout_seconds: HTTP timeout in seconds.
        verify_tls: Whether TLS certificates should be verified.
    """

    base_url: str
    api_token: str
    default_locale: str = DEFAULT_LOCALE
    default_editor: str = DEFAULT_EDITOR
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS
    verify_tls: bool = True


class WikiJsError(RuntimeError):
    """Raised when a Wiki.js operation fails."""


def load_config() -> WikiConfig:
    """Load configuration from environment variables.

    Returns:
        A fully validated WikiConfig instance.

    Raises:
        WikiJsError: If a required environment variable is missing.
    """
    base_url = os.getenv("WIKIJS_URL", "").strip().rstrip("/")
    api_token = os.getenv("WIKIJS_API_TOKEN", "").strip()
    default_locale = os.getenv("WIKIJS_DEFAULT_LOCALE", DEFAULT_LOCALE).strip() or DEFAULT_LOCALE
    default_editor = os.getenv("WIKIJS_DEFAULT_EDITOR", DEFAULT_EDITOR).strip() or DEFAULT_EDITOR
    timeout_raw = os.getenv("WIKIJS_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS)).strip()
    verify_tls_raw = os.getenv("WIKIJS_VERIFY_TLS", "true").strip().lower()
    verify_tls = verify_tls_raw not in {"0", "false", "no", "off"}

    missing = []
    if not base_url:
        missing.append("WIKIJS_URL")
    if not api_token:
        missing.append("WIKIJS_API_TOKEN")
    if missing:
        raise WikiJsError(f"Missing required environment variable(s): {', '.join(missing)}.")

    try:
        timeout_seconds = int(timeout_raw)
    except ValueError as exc:
        raise WikiJsError("Invalid WIKIJS_TIMEOUT_SECONDS: expected an integer.") from exc

    return WikiConfig(
        base_url=base_url,
        api_token=api_token,
        default_locale=default_locale,
        default_editor=default_editor,
        timeout_seconds=timeout_seconds,
        verify_tls=verify_tls,
    )


def build_headers(config: WikiConfig) -> Dict[str, str]:
    """Build HTTP headers for authenticated requests.

    Args:
        config: Runtime configuration.

    Returns:
        Headers including bearer authentication.
    """
    return {
        "Authorization": f"Bearer {config.api_token}",
        "Content-Type": "application/json",
    }


def graphql_request(config: WikiConfig, query: str, variables: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a GraphQL request against Wiki.js.

    Args:
        config: Runtime configuration.
        query: GraphQL document string.
        variables: GraphQL variables.

    Returns:
        Parsed JSON response.

    Raises:
        WikiJsError: If the HTTP request or GraphQL response fails.
    """
    response = requests.post(
        urljoin(config.base_url + "/", "graphql"),
        headers=build_headers(config),
        json={"query": query, "variables": variables},
        timeout=config.timeout_seconds,
        verify=config.verify_tls,
    )
    if not response.ok:
        raise WikiJsError(f"GraphQL HTTP {response.status_code}: {response.text}")

    payload = response.json()
    if payload.get("errors"):
        raise WikiJsError(f"GraphQL errors: {json.dumps(payload['errors'], ensure_ascii=False)}")
    return payload


def sanitize_page_path(page_path: str) -> str:
    """Normalize a page path for Wiki.js.

    Args:
        page_path: Raw page path.

    Returns:
        Normalized path without scheme or hostname.
    """
    clean_path = page_path.strip()
    clean_path = re.sub(r"^https?://[^/]+", "", clean_path)
    clean_path = clean_path.strip()
    if clean_path in {"", "/"}:
        return "home"
    return clean_path.lstrip("/")


def list_pages(config: WikiConfig, locale: Optional[str] = None) -> List[Dict[str, Any]]:
    """List pages from Wiki.js.

    Args:
        config: Runtime configuration.
        locale: Optional locale filter.

    Returns:
        List of page metadata dictionaries.
    """
    query = """
    query ListPages($locale: String) {
      pages {
        list(locale: $locale) {
          id
          path
          locale
          title
          description
          contentType
          updatedAt
        }
      }
    }
    """
    payload = graphql_request(config, query, {"locale": locale or config.default_locale})
    return payload["data"]["pages"]["list"]


def get_page_by_path(config: WikiConfig, page_path: str, locale: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Fetch a page by path.

    Args:
        config: Runtime configuration.
        page_path: Wiki.js page path.
        locale: Optional locale override.

    Returns:
        The page dictionary if found, otherwise None.

    Raises:
        WikiJsError: If an unexpected GraphQL failure occurs.
    """
    query = """
    query SingleByPath($path: String!, $locale: String!) {
      pages {
        singleByPath(path: $path, locale: $locale) {
          id
          path
          locale
          title
          description
          content
          render
          contentType
          updatedAt
        }
      }
    }
    """
    variables = {
        "path": sanitize_page_path(page_path),
        "locale": locale or config.default_locale,
    }
    try:
        payload = graphql_request(config, query, variables)
    except WikiJsError as exc:
        message = str(exc)
        if (
            "Page Not Found" in message
            or "PageNotFound" in message
            or "This page does not exist" in message
            or '"code": 6003' in message
            or '"singleByPath": null' in message
        ):
            return None
        raise
    return payload["data"]["pages"]["singleByPath"]


def create_page(
    config: WikiConfig,
    title: str,
    description: str,
    page_path: str,
    content: str,
    tags: Iterable[str],
    locale: Optional[str] = None,
    editor: Optional[str] = None,
    is_published: bool = True,
    is_private: bool = False,
) -> Dict[str, Any]:
    """Create a new Wiki.js page.

    Args:
        config: Runtime configuration.
        title: Page title.
        description: Short page description.
        page_path: Wiki.js page path.
        content: Raw page content.
        tags: Page tags.
        locale: Optional locale override.
        editor: Optional editor key override.
        is_published: Whether the page should be published.
        is_private: Whether the page should be private.

    Returns:
        The GraphQL page response block.

    Raises:
        WikiJsError: If Wiki.js reports a failed mutation.
    """
    mutation = """
    mutation CreatePage(
      $content: String!
      $description: String!
      $editor: String!
      $isPublished: Boolean!
      $isPrivate: Boolean!
      $locale: String!
      $path: String!
      $tags: [String]!
      $title: String!
      $scriptCss: String
      $scriptJs: String
    ) {
      pages {
        create(
          content: $content
          description: $description
          editor: $editor
          isPublished: $isPublished
          isPrivate: $isPrivate
          locale: $locale
          path: $path
          tags: $tags
          title: $title
          scriptCss: $scriptCss
          scriptJs: $scriptJs
        ) {
          responseResult {
            succeeded
            errorCode
            slug
            message
          }
          page {
            id
            path
            title
          }
        }
      }
    }
    """
    variables = {
        "content": content,
        "description": description,
        "editor": editor or config.default_editor,
        "isPublished": is_published,
        "isPrivate": is_private,
        "locale": locale or config.default_locale,
        "path": sanitize_page_path(page_path),
        "tags": list(tags),
        "title": title,
        "scriptCss": "",
        "scriptJs": "",
    }
    payload = graphql_request(config, mutation, variables)
    result = payload["data"]["pages"]["create"]
    ensure_response_succeeded(result)
    return result


def update_page(
    config: WikiConfig,
    page_id: int,
    title: str,
    description: str,
    page_path: str,
    content: str,
    tags: Iterable[str],
    locale: Optional[str] = None,
    editor: Optional[str] = None,
    is_published: bool = True,
    is_private: bool = False,
) -> Dict[str, Any]:
    """Update an existing Wiki.js page.

    Args:
        config: Runtime configuration.
        page_id: Existing page identifier.
        title: Page title.
        description: Page description.
        page_path: Desired page path.
        content: Raw page content.
        tags: Page tags.
        locale: Optional locale override.
        editor: Optional editor override.
        is_published: Whether the page should be published.
        is_private: Whether the page should be private.

    Returns:
        The GraphQL page response block.

    Raises:
        WikiJsError: If Wiki.js reports a failed mutation.
    """
    mutation = """
    mutation UpdatePage(
      $id: Int!
      $content: String
      $description: String
      $editor: String
      $isPrivate: Boolean
      $isPublished: Boolean
      $locale: String
      $path: String
      $tags: [String]
      $title: String
      $scriptCss: String
      $scriptJs: String
    ) {
      pages {
        update(
          id: $id
          content: $content
          description: $description
          editor: $editor
          isPrivate: $isPrivate
          isPublished: $isPublished
          locale: $locale
          path: $path
          tags: $tags
          title: $title
          scriptCss: $scriptCss
          scriptJs: $scriptJs
        ) {
          responseResult {
            succeeded
            errorCode
            slug
            message
          }
          page {
            id
            path
            title
          }
        }
      }
    }
    """
    variables = {
        "id": page_id,
        "content": content,
        "description": description,
        "editor": editor or config.default_editor,
        "isPrivate": is_private,
        "isPublished": is_published,
        "locale": locale or config.default_locale,
        "path": sanitize_page_path(page_path),
        "tags": list(tags),
        "title": title,
        "scriptCss": "",
        "scriptJs": "",
    }
    payload = graphql_request(config, mutation, variables)
    result = payload["data"]["pages"]["update"]
    ensure_response_succeeded(result)
    return result


def ensure_response_succeeded(result: Dict[str, Any]) -> None:
    """Validate a Wiki.js mutation response block.

    Args:
        result: Mutation result dictionary with `responseResult`.

    Raises:
        WikiJsError: If the mutation did not succeed.
    """
    response_result = result.get("responseResult") or {}
    if not response_result.get("succeeded"):
        raise WikiJsError(
            "Wiki.js mutation failed: "
            f"{response_result.get('errorCode', 'unknown')} - {response_result.get('message', '')}"
        )


def list_asset_folders(config: WikiConfig, parent_folder_id: int = 0) -> List[Dict[str, Any]]:
    """List asset folders for a parent folder.

    Args:
        config: Runtime configuration.
        parent_folder_id: Parent folder identifier. Use 0 for root.

    Returns:
        List of folder dictionaries.
    """
    query = """
    query AssetFolders($parentFolderId: Int!) {
      assets {
        folders(parentFolderId: $parentFolderId) {
          id
          slug
          name
        }
      }
    }
    """
    payload = graphql_request(config, query, {"parentFolderId": parent_folder_id})
    return payload["data"]["assets"]["folders"]


def create_asset_folder(config: WikiConfig, slug: str, name: str, parent_folder_id: int = 0) -> Dict[str, Any]:
    """Create an asset folder.

    Args:
        config: Runtime configuration.
        slug: Folder slug.
        name: Human-readable folder name.
        parent_folder_id: Parent folder identifier.

    Raises:
        WikiJsError: If the mutation fails.
    """
    mutation = """
    mutation CreateAssetFolder($parentFolderId: Int!, $slug: String!, $name: String) {
      assets {
        createFolder(parentFolderId: $parentFolderId, slug: $slug, name: $name) {
          responseResult {
            succeeded
            slug
            message
          }
        }
      }
    }
    """
    payload = graphql_request(
        config,
        mutation,
        {
            "parentFolderId": parent_folder_id,
            "slug": slug,
            "name": name,
        },
    )
    result = payload["data"]["assets"]["createFolder"]
    response_result = result.get("responseResult") or {}
    if not response_result.get("succeeded"):
        raise WikiJsError(f"Asset folder creation failed: {response_result.get('message', '')}")
    return response_result


def get_or_create_asset_folder(config: WikiConfig, slug: str, name: str, parent_folder_id: int = 0) -> Dict[str, Any]:
    """Return an existing asset folder or create it if missing."""
    for folder in list_asset_folders(config=config, parent_folder_id=parent_folder_id):
        if folder.get("slug") == slug:
            return folder

    create_asset_folder(config=config, slug=slug, name=name, parent_folder_id=parent_folder_id)
    for folder in list_asset_folders(config=config, parent_folder_id=parent_folder_id):
        if folder.get("slug") == slug:
            return folder

    raise WikiJsError(f"Asset folder was created but not found: {slug}")


def ensure_asset_folder_path(config: WikiConfig, folder_path: str) -> Dict[str, Any]:
    """Ensure a slash-separated Wiki.js asset folder path exists."""
    parent_id = 0
    current_path: List[str] = []
    folder: Dict[str, Any] = {}
    for raw_segment in folder_path.strip("/").split("/"):
        segment = raw_segment.strip()
        if not segment:
            continue
        current_path.append(segment)
        folder = get_or_create_asset_folder(
            config=config,
            slug=segment,
            name=segment.replace("-", " ").title(),
            parent_folder_id=parent_id,
        )
        parent_id = int(folder["id"])
    if not folder:
        raise WikiJsError("Asset folder path must contain at least one segment.")
    return {"id": parent_id, "path": "/".join(current_path)}


def guess_mime_type(file_path: Path) -> str:
    """Infer the MIME type for an upload file.

    Args:
        file_path: Path to the asset file.

    Returns:
        MIME type string.
    """
    mime_type, _ = mimetypes.guess_type(str(file_path))
    return mime_type or "application/octet-stream"


def upload_asset(
    config: WikiConfig,
    file_path: Path,
    folder_id: int = 0,
    asset_folder_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Upload one asset file to Wiki.js.

    Args:
        config: Runtime configuration.
        file_path: File to upload.
        folder_id: Destination Wiki.js asset folder identifier.

    Returns:
        A small dictionary describing the inferred uploaded asset path.

    Raises:
        WikiJsError: If the upload fails.
    """
    if not file_path.exists() or not file_path.is_file():
        raise WikiJsError(f"Upload file not found: {file_path}")

    metadata_payload = json.dumps({"folderId": folder_id})
    mime_type = guess_mime_type(file_path)
    headers = {"Authorization": f"Bearer {config.api_token}"}

    with file_path.open("rb") as file_handle:
        files = [
            (
                "mediaUpload",
                (
                    None,
                    metadata_payload,
                    "application/json",
                ),
            ),
            (
                "mediaUpload",
                (
                    file_path.name,
                    file_handle,
                    mime_type,
                ),
            ),
        ]
        response = requests.post(
            urljoin(config.base_url + "/", "u"),
            headers=headers,
            files=files,
            timeout=config.timeout_seconds,
            verify=config.verify_tls,
        )

    if not response.ok:
        raise WikiJsError(f"Upload HTTP {response.status_code}: {response.text}")
    if response.text.strip().lower() != "ok":
        raise WikiJsError(f"Unexpected upload response: {response.text}")

    return {
        "filename": file_path.name,
        "folderId": folder_id,
        "status": "ok",
        "inferredAssetPath": f"/{asset_folder_path.strip('/')}/{file_path.name}" if asset_folder_path else None,
    }


def build_markdown_image_block(image_paths: Iterable[str]) -> str:
    """Build a markdown image block from relative or absolute asset paths.

    Args:
        image_paths: Iterable of image URLs or paths.

    Returns:
        Markdown text containing one image per line.
    """
    lines: List[str] = []
    for image_path in image_paths:
        lines.append(f"![]({image_path})")
    return "\n\n".join(lines)


def create_or_update_page(
    config: WikiConfig,
    title: str,
    description: str,
    page_path: str,
    content: str,
    tags: Iterable[str],
    locale: Optional[str] = None,
    editor: Optional[str] = None,
    is_published: bool = True,
    is_private: bool = False,
    mode: str = "upsert",
) -> Dict[str, Any]:
    """Create, update, or upsert a Wiki.js page.

    Args:
        config: Runtime configuration.
        title: Page title.
        description: Page description.
        page_path: Target page path.
        content: Page content.
        tags: Page tags.
        locale: Optional locale override.
        editor: Optional editor override.
        is_published: Publication flag.
        is_private: Privacy flag.
        mode: One of ``create``, ``update``, or ``upsert``.

    Returns:
        The GraphQL page response block.
    """
    if mode not in {"create", "update", "upsert"}:
        raise WikiJsError(f"Invalid publish mode: {mode}")

    sanitized_path = sanitize_page_path(page_path)
    page = get_page_by_path(config, page_path=page_path, locale=locale)
    if mode == "create" and page is not None:
        raise WikiJsError(f"Page already exists: {sanitized_path}")
    if mode == "update" and page is None:
        raise WikiJsError(f"Page not found: {sanitized_path}")

    if page is None:
        return create_page(
            config=config,
            title=title,
            description=description,
            page_path=page_path,
            content=content,
            tags=tags,
            locale=locale,
            editor=editor,
            is_published=is_published,
            is_private=is_private,
        )

    return update_page(
        config=config,
        page_id=int(page["id"]),
        title=title,
        description=description,
        page_path=page_path,
        content=content,
        tags=tags,
        locale=locale,
        editor=editor,
        is_published=is_published,
        is_private=is_private,
    )


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(description="Create, update, or upsert Wiki.js pages and upload assets.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list-pages", help="List pages in a locale.")
    list_parser.add_argument("--locale", default=None)

    publish_parser = subparsers.add_parser("publish-page", help="Create, update, or upsert one page.")
    publish_parser.add_argument("--title", required=True)
    publish_parser.add_argument("--description", required=True)
    publish_parser.add_argument("--path", required=True)
    publish_parser.add_argument("--content-file", required=True)
    publish_parser.add_argument("--tag", action="append", default=[])
    publish_parser.add_argument("--locale", default=None)
    publish_parser.add_argument("--editor", default=None)
    publish_parser.add_argument("--mode", choices=["create", "update", "upsert"], default="upsert")
    publish_parser.add_argument("--private", action="store_true")
    publish_parser.add_argument("--draft", action="store_true")

    upload_parser = subparsers.add_parser("upload-asset", help="Upload a single asset file.")
    upload_parser.add_argument("--file", required=True)
    upload_parser.add_argument("--folder-id", type=int, default=0)
    upload_parser.add_argument("--asset-folder-path", default=None)

    folders_parser = subparsers.add_parser("list-folders", help="List asset folders.")
    folders_parser.add_argument("--parent-folder-id", type=int, default=0)

    create_folder_parser = subparsers.add_parser("create-folder", help="Create an asset folder.")
    create_folder_parser.add_argument("--slug", required=True)
    create_folder_parser.add_argument("--name", required=True)
    create_folder_parser.add_argument("--parent-folder-id", type=int, default=0)

    ensure_folder_parser = subparsers.add_parser("ensure-folder-path", help="Ensure a nested asset folder path exists.")
    ensure_folder_parser.add_argument("--path", required=True)

    return parser.parse_args()


def read_text_file(file_path: Path) -> str:
    """Read a UTF-8 text file.

    Args:
        file_path: Path to the file.

    Returns:
        File content as a string.
    """
    return file_path.read_text(encoding="utf-8")


def main() -> int:
    """Run the command-line entry point.

    Returns:
        Process exit code.
    """
    try:
        args = parse_args()
        config = load_config()

        if args.command == "list-pages":
            pages = list_pages(config=config, locale=args.locale)
            print(json.dumps(pages, ensure_ascii=False, indent=2))
            return 0

        if args.command == "publish-page":
            content = read_text_file(Path(args.content_file))
            result = create_or_update_page(
                config=config,
                title=args.title,
                description=args.description,
                page_path=args.path,
                content=content,
                tags=args.tag,
                locale=args.locale,
                editor=args.editor,
                is_published=not args.draft,
                is_private=args.private,
                mode=args.mode,
            )
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0

        if args.command == "upload-asset":
            folder_id = args.folder_id
            if args.asset_folder_path and args.folder_id == 0:
                folder = ensure_asset_folder_path(config=config, folder_path=args.asset_folder_path)
                folder_id = int(folder["id"])
            result = upload_asset(
                config=config,
                file_path=Path(args.file),
                folder_id=folder_id,
                asset_folder_path=args.asset_folder_path,
            )
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0

        if args.command == "list-folders":
            folders = list_asset_folders(config=config, parent_folder_id=args.parent_folder_id)
            print(json.dumps(folders, ensure_ascii=False, indent=2))
            return 0

        if args.command == "create-folder":
            result = create_asset_folder(
                config=config,
                slug=args.slug,
                name=args.name,
                parent_folder_id=args.parent_folder_id,
            )
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0

        if args.command == "ensure-folder-path":
            result = ensure_asset_folder_path(config=config, folder_path=args.path)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0

        raise WikiJsError(f"Unknown command: {args.command}")
    except WikiJsError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
