#!/usr/bin/env python3
"""Validate agent frontmatter and name consistency.

Checks:
- Agent frontmatter validation (required fields, no model)
- Agent name consistency (name matches filename)

Requires Python 3.9+ stdlib only.
Run from the repository root: python3 scripts/validate-agents.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from validate_common import (
    AGENTS_DIR,
    error,
    ok,
    parse_frontmatter,
    print_summary,
    rel,
    warn,
)


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
# 4. Agent name consistency
# ---------------------------------------------------------------------------

def check_agent_name_consistency(agent_files: list[Path]) -> None:
    print("\n=== Name Consistency ===")

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
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    agent_files = check_agent_frontmatter()
    check_agent_name_consistency(agent_files)

    return print_summary()


if __name__ == "__main__":
    sys.exit(main())
