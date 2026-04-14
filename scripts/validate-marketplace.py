#!/usr/bin/env python3
"""Validate marketplace.json integrity, plugin naming, and orphan detection.

Checks:
- Marketplace JSON validity (valid JSON, required fields, paths exist)
- Plugin naming convention
- Orphan detection (skills/agents not registered)

Requires Python 3.9+ stdlib only.
Run from the repository root: python3 scripts/validate-marketplace.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from validate_common import (
    AGENTS_DIR,
    MARKETPLACE_PATH,
    REPO_ROOT,
    SKILLS_DIR,
    error,
    ok,
    parse_frontmatter,
    print_summary,
    rel,
    warn,
)

PLUGIN_NAME_RE = re.compile(
    r"^([\w-]+-virtuoso|role-[\w-]+|agent-[\w-]+|tool-[\w-]+|code-virtuoso)$"
)


# ---------------------------------------------------------------------------
# 1. Marketplace JSON validity
# ---------------------------------------------------------------------------

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
# 9. Orphan detection
# ---------------------------------------------------------------------------

def check_orphans(data: dict) -> None:
    print("\n=== Orphan Detection ===")

    # Collect all skill and agent paths referenced in any plugin
    referenced_skill_dirs: set[Path] = set()
    referenced_agent_paths: set[Path] = set()
    uses_auto_discovery = False

    for plugin in data.get("plugins", []):
        skills_list = plugin.get("skills", [])
        agents_list = plugin.get("agents", [])

        # If a plugin has source but no explicit skills/agents, it uses auto-discovery
        if plugin.get("source") and not skills_list and not agents_list:
            uses_auto_discovery = True

        for spath in skills_list:
            resolved = (REPO_ROOT / spath.lstrip("./")).resolve()
            referenced_skill_dirs.add(resolved)

        for apath in agents_list:
            resolved = (REPO_ROOT / apath.lstrip("./")).resolve()
            referenced_agent_paths.add(resolved)

    if uses_auto_discovery:
        skill_files = sorted(SKILLS_DIR.rglob("SKILL.md"))
        agent_files = sorted(AGENTS_DIR.glob("*.md")) if AGENTS_DIR.is_dir() else []
        ok(f"Auto-discovery mode: found {len(skill_files)} skill(s) and {len(agent_files)} agent(s)")
        return

    skill_files = sorted(SKILLS_DIR.rglob("SKILL.md"))
    agent_files = sorted(AGENTS_DIR.glob("*.md")) if AGENTS_DIR.is_dir() else []

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
            error(f"{rel(path)}: agent not referenced in any plugin in marketplace.json")
        else:
            ok(f"{rel(path)}: registered in agents-virtuoso")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    data = load_marketplace()
    if data is not None:
        check_marketplace(data)
        check_plugin_naming(data)
        check_orphans(data)

    return print_summary()


if __name__ == "__main__":
    sys.exit(main())
