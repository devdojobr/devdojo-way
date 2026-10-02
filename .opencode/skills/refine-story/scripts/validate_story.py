#!/usr/bin/env python3
"""Read-only mechanical preflight; not the pipeline's contract validator.

Requires preinstalled Python 3 / PyYAML. Run from the repository root with -B.
One input under docs/stories/refined/; no command execution or filesystem writes.
"""

import fnmatch
import json
from pathlib import Path
import re
import sys

try:
    import yaml
except ImportError:
    yaml = None


HEADINGS = [
    "Context", "Problem statement", "Glossary", "Functional requirements",
    "Business rules", "Decisions", "Data specification", "Contracts",
    "State & side effects", "Error handling", "Non-functional requirements",
    "Security", "Observability", "Configuration", "Out of scope",
    "Implementation guidance", "Codebase map", "Prohibited", "Compatibility",
    "Coverage matrix", "Fixtures & test data", "Environment",
    "Escalation triggers", "Definition of done", "Refinement log",
]
ITEM_ID = re.compile(r"[A-Z][A-Z0-9]*-\d+\Z")
STORY_ID = re.compile(r"[A-Z][A-Z0-9]*-\d+(?:\.\d+)*\Z")
KINDS = {
    "functional", "business_rule", "error", "nfr", "security",
    "observability", "configuration", "constraint",
}
OBLIGATIONS = {"MUST", "MUST_NOT", "SHOULD", "SHOULD_NOT", "MAY"}
LEVELS = {"unit", "component", "integration", "contract", "e2e"}
PREFIX_KINDS = {
    "FR": "functional", "BR": "business_rule", "E": "error", "NFR": "nfr",
    "SEC": "security", "OBS": "observability", "CFG": "configuration",
    "IG": "constraint",
}
MIRROR_SECTIONS = {"criteria": None, "coverage": "20", "checks": "24"}
ITEM_SECTIONS = {
    "GL": "03", "FR": "04", "BR": "05", "D": "06", "CT": "08",
    "E": "10", "NFR": "11", "SEC": "12", "OBS": "13", "CFG": "14",
    "OOS": "15", "IG": "16", "IGS": "16", "PR": "18", "CM": "20",
    "FX": "21", "ET": "23", "DOD": "24",
}


if yaml is not None:
    class StrictLoader(yaml.SafeLoader):
        def compose_node(self, parent, index):
            if self.check_event(yaml.AliasEvent):
                raise ValueError("YAML aliases are unsupported; use explicit values")
            return super().compose_node(parent, index)

        def construct_mapping(self, node, deep=False):
            result = {}
            for key_node, value_node in node.value:
                key = self.construct_object(key_node, deep=deep)
                if not isinstance(key, str):
                    raise ValueError("YAML mapping keys must be strings")
                if key in result:
                    raise ValueError(f"Duplicate YAML key: {key}")
                result[key] = self.construct_object(value_node, deep=deep)
            return result


def clean(value):
    return value.strip().strip("`").strip()


def substantive(text):
    """Headings, ID-only rows, and empty template tables do not count."""
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith(("#", "<!--")) or line == "---":
            continue
        if line.startswith("|"):
            cells = [clean(cell) for cell in line.strip("|").split("|")]
            if all(re.fullmatch(r":?-+:?", cell or " ") for cell in cells):
                continue
            if cells[0] in {"ID", "#", "Path"}:
                continue
            if any(cell for cell in cells[1:]):
                return True
        elif re.fullmatch(r"N/A\s*[—–-]\s*\S.*", line):
            return True
        elif line != "N/A" and not re.fullmatch(r"[-*]\s*[A-Z][A-Z0-9]*-\d+:?", line):
            return True
    return False


def parse_artifact(text):
    marker = "<!-- refined-story-candidate -->"
    if marker in text:
        if text.count(marker) != 1 or not text.startswith("# Blocking\n"):
            raise ValueError("Draft must have one candidate marker and top Blocking list")
        text = text.split(marker, 1)[1].lstrip("\r\n")
    if not text.startswith("---\n"):
        raise ValueError("Candidate must start with YAML frontmatter")
    match = re.search(r"^---\s*$", text[4:], re.MULTILINE)
    if match is None:
        raise ValueError("Missing closing frontmatter delimiter")
    offset = 4 + match.start()
    header = yaml.load(text[4:offset], Loader=StrictLoader)
    if not isinstance(header, dict):
        raise ValueError("Header must be a mapping")
    body = text[4 + match.end():].lstrip("\r\n")
    sections = {}
    ordered = []
    headings = list(re.finditer(r"^## (\d{2}) (.+?)\s*$", body, re.MULTILINE))
    for index, heading in enumerate(headings):
        number, title = heading.groups()
        ordered.append((number, title))
        end = headings[index + 1].start() if index + 1 < len(headings) else len(body)
        sections.setdefault(number, []).append(body[heading.end():end])
    definitions = {}
    for number, chunks in sections.items():
        for chunk in chunks:
            in_fence = False
            for line in chunk.splitlines():
                if line.strip().startswith(("```", "~~~")):
                    in_fence = not in_fence
                if in_fence:
                    continue
                item = None
                if line.lstrip().startswith("|"):
                    item = clean(line.strip().strip("|").split("|", 1)[0])
                else:
                    match = re.match(r"\s*[-*]\s+`?([A-Z][A-Z0-9]*-\d+)`?(?=[:\s]|$)", line)
                    if match:
                        item = match.group(1)
                if item and ITEM_ID.fullmatch(item):
                    definitions.setdefault(item, []).append((number, line.strip()))
    return header, body, sections, ordered, definitions


def path_problem(path):
    if not isinstance(path, str) or not path.strip():
        return "must be a non-empty path string"
    if path.startswith(("/", "~")) or "\\" in path:
        return "must be repository-relative with forward slashes"
    if any(part in {"", ".", ".."} for part in path.split("/")):
        return "must not contain empty, dot, or parent components"
    if any(char in path for char in "{}"):
        return "brace expansion is unsupported; supply concrete approved paths"
    return None


def might_overlap(left, right):
    """Conservative whole-path glob intersection, never an uncertainty waiver.

    fnmatch '*' includes '/', so matching is conservative for segment globs.
    Two glob patterns are disjoint only if their literal prefixes are disjoint.
    """
    wildcard = lambda path: any(char in path for char in "*?[")
    if not wildcard(left):
        return fnmatch.fnmatchcase(left, right)
    if not wildcard(right):
        return fnmatch.fnmatchcase(right, left)
    prefix = lambda path: re.split(r"[*?\[]", path, maxsplit=1)[0]
    a, b = prefix(left), prefix(right)
    return a.startswith(b) or b.startswith(a)


def _validate(text):
    results = []

    def result(rule, failures):
        results.append({"rule": rule, "status": "FAIL" if failures else "PASS", "detail": failures})

    try:
        header, body, sections, ordered, definitions = parse_artifact(text)
    except (ValueError, yaml.YAMLError) as exc:
        result("parse", [str(exc)])
        return {"mechanical_pass": False, "results": results}

    shape = []

    def mapping(value, required, optional, label):
        if not isinstance(value, dict):
            shape.append(f"{label}: expected mapping")
            return {}
        missing = set(required) - value.keys()
        unknown = value.keys() - set(required) - set(optional)
        if missing:
            shape.append(f"{label}: missing {sorted(missing)}")
        if unknown:
            shape.append(f"{label}: unknown fields {sorted(unknown)}")
        return value

    def string(value, label, empty=False):
        if not isinstance(value, str) or (not empty and not value.strip()):
            shape.append(f"{label}: expected {'possibly empty' if empty else 'non-empty'} string")

    def strings(value, label):
        if not isinstance(value, list):
            shape.append(f"{label}: expected string list")
            return []
        for entry in value:
            string(entry, label)
        return [entry for entry in value if isinstance(entry, str)]

    def rows(value, label):
        if not isinstance(value, list):
            shape.append(f"{label}: expected list")
            return []
        return value

    mapping(header, ["template_version", "story", "criteria", "scope", "coverage", "checks", "environment"], [], "header")
    if str(header.get("template_version")) != "2.0":
        shape.append("template_version: expected 2.0")
    story = mapping(header.get("story"), ["id", "version", "type", "title", "repository", "target_branch", "refined_against_sha", "depends_on"], ["risk"], "story")
    for field in ["id", "title", "repository", "target_branch", "refined_against_sha"]:
        string(story.get(field), f"story.{field}")
    if not STORY_ID.fullmatch(str(story.get("id", ""))):
        shape.append("story.id: invalid stable/split ID")
    if type(story.get("version")) is not int or story["version"] < 1:
        shape.append("story.version: expected positive integer")
    if story.get("type") not in {"foundation", "change"}:
        shape.append("story.type: expected foundation or change")
    if story.get("target_branch") != "main":
        shape.append("story.target_branch: this repository requires main")
    if not re.fullmatch(r"[0-9a-fA-F]{40}", str(story.get("refined_against_sha", ""))):
        shape.append("story.refined_against_sha: expected 40 hexadecimal characters")
    if story.get("risk") not in {None, "low", "medium", "high"}:
        shape.append("story.risk: invalid risk declaration")
    dependencies = []
    for index, raw in enumerate(rows(story.get("depends_on"), "story.depends_on")):
        dep = mapping(raw, ["story_id", "min_version"], [], f"depends_on[{index}]")
        identity = dep.get("story_id")
        if not STORY_ID.fullmatch(str(identity or "")) or identity == story.get("id"):
            shape.append(f"depends_on[{index}]: invalid/self story ID")
        if type(dep.get("min_version")) is not int or dep["min_version"] < 1:
            shape.append(f"depends_on[{index}]: min_version must be a positive integer")
        if identity in dependencies:
            shape.append(f"depends_on[{index}]: duplicate dependency")
        dependencies.append(identity)

    header_defs = {}
    references = []
    criteria = []
    coverage = []
    commands = []

    def register(item, group):
        identity = item.get("id")
        if not isinstance(identity, str) or not ITEM_ID.fullmatch(identity):
            shape.append(f"{group}: invalid item ID {identity!r}")
        else:
            header_defs.setdefault(identity, []).append(group)
        return identity

    for index, raw in enumerate(rows(header.get("criteria"), "criteria")):
        item = mapping(raw, ["id", "kind", "obligation", "verified_in", "text", "links"], [], f"criteria[{index}]")
        identity = register(item, "criteria")
        criteria.append(item)
        string(item.get("text"), f"{identity}.text")
        if item.get("kind") not in KINDS or item.get("obligation") not in OBLIGATIONS or item.get("verified_in") not in {"pipeline", "post_deploy"}:
            shape.append(f"{identity}: invalid kind/obligation/verified_in")
        prefix = str(identity).split("-", 1)[0]
        if prefix in PREFIX_KINDS and item.get("kind") != PREFIX_KINDS[prefix]:
            shape.append(f"{identity}: kind does not match item prefix")
        for ref in strings(item.get("links"), f"{identity}.links"):
            references.append((identity, "links", ref))

    scope = mapping(header.get("scope"), ["codebase_map", "prohibited_paths", "permitted_test_removals"], [], "scope")
    code_map = mapping(scope.get("codebase_map"), ["create", "modify", "reference"], [], "scope.codebase_map")
    paths = {action: strings(code_map.get(action), f"codebase_map.{action}") for action in ["create", "modify", "reference"]}
    prohibited = strings(scope.get("prohibited_paths"), "prohibited_paths")
    for path in sum(paths.values(), []) + prohibited:
        problem = path_problem(path)
        if problem:
            shape.append(f"path {path!r}: {problem}")
    removal_failures = []
    for index, raw in enumerate(rows(scope.get("permitted_test_removals"), "permitted_test_removals")):
        item = mapping(raw, ["test_id_pattern", "reason"], [], f"permitted_test_removals[{index}]")
        string(item.get("test_id_pattern"), f"removal[{index}].test_id_pattern")
        if not isinstance(item.get("reason"), str) or not item["reason"].strip():
            removal_failures.append(f"removal[{index}]: missing reason")

    for index, raw in enumerate(rows(header.get("coverage"), "coverage")):
        item = mapping(raw, ["id", "covers", "scenario", "level", "fixture", "test_id"], [], f"coverage[{index}]")
        identity = register(item, "coverage")
        coverage.append(item)
        if item.get("level") not in LEVELS:
            shape.append(f"{identity}: invalid coverage level")
        string(item.get("scenario"), f"{identity}.scenario")
        string(item.get("fixture"), f"{identity}.fixture", empty=True)
        string(item.get("test_id"), f"{identity}.test_id", empty=True)
        covers = strings(item.get("covers"), f"{identity}.covers")
        if not covers:
            shape.append(f"{identity}: covers must not be empty")
        for ref in covers:
            references.append((identity, "covers", ref))
        if isinstance(item.get("fixture"), str) and item["fixture"]:
            references.append((identity, "fixture", item["fixture"]))

    for index, raw in enumerate(rows(header.get("checks"), "checks")):
        item = mapping(raw, ["id", "command", "expect"], [], f"checks[{index}]")
        identity = register(item, "checks")
        string(item.get("command"), f"{identity}.command")
        commands.append({"source": identity, "command": item.get("command")})
        expect = mapping(item.get("expect"), [], ["exit_code", "stdout_contains", "stdout_not_contains", "file_exists"], f"{identity}.expect")
        if not expect:
            shape.append(f"{identity}: expect must not be empty")
        for key, value in expect.items():
            if key == "exit_code":
                if type(value) is not int:
                    shape.append(f"{identity}.expect.exit_code: expected integer")
            elif isinstance(value, list):
                if not value:
                    shape.append(f"{identity}.expect.{key}: empty expectation list")
                strings(value, f"{identity}.expect.{key}")
            else:
                string(value, f"{identity}.expect.{key}")

    environment = mapping(header.get("environment"), ["commands_ref", "extra"], [], "environment")
    string(environment.get("commands_ref"), "environment.commands_ref")
    for index, raw in enumerate(rows(environment.get("extra"), "environment.extra")):
        item = mapping(raw, ["purpose", "command"], [], f"environment.extra[{index}]")
        string(item.get("purpose"), f"extra[{index}].purpose")
        string(item.get("command"), f"extra[{index}].command")
        commands.append({"source": f"environment.extra[{index}]", "command": item.get("command")})
    result("1_header_shape_sha_format", shape)

    uniqueness = []
    if story.get("id") in header_defs or story.get("id") in definitions:
        uniqueness.append("story.id collides with an item ID")
    for identity, groups in header_defs.items():
        if len(groups) != 1:
            uniqueness.append(f"{identity}: multiple header definitions {groups}")
    for identity, locations in definitions.items():
        if len(locations) != 1:
            uniqueness.append(f"{identity}: multiple prose definitions")
        expected_section = ITEM_SECTIONS.get(identity.split("-", 1)[0])
        if expected_section and any(number != expected_section for number, _ in locations):
            uniqueness.append(f"{identity}: item definition belongs in section {expected_section}")
        if identity in header_defs:
            group = header_defs[identity][0]
            expected = MIRROR_SECTIONS[group]
            if expected and any(number != expected for number, _ in locations):
                uniqueness.append(f"{identity}: {group} mirror must be in section {expected}")
        elif identity.startswith(("CM-", "DOD-")):
            uniqueness.append(f"{identity}: prose mirror has no header definition")
    result("2_logical_id_uniqueness", uniqueness)

    criterion_ids = {item["id"] for item in criteria if isinstance(item.get("id"), str)}
    known = set(header_defs) | set(definitions)
    dangling = []
    for source, kind, target in references:
        if target not in known:
            dangling.append(f"{source}.{kind}: unresolved {target}")
        elif kind == "covers" and target not in criterion_ids:
            dangling.append(f"{source}.covers: {target} is not a criterion")
        elif kind == "fixture" and (not target.startswith("FX-") or target not in definitions):
            dangling.append(f"{source}.fixture: {target} is not a defined FX item")
    result("3_reference_resolution", dangling)
    prose_failures = [f"{identity}: missing prose definition" for identity in sorted(criterion_ids - definitions.keys())]
    for identity in definitions:
        prefix = identity.split("-", 1)[0]
        if prefix in PREFIX_KINDS and identity not in criterion_ids:
            prose_failures.append(f"{identity}: checkable prose item missing from criteria")
    result("4_criteria_prose_registration", prose_failures)

    gating = [item for item in criteria if item.get("obligation") in {"MUST", "MUST_NOT"} and item.get("verified_in") == "pipeline"]
    covered = {ref for item in coverage for ref in item.get("covers", []) if isinstance(ref, str)} if not shape else set()
    result("5_gating_coverage", [f"{item.get('id')}: no coverage row" for item in gating if item.get("id") not in covered])
    expected_order = [(f"{index:02d}", title) for index, title in enumerate(HEADINGS, 1)]
    section_failures = []
    if ordered != expected_order:
        section_failures.append("Expected exact template headings 01–25 once, in order")
    for number, _ in expected_order:
        if not sections.get(number) or not all(substantive(chunk) for chunk in sections[number]):
            section_failures.append(f"Section {number}: missing or empty/placeholder-only")
    result("7_sections", section_failures)
    overlap = [f"{a} may overlap prohibited {b}; supply disjoint concrete paths" for a in sorted(set(paths["create"] + paths["modify"])) for b in prohibited if might_overlap(a, b)]
    result("8_path_overlap", overlap)
    result("9_test_removal_reasons", removal_failures)
    content = []
    if re.search(r"\bTBD\b|\bTODO\b|Unanswered\s*[—–-]|unconfirmed assumption", body, re.IGNORECASE):
        content.append("Candidate contains an unresolved/placeholder marker")
    if "ET-0" not in definitions or not any("Sections conflict in a way the precedence rule does not resolve" in row for _, row in definitions.get("ET-0", [])):
        content.append("Missing required ET-0 definition")
    result("settled_markers_et0", content)
    fr_count = len({identity for identity in known if identity.startswith("FR-")})
    result("fr_size_guard", [f"{fr_count} FR items exceed 10; approved split required"] if fr_count > 10 else [])
    return {
        "mechanical_pass": all(row["status"] == "PASS" for row in results),
        "results": results,
        "counts": {
            "functional_requirements": fr_count,
            "gating": len(gating),
            "advisory": sum(item.get("obligation") in {"SHOULD", "SHOULD_NOT"} and item.get("verified_in") == "pipeline" for item in criteria),
            "follow_up": sum(item.get("verified_in") == "post_deploy" for item in criteria),
            "not_judged": sum(item.get("obligation") == "MAY" for item in criteria),
            "codebase_map_path_entries": len(set(paths["create"] + paths["modify"])),
        },
        "commands_requiring_user_allowlist_confirmation": commands,
        "manual_checks_required": [
            "SHA exists: git cat-file -e <40-hex-SHA>",
            "Each command user-confirmed allowlist-eligible; runtime matching not certified",
            "Dependency versions, merged files/paths, user merge confirmation, runtime MERGED ancestry",
            "Create paths absent at recorded SHA; main ancestry/intervening changes; HEAD/base stable",
            "Header/prose meaning and mirrors; no unresolved questions/source conflicts/assumptions",
            "Every criterion slice complete; measurements, provenance, precedence, approvals",
            "Concrete glob expansion/file count; size/split and final approval",
        ],
    }


def validate(text):
    if yaml is None:
        return {"mechanical_pass": False, "results": [{"rule": "prerequisite", "status": "FAIL", "detail": ["Preinstalled PyYAML required"]}]}
    try:
        return _validate(text)
    except (ValueError, TypeError, KeyError, IndexError, RecursionError) as exc:
        return {"mechanical_pass": False, "results": [{"rule": "invalid_data", "status": "FAIL", "detail": [str(exc)]}]}


def input_path(argument):
    path = Path(argument)
    if path.is_absolute() or any(part in {".", ".."} for part in argument.split("/")):
        raise ValueError("Use one repository-relative story path without dot/parent components")
    if path.parts[:3] != ("docs", "stories", "refined") or path.suffix != ".md":
        raise ValueError("Input must be a .md story under docs/stories/refined/")
    if path.parent not in {Path("docs/stories/refined"), Path("docs/stories/refined/drafts")}:
        raise ValueError("Input must be directly under refined/ or refined/drafts/")
    if not STORY_ID.fullmatch(path.stem):
        raise ValueError("Input filename must be a story ID, not shared context")
    root = Path.cwd().resolve()
    current = root
    for part in path.parts:
        current /= part
        if current.is_symlink():
            raise ValueError("Symlink input/path components are forbidden")
    if not current.is_file() or not current.resolve().is_relative_to(root / "docs/stories/refined"):
        raise ValueError("Input is missing or outside the refined story boundary")
    return current


def main():
    if yaml is None:
        print(json.dumps({"mechanical_pass": False, "error": "Preinstalled PyYAML required; refiner must not install dependencies"}))
        return 2
    if len(sys.argv) != 2:
        print(json.dumps({"mechanical_pass": False, "error": "Usage: python3 -B validate_story.py docs/stories/refined/[drafts/]<ID>.md"}))
        return 2
    try:
        path = input_path(sys.argv[1])
        report = validate(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError, TypeError, KeyError, RecursionError) as exc:
        print(json.dumps({"mechanical_pass": False, "error": str(exc)}))
        return 2
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["mechanical_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
