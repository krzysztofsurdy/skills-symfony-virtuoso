#!/usr/bin/env python3
"""Validation script for the Code Virtuoso skill/agent repository.

Checks marketplace.json integrity, skill and agent frontmatter conventions,
naming consistency, plugin naming, markdown hygiene, internal links, size
limits, and orphan detection.

Requires Python 3.9+ stdlib only -- no third-party dependencies.
Run from the repository root: python3 scripts/validate.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MARKETPLACE_PATH = REPO_ROOT / ".claude-plugin" / "marketplace.json"
SKILLS_DIR = REPO_ROOT / "skills"
AGENTS_DIR = REPO_ROOT / "agents"

PLUGIN_NAME_RE = re.compile(
    r"^([\w-]+-virtuoso|role-[\w-]+|agent-[\w-]+|tool-[\w-]+)$"
)

errors: list[str] = []
warnings: list[str] = []


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def ok(msg: str) -> None:
    print(f"  OK    {msg}")


def error(msg: str) -> None:
    print(f"  ERROR {msg}")
    errors.append(msg)


def warn(msg: str) -> None:
    print(f"  WARN  {msg}")
    warnings.append(msg)


def parse_frontmatter(path: Path) -> dict[str, object] | None:
    """Parse simple YAML frontmatter between --- markers.

    Handles scalar key-value pairs and simple list fields (like skills:).
    Returns None if no valid frontmatter found.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as exc:
        error(f"{rel(path)}: cannot read file ({exc})")
        return None

    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return None

    raw = match.group(1)
    result: dict[str, object] = {}
    current_list_key: str | None = None

    for line in raw.splitlines():
        # Continuation of a list field
        if current_list_key is not None:
            list_match = re.match(r"^\s+-\s+(.+)$", line)
            if list_match:
                result[current_list_key].append(list_match.group(1).strip())  # type: ignore[union-attr]
                continue
            else:
                current_list_key = None

        # Key-value pair
        kv = re.match(r"^([A-Za-z_-]+)\s*:\s*(.*)$", line)
        if not kv:
            continue

        key = kv.group(1)
        value = kv.group(2).strip()

        # Boolean
        if value.lower() == "true":
            result[key] = True
        elif value.lower() == "false":
            result[key] = False
        # Empty value followed by list items
        elif value == "":
            result[key] = []
            current_list_key = key
        else:
            result[key] = value

    return result


def rel(path: Path) -> str:
    """Return path relative to REPO_ROOT for display."""
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def load_marketplace() -> dict | None:
    """Load and return marketplace.json, or None on failure."""
    print("\n=== Marketplace JSON Validity ===")
    if not MARKETPLACE_PATH.exists():
        error("marketplace.json does not exist")
        return None
    try:
        data = json.loads(MARKETPLACE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        error(f"marketplace.json is not valid JSON: {exc}")
        return None
    ok("marketplace.json is valid JSON")
    return data


# ---------------------------------------------------------------------------
# 1. Marketplace JSON validity
# ---------------------------------------------------------------------------

def check_marketplace(data: dict) -> None:
    # Top-level fields
    for field in ("name", "metadata", "plugins"):
        if field not in data:
            error(f"marketplace.json: missing required top-level field '{field}'")
        else:
            ok(f"marketplace.json has '{field}'")

    metadata = data.get("metadata", {})
    if "version" not in metadata:
        error("marketplace.json: metadata missing 'version'")
    else:
        ok("marketplace.json metadata has 'version'")

    plugins = data.get("plugins", [])
    skill_count = 0
    agent_count = 0

    for plugin in plugins:
        pname = plugin.get("name", "<unnamed>")

        for spath in plugin.get("skills", []):
            resolved = REPO_ROOT / spath.lstrip("./")
            skill_md = resolved / "SKILL.md"
            if not skill_md.is_file():
                error(f"{spath}/SKILL.md does not exist (referenced by {pname})")
            else:
                skill_count += 1

        for apath in plugin.get("agents", []):
            resolved = REPO_ROOT / apath.lstrip("./")
            if not resolved.is_file():
                error(f"{apath} does not exist (referenced by {pname})")
            else:
                agent_count += 1

    ok(f"Checked {skill_count} skill path(s) and {agent_count} agent path(s)")


# ---------------------------------------------------------------------------
# 2. Skill frontmatter validation
# ---------------------------------------------------------------------------

def check_skill_frontmatter() -> list[Path]:
    print("\n=== Skill Frontmatter ===")
    skill_files = sorted(SKILLS_DIR.rglob("SKILL.md"))

    if not skill_files:
        warn("No SKILL.md files found in skills/")
        return []

    for path in skill_files:
        fm = parse_frontmatter(path)
        rp = rel(path)

        if fm is None:
            error(f"{rp}: missing or invalid YAML frontmatter")
            continue

        # Required fields
        for field in ("name", "description", "user-invocable"):
            if field not in fm:
                error(f"{rp}: missing required field '{field}'")

        # name must be non-empty string
        name = fm.get("name")
        if isinstance(name, str) and not name.strip():
            error(f"{rp}: 'name' must be a non-empty string")

        # description must be non-empty string, at least 50 chars
        desc = fm.get("description")
        if isinstance(desc, str):
            if not desc.strip():
                error(f"{rp}: 'description' must be a non-empty string")
            elif len(desc) < 50:
                error(f"{rp}: 'description' is {len(desc)} chars, minimum is 50")
        elif desc is not None:
            error(f"{rp}: 'description' must be a string")

        # user-invocable must be boolean
        ui = fm.get("user-invocable")
        if ui is not None and not isinstance(ui, bool):
            error(f"{rp}: 'user-invocable' must be boolean (true or false)")

        # Must NOT have model field
        if "model" in fm:
            error(f"{rp}: must not have a 'model' field (no provider-specific models)")

        if all(f in fm for f in ("name", "description", "user-invocable")):
            if isinstance(fm.get("user-invocable"), bool):
                ok(rp)

    return skill_files


# ---------------------------------------------------------------------------
# 3. Agent frontmatter validation
# ---------------------------------------------------------------------------

def check_agent_frontmatter() -> list[Path]:
    print("\n=== Agent Frontmatter ===")

    if not AGENTS_DIR.is_dir():
        warn("No agents/ directory found")
        return []

    agent_files = sorted(AGENTS_DIR.glob("*.md"))

    if not agent_files:
        warn("No agent .md files found in agents/")
        return []

    for path in agent_files:
        fm = parse_frontmatter(path)
        rp = rel(path)

        if fm is None:
            error(f"{rp}: missing or invalid YAML frontmatter")
            continue

        # Required fields
        for field in ("name", "description", "tools"):
            if field not in fm:
                error(f"{rp}: missing required field '{field}'")

        # Must NOT have model field
        if "model" in fm:
            error(f"{rp}: must not have a 'model' field (no provider-specific models)")

        # name must be non-empty string
        name = fm.get("name")
        if isinstance(name, str) and not name.strip():
            error(f"{rp}: 'name' must be a non-empty string")

        # description must be non-empty string
        desc = fm.get("description")
        if isinstance(desc, str) and not desc.strip():
            error(f"{rp}: 'description' must be a non-empty string")

        if all(f in fm for f in ("name", "description", "tools")) and "model" not in fm:
            ok(rp)

    return agent_files


# ---------------------------------------------------------------------------
# 4. Name consistency
# ---------------------------------------------------------------------------

def check_name_consistency(skill_files: list[Path], agent_files: list[Path]) -> None:
    print("\n=== Name Consistency ===")

    for path in skill_files:
        fm = parse_frontmatter(path)
        if fm is None or "name" not in fm:
            continue
        expected = path.parent.name
        actual = fm["name"]
        if actual != expected:
            error(f"{rel(path)}: name '{actual}' does not match directory name '{expected}'")
        else:
            ok(f"{rel(path)}: name matches directory")

    for path in agent_files:
        fm = parse_frontmatter(path)
        if fm is None or "name" not in fm:
            continue
        expected = path.stem
        actual = fm["name"]
        if actual != expected:
            error(f"{rel(path)}: name '{actual}' does not match filename '{expected}'")
        else:
            ok(f"{rel(path)}: name matches filename")


# ---------------------------------------------------------------------------
# 5. Plugin naming convention
# ---------------------------------------------------------------------------

def check_plugin_naming(data: dict) -> None:
    print("\n=== Plugin Naming Convention ===")

    for plugin in data.get("plugins", []):
        pname = plugin.get("name", "")
        if PLUGIN_NAME_RE.match(pname):
            ok(f"plugin '{pname}' matches naming convention")
        else:
            error(
                f"plugin '{pname}' does not match naming convention "
                "(expected: {{word}}-virtuoso, role-{{word}}, agent-{{word}}, or tool-{{word}})"
            )


# ---------------------------------------------------------------------------
# 6. Markdown lint (basic)
# ---------------------------------------------------------------------------

def check_markdown_lint(skill_files: list[Path], agent_files: list[Path]) -> None:
    print("\n=== Markdown Lint ===")

    all_files = list(skill_files) + list(agent_files)

    for path in all_files:
        rp = rel(path)
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue

        # Must start with frontmatter
        if not text.startswith("---"):
            error(f"{rp}: file must start with frontmatter (---)")

        # No consecutive blank lines (more than 2 newlines in a row)
        if "\n\n\n" in text:
            error(f"{rp}: consecutive blank lines detected (more than 2 newlines in a row)")

        # Must end with a single newline
        if text and not text.endswith("\n"):
            error(f"{rp}: file must end with a newline")
        elif text.endswith("\n\n"):
            error(f"{rp}: file must end with a single newline, not multiple")

        if (
            text.startswith("---")
            and "\n\n\n" not in text
            and text.endswith("\n")
            and not text.endswith("\n\n")
        ):
            ok(f"{rp}: markdown lint OK")


# ---------------------------------------------------------------------------
# 7. Internal link checking
# ---------------------------------------------------------------------------

def check_internal_links(skill_files: list[Path]) -> None:
    print("\n=== Internal Link Checking ===")

    # Check reference links in SKILL.md files
    link_re = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")

    for path in skill_files:
        rp = rel(path)
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue

        links_checked = 0
        for match in link_re.finditer(text):
            target = match.group(2)
            # Skip external links, anchors, and platform-specific references
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                error(f"{rp}: broken link '{target}' (file not found)")
            else:
                links_checked += 1

        if links_checked > 0:
            ok(f"{rp}: {links_checked} internal link(s) verified")

    # Check README.md internal links
    readme = REPO_ROOT / "README.md"
    if readme.is_file():
        try:
            text = readme.read_text(encoding="utf-8")
        except Exception:
            text = ""

        links_checked = 0
        for match in link_re.finditer(text):
            target = match.group(2)
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            resolved = (readme.parent / target).resolve()
            if not resolved.exists():
                error(f"README.md: broken link '{target}' (file not found)")
            else:
                links_checked += 1

        if links_checked > 0:
            ok(f"README.md: {links_checked} internal link(s) verified")


# ---------------------------------------------------------------------------
# 8. SKILL.md size check
# ---------------------------------------------------------------------------

def check_skill_size(skill_files: list[Path]) -> None:
    print("\n=== SKILL.md Size Check ===")

    for path in skill_files:
        rp = rel(path)
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except Exception:
            continue

        count = len(lines)
        if count > 1000:
            error(f"{rp}: {count} lines exceeds 1000 line limit")
        elif count > 500:
            warn(f"{rp}: {count} lines exceeds 500 line recommendation")
        else:
            ok(f"{rp}: {count} lines")


# ---------------------------------------------------------------------------
# 9. Orphan detection
# ---------------------------------------------------------------------------

def check_orphans(data: dict, skill_files: list[Path], agent_files: list[Path]) -> None:
    print("\n=== Orphan Detection ===")

    # Collect all skill paths referenced in any plugin
    referenced_skill_dirs: set[Path] = set()
    for plugin in data.get("plugins", []):
        for spath in plugin.get("skills", []):
            resolved = (REPO_ROOT / spath.lstrip("./")).resolve()
            referenced_skill_dirs.add(resolved)

    # Collect all agent paths referenced in the agents-virtuoso plugin
    referenced_agent_paths: set[Path] = set()
    for plugin in data.get("plugins", []):
        if plugin.get("name") == "agents-virtuoso":
            for apath in plugin.get("agents", []):
                resolved = (REPO_ROOT / apath.lstrip("./")).resolve()
                referenced_agent_paths.add(resolved)

    # Check skill orphans
    for path in skill_files:
        skill_dir = path.parent.resolve()
        if skill_dir not in referenced_skill_dirs:
            error(f"{rel(path)}: skill directory not referenced in any plugin in marketplace.json")
        else:
            ok(f"{rel(path)}: registered in marketplace.json")

    # Check agent orphans
    for path in agent_files:
        resolved = path.resolve()
        if resolved not in referenced_agent_paths:
            error(f"{rel(path)}: agent not referenced in agents-virtuoso plugin")
        else:
            ok(f"{rel(path)}: registered in agents-virtuoso")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    data = load_marketplace()
    if data is not None:
        check_marketplace(data)

    skill_files = check_skill_frontmatter()
    agent_files = check_agent_frontmatter()
    check_name_consistency(skill_files, agent_files)

    if data is not None:
        check_plugin_naming(data)

    check_markdown_lint(skill_files, agent_files)
    check_internal_links(skill_files)
    check_skill_size(skill_files)

    if data is not None:
        check_orphans(data, skill_files, agent_files)

    # Summary
    print(f"\n=== Summary ===")
    print(f"{len(errors)} error(s), {len(warnings)} warning(s)")

    if errors:
        print("\nErrors:")
        for e in errors:
            print(f"  - {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
