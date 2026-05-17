#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optional Gemini Deep Research runner for world-book-skill.

This script is intentionally isolated from the main world-book / character-card
tooling. It only runs when the user explicitly asks for Deep Research.

Auth sources, in priority order:
1. CLI flags
2. .env file values
3. Current process environment variables

Supported auth modes:
- GEMINI_DEEP_RESEARCH_CONFIG_JSON: gcli2api-generated OAuth credential JSON
- GEMINI_API_KEY / GOOGLE_API_KEY: Google AI Studio API key
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


DEFAULT_AGENT = "deep-research-preview-04-2026"
DEFAULT_API_BASE = "https://generativelanguage.googleapis.com/v1beta"
DEFAULT_API_REVISION = "2026-05-20"
DEFAULT_POLL_INTERVAL = 10
DEFAULT_TIMEOUT = 1800
DEFAULT_OUTPUT_DIR = "deep-research-output"
TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"


class ConfigError(RuntimeError):
    """Raised when user configuration is missing or invalid."""


class HttpError(RuntimeError):
    """Raised when an HTTP request fails."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Gemini Deep Research with optional gcli2api OAuth credentials.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python gemini-deep-research.py \\
    --input "Research key worldbuilding facts for Arknights and cite sources." \\
    --output-dir ./deep-research-output

  python gemini-deep-research.py \\
    --env-file /path/to/.env \\
    --input-file ./prompt.txt \\
    --tool url_context

  python gemini-deep-research.py \\
    --interaction-id interactions/abc123 \\
    --output-dir ./deep-research-output
        """,
    )
    parser.add_argument("--input", help="Research prompt text.")
    parser.add_argument("--input-file", help="Read the research prompt from a UTF-8 text file.")
    parser.add_argument("--interaction-id", help="Resume polling an existing interaction id.")
    parser.add_argument("--env-file", help="Optional .env file. Defaults to cwd/.env, then skill-root/.env if present.")
    parser.add_argument("--config-json", help="Path to a gcli2api-generated OAuth credential JSON file.")
    parser.add_argument("--api-key", help="Gemini API key from Google AI Studio.")
    parser.add_argument("--agent", help=f"Deep Research agent id. Default: {DEFAULT_AGENT}")
    parser.add_argument(
        "--tool",
        action="append",
        choices=["google_search", "url_context", "code_execution"],
        help="Optional tool to expose to Deep Research. Can be provided multiple times.",
    )
    parser.add_argument(
        "--poll-interval",
        type=int,
        help=f"Polling interval in seconds. Default: {DEFAULT_POLL_INTERVAL}",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        help=f"Maximum wait time in seconds. Default: {DEFAULT_TIMEOUT}",
    )
    parser.add_argument(
        "--api-revision",
        help=f"Api-Revision header value. Default: {DEFAULT_API_REVISION}",
    )
    parser.add_argument(
        "--output-dir",
        help=f"Directory for research artifacts. Default: {DEFAULT_OUTPUT_DIR}",
    )
    parser.add_argument(
        "--no-wait",
        action="store_true",
        help="Create the interaction and exit immediately after writing the initial JSON artifact.",
    )
    return parser.parse_args()


def strip_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def load_env_file(env_path: Path) -> Dict[str, str]:
    env: Dict[str, str] = {}
    if not env_path.exists():
        raise ConfigError(f".env file not found: {env_path}")
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        env[key.strip()] = strip_quotes(value.strip())
    return env


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def discover_env_file(explicit_env_file: Optional[str]) -> Optional[Path]:
    if explicit_env_file:
        return Path(explicit_env_file).expanduser().resolve()
    env_var = os.environ.get("WORLD_BOOK_SKILL_ENV_FILE")
    if env_var:
        return Path(env_var).expanduser().resolve()
    cwd_candidate = Path.cwd() / ".env"
    if cwd_candidate.exists():
        return cwd_candidate.resolve()
    skill_candidate = skill_root() / ".env"
    if skill_candidate.exists():
        return skill_candidate.resolve()
    return None


def merged_env(args: argparse.Namespace) -> Tuple[Dict[str, str], Optional[Path]]:
    merged = dict(os.environ)
    env_path = discover_env_file(args.env_file)
    if env_path:
        merged.update(load_env_file(env_path))
    return merged, env_path


def first_non_empty(*values: Optional[str]) -> Optional[str]:
    for value in values:
        if value is not None and str(value).strip():
            return str(value).strip()
    return None


def parse_int(value: Optional[str], default: int) -> int:
    if value is None or str(value).strip() == "":
        return default
    return int(str(value).strip())


def parse_iso_datetime(value: Optional[str]) -> Optional[dt.datetime]:
    if not value:
        return None
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = dt.datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def json_dumps(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)


def read_prompt(args: argparse.Namespace) -> str:
    if args.input and args.input_file:
        raise ConfigError("Use either --input or --input-file, not both.")
    if args.input_file:
        return Path(args.input_file).expanduser().read_text(encoding="utf-8").strip()
    if args.input:
        return args.input.strip()
    raise ConfigError("A research prompt is required. Use --input or --input-file.")


def resolve_auth(
    args: argparse.Namespace,
    env_map: Dict[str, str],
    ssl_context: ssl.SSLContext,
) -> Dict[str, str]:
    config_json = first_non_empty(
        args.config_json,
        env_map.get("GEMINI_DEEP_RESEARCH_CONFIG_JSON"),
        env_map.get("GOOGLE_AI_STUDIO_OAUTH_JSON"),
        env_map.get("GCLI2API_CONFIG_JSON"),
    )
    api_key = first_non_empty(
        args.api_key,
        env_map.get("GEMINI_API_KEY"),
        env_map.get("GOOGLE_API_KEY"),
    )
    if config_json:
        token = load_oauth_access_token(
            Path(config_json).expanduser().resolve(),
            ssl_context,
        )
        return {
            "mode": "oauth",
            "token": token,
            "config_json": str(Path(config_json).expanduser().resolve()),
        }
    if api_key:
        return {"mode": "api_key", "token": api_key}
    raise ConfigError(
        "Missing Gemini auth. Set GEMINI_DEEP_RESEARCH_CONFIG_JSON or GEMINI_API_KEY "
        "via CLI, .env, or environment variables."
    )


def load_oauth_access_token(config_path: Path, ssl_context: ssl.SSLContext) -> str:
    if not config_path.exists():
        raise ConfigError(f"OAuth config JSON not found: {config_path}")
    data = json.loads(config_path.read_text(encoding="utf-8"))
    access_token = str(data.get("access_token") or "").strip()
    expiry = parse_iso_datetime(data.get("expiry"))
    now = dt.datetime.now(dt.timezone.utc)
    # Refresh when the token is missing or about to expire.
    if access_token and expiry and expiry - now > dt.timedelta(minutes=2):
        return access_token
    refresh_token = str(data.get("refresh_token") or "").strip()
    client_id = str(data.get("client_id") or "").strip()
    client_secret = str(data.get("client_secret") or "").strip()
    if not refresh_token or not client_id or not client_secret:
        raise ConfigError(
            "OAuth config JSON is missing refresh_token, client_id, or client_secret."
        )
    return refresh_access_token(refresh_token, client_id, client_secret, ssl_context)


def refresh_access_token(
    refresh_token: str,
    client_id: str,
    client_secret: str,
    ssl_context: ssl.SSLContext,
) -> str:
    payload = urllib.parse.urlencode(
        {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        TOKEN_ENDPOINT,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    response = http_json(request, ssl_context)
    token = str(response.get("access_token") or "").strip()
    if not token:
        raise ConfigError("OAuth refresh succeeded but no access_token was returned.")
    return token


def request_headers(auth: Dict[str, str], api_revision: str) -> Dict[str, str]:
    headers = {
        "Content-Type": "application/json",
        "Api-Revision": api_revision,
    }
    if auth["mode"] == "api_key":
        headers["x-goog-api-key"] = auth["token"]
    else:
        headers["Authorization"] = f"Bearer {auth['token']}"
    return headers


def build_ssl_context(ca_bundle: Optional[str]) -> ssl.SSLContext:
    if ca_bundle:
        return ssl.create_default_context(cafile=ca_bundle)
    try:
        import certifi  # type: ignore

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


def http_json(request: urllib.request.Request, ssl_context: ssl.SSLContext) -> Any:
    try:
        with urllib.request.urlopen(request, timeout=120, context=ssl_context) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        if "ACCESS_TOKEN_SCOPE_INSUFFICIENT" in body:
            raise HttpError(
                "OAuth token lacks the required Gemini API scopes for Deep Research. "
                "Use GEMINI_API_KEY or regenerate the OAuth JSON with access to "
                "generativelanguage.googleapis.com."
            ) from exc
        raise HttpError(f"HTTP {exc.code} {exc.reason}: {body}") from exc
    except urllib.error.URLError as exc:
        raise HttpError(f"Network error: {exc}") from exc
    if not raw.strip():
        return {}
    return json.loads(raw)


def create_interaction(
    prompt: str,
    auth: Dict[str, str],
    api_base: str,
    agent: str,
    api_revision: str,
    tools: List[str],
    ssl_context: ssl.SSLContext,
) -> Dict[str, Any]:
    body: Dict[str, Any] = {
        "input": prompt,
        "agent": agent,
        "background": True,
        "store": True,
        "agent_config": {
            "type": "deep-research",
            "thinking_summaries": "none",
            "visualization": "off",
            "collaborative_planning": False,
        },
    }
    if tools:
        body["tools"] = [{"type": tool} for tool in tools]
    request = urllib.request.Request(
        f"{api_base}/interactions",
        data=json.dumps(body).encode("utf-8"),
        headers=request_headers(auth, api_revision),
        method="POST",
    )
    return http_json(request, ssl_context)


def get_interaction(
    interaction_id: str,
    auth: Dict[str, str],
    api_base: str,
    api_revision: str,
    ssl_context: ssl.SSLContext,
) -> Dict[str, Any]:
    request = urllib.request.Request(
        f"{api_base}/interactions/{interaction_id}",
        headers=request_headers(auth, api_revision),
        method="GET",
    )
    return http_json(request, ssl_context)


def normalize_interaction_id(interaction_id: str) -> str:
    return interaction_id.strip().split("/")[-1]


def wait_for_completion(
    interaction_id: str,
    auth: Dict[str, str],
    api_base: str,
    api_revision: str,
    poll_interval: int,
    timeout: int,
    ssl_context: ssl.SSLContext,
) -> Dict[str, Any]:
    deadline = time.time() + timeout
    while True:
        interaction = get_interaction(
            interaction_id,
            auth,
            api_base,
            api_revision,
            ssl_context,
        )
        status = str(interaction.get("status") or "").lower()
        if status in {"completed", "failed", "cancelled", "canceled"}:
            return interaction
        if time.time() >= deadline:
            raise TimeoutError(
                f"Timed out after {timeout}s waiting for interaction {interaction_id}."
            )
        time.sleep(poll_interval)


def extract_final_text(interaction: Dict[str, Any]) -> str:
    steps = interaction.get("steps") or []
    texts: List[str] = []
    for step in steps:
        content = step.get("content")
        if isinstance(content, list):
            for part in content:
                if isinstance(part, dict):
                    text = part.get("text")
                    if isinstance(text, str) and text.strip():
                        texts.append(text.strip())
    if texts:
        return "\n\n".join(texts).strip()
    # Fall back to a broad recursive search for text blocks.
    recursive_texts: List[str] = []
    collect_texts(interaction, recursive_texts)
    deduped: List[str] = []
    seen = set()
    for item in recursive_texts:
        if item not in seen:
            deduped.append(item)
            seen.add(item)
    return "\n\n".join(deduped).strip()


def collect_texts(node: Any, sink: List[str]) -> None:
    if isinstance(node, dict):
        text = node.get("text")
        if isinstance(text, str) and text.strip():
            sink.append(text.strip())
        for value in node.values():
            collect_texts(value, sink)
    elif isinstance(node, list):
        for item in node:
            collect_texts(item, sink)


def extract_citations(interaction: Dict[str, Any]) -> List[Dict[str, Any]]:
    citations: List[Dict[str, Any]] = []
    walk_for_citations(interaction, citations)
    deduped: List[Dict[str, Any]] = []
    seen = set()
    for citation in citations:
        fingerprint = json.dumps(citation, ensure_ascii=False, sort_keys=True)
        if fingerprint not in seen:
            deduped.append(citation)
            seen.add(fingerprint)
    return deduped


def walk_for_citations(node: Any, sink: List[Dict[str, Any]]) -> None:
    if isinstance(node, dict):
        if "citations" in node and isinstance(node["citations"], list):
            for citation in node["citations"]:
                if isinstance(citation, dict):
                    sink.append(citation)
        maybe_source = build_source_candidate(node)
        if maybe_source:
            sink.append(maybe_source)
        for value in node.values():
            walk_for_citations(value, sink)
    elif isinstance(node, list):
        for item in node:
            walk_for_citations(item, sink)


def build_source_candidate(node: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    url = first_non_empty(node.get("url"), node.get("uri"))
    title = first_non_empty(node.get("title"), node.get("name"))
    if not url and not title:
        return None
    candidate: Dict[str, Any] = {}
    if title:
        candidate["title"] = title
    if url:
        candidate["url"] = url
    for field in ("publisher", "snippet", "startIndex", "endIndex"):
        value = node.get(field)
        if value not in (None, "", []):
            candidate[field] = value
    return candidate


def ensure_output_dir(path_value: Optional[str]) -> Path:
    target = Path(path_value or DEFAULT_OUTPUT_DIR).expanduser().resolve()
    target.mkdir(parents=True, exist_ok=True)
    return target


def write_artifacts(
    output_dir: Path,
    prompt: Optional[str],
    interaction: Dict[str, Any],
    auth_mode: str,
    env_path: Optional[Path],
) -> None:
    status = str(interaction.get("status") or "")
    interaction_id = str(interaction.get("id") or "unknown")
    (output_dir / "interaction.json").write_text(
        json_dumps(interaction),
        encoding="utf-8",
    )
    citations = extract_citations(interaction)
    (output_dir / "sources.json").write_text(
        json_dumps(citations),
        encoding="utf-8",
    )
    report_text = extract_final_text(interaction)
    report_lines = [
        "# Gemini Deep Research Report",
        "",
        f"- interaction_id: {interaction_id}",
        f"- status: {status}",
        f"- auth_mode: {auth_mode}",
    ]
    if env_path:
        report_lines.append(f"- env_file: {env_path}")
    if prompt:
        report_lines.extend(["", "## Prompt", "", prompt])
    report_lines.extend(["", "## Final Report", "", report_text or "(No final text found in response.)"])
    report_lines.extend(["", "## Extracted Sources", ""])
    if citations:
        for idx, citation in enumerate(citations, start=1):
            title = citation.get("title") or "(untitled)"
            url = citation.get("url") or citation.get("uri") or "(no url)"
            report_lines.append(f"{idx}. {title}")
            report_lines.append(f"   {url}")
    else:
        report_lines.append("No citations were extracted from the returned payload.")
    (output_dir / "report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")


def print_status(interaction: Dict[str, Any], output_dir: Path) -> None:
    interaction_id = interaction.get("id") or "(unknown)"
    status = interaction.get("status") or "(unknown)"
    print(f"interaction_id={interaction_id}")
    print(f"status={status}")
    print(f"artifacts={output_dir}")


def main() -> int:
    args = parse_args()
    try:
        env_map, env_path = merged_env(args)
        ca_bundle = first_non_empty(
            env_map.get("GEMINI_DEEP_RESEARCH_CA_BUNDLE"),
            env_map.get("SSL_CERT_FILE"),
        )
        ssl_context = build_ssl_context(ca_bundle)
        auth = resolve_auth(args, env_map, ssl_context)
        agent = first_non_empty(
            args.agent,
            env_map.get("GEMINI_DEEP_RESEARCH_AGENT"),
            DEFAULT_AGENT,
        ) or DEFAULT_AGENT
        api_revision = first_non_empty(
            args.api_revision,
            env_map.get("GEMINI_DEEP_RESEARCH_API_REVISION"),
            DEFAULT_API_REVISION,
        ) or DEFAULT_API_REVISION
        poll_interval = parse_int(
            first_non_empty(str(args.poll_interval) if args.poll_interval is not None else None,
                            env_map.get("GEMINI_DEEP_RESEARCH_POLL_INTERVAL")),
            DEFAULT_POLL_INTERVAL,
        )
        timeout = parse_int(
            first_non_empty(str(args.timeout) if args.timeout is not None else None,
                            env_map.get("GEMINI_DEEP_RESEARCH_TIMEOUT")),
            DEFAULT_TIMEOUT,
        )
        output_dir = ensure_output_dir(
            first_non_empty(args.output_dir, env_map.get("GEMINI_DEEP_RESEARCH_OUTPUT_DIR"))
        )
        tools = args.tool[:] if args.tool else ["google_search"]

        if args.interaction_id:
            prompt = None
            interaction_id = normalize_interaction_id(args.interaction_id)
            interaction = get_interaction(
                interaction_id,
                auth,
                DEFAULT_API_BASE,
                api_revision,
                ssl_context,
            )
            status = str(interaction.get("status") or "").lower()
            if status not in {"completed", "failed", "cancelled", "canceled"}:
                interaction = wait_for_completion(
                    interaction_id,
                    auth,
                    DEFAULT_API_BASE,
                    api_revision,
                    poll_interval,
                    timeout,
                    ssl_context,
                )
        else:
            prompt = read_prompt(args)
            interaction = create_interaction(
                prompt,
                auth,
                DEFAULT_API_BASE,
                agent,
                api_revision,
                tools,
                ssl_context,
            )
            if args.no_wait:
                write_artifacts(output_dir, prompt, interaction, auth["mode"], env_path)
                print_status(interaction, output_dir)
                return 0
            interaction_id = normalize_interaction_id(str(interaction.get("id") or ""))
            if not interaction_id:
                raise HttpError(f"Interaction creation returned no id: {json_dumps(interaction)}")
            interaction = wait_for_completion(
                interaction_id,
                auth,
                DEFAULT_API_BASE,
                api_revision,
                poll_interval,
                timeout,
                ssl_context,
            )

        write_artifacts(output_dir, prompt, interaction, auth["mode"], env_path)
        print_status(interaction, output_dir)
        if str(interaction.get("status") or "").lower() == "failed":
            error_payload = interaction.get("error")
            print(f"error={json.dumps(error_payload, ensure_ascii=False)}", file=sys.stderr)
            return 1
        return 0
    except (ConfigError, HttpError, TimeoutError, OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
