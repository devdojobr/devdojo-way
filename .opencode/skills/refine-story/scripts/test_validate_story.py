"""Maintainer-only regression tests using synthetic in-memory contracts.

Run: python3 -B -m unittest discover -s .opencode/skills/refine-story/scripts -p 'test_*.py'
The story-refiner agent is NOT permitted to run this test command.
"""

import copy
import fnmatch
from pathlib import Path
import unittest
from unittest.mock import patch

import yaml

import validate_story as validator


def fixture():
    data = {
        "template_version": "2.0",
        "story": {
            "id": "TEST-01", "version": 1, "type": "change", "title": "Synthetic test",
            "repository": "test/repo", "target_branch": "main",
            "refined_against_sha": "a" * 40, "risk": None, "depends_on": [],
        },
        "criteria": [{"id": "FR-1", "kind": "functional", "obligation": "MUST",
                      "verified_in": "pipeline", "text": "Synthetic outcome", "links": ["GL-1", "D-1", "FX-1"]}],
        "scope": {"codebase_map": {"create": ["src/new/File.java"], "modify": [], "reference": []},
                  "prohibited_paths": ["docs/plans/**"], "permitted_test_removals": []},
        "coverage": [{"id": "CM-1", "covers": ["FR-1"], "scenario": "Synthetic case",
                      "level": "unit", "fixture": "FX-1", "test_id": "ExampleTest#case"}],
        "checks": [{"id": "DOD-1", "command": "existing-wrapper check", "expect": {"exit_code": 0}}],
        "environment": {"commands_ref": "AGENTS.md", "extra": []},
    }
    prose = {f"{i:02d}": "N/A — synthetic fixture" for i in range(1, 26)}
    prose.update({
        "03": "| ID | Domain term | Precise meaning | Name in code |\n|---|---|---|---|\n| GL-1 | Test | Synthetic term | Test |",
        "04": "| ID | Obligation | Requirement |\n|---|---|---|\n| FR-1 | MUST | Synthetic outcome |",
        "06": "| ID | Decision | Rationale | Rejected alternatives |\n|---|---|---|---|\n| D-1 | Synthetic choice | Test source | Other choice |",
        "20": "| ID | Covers | Scenario | Level | Fixture | Test ID |\n|---|---|---|---|---|---|\n| CM-1 | FR-1 | Synthetic case | unit | FX-1 | ExampleTest#case |",
        "21": "| ID | Description | Location or inline payload |\n|---|---|---|\n| FX-1 | Synthetic input | Inline: test |",
        "23": "| ID | Trigger |\n|---|---|\n| ET-0 | Sections conflict in a way the precedence rule does not resolve |",
        "24": "| ID | Command | Expected result |\n|---|---|---|\n| DOD-1 | existing-wrapper check | exit code 0 |",
        "25": "| # | Question | Answer | Source | Date |\n|---|---|---|---|---|\n| 1 | Synthetic question | Synthetic answer | Test fixture | 2026-10-02 |",
    })
    return data, prose


def artifact(data=None, prose=None):
    default_data, default_prose = fixture()
    data = default_data if data is None else data
    prose = default_prose if prose is None else prose
    body = "# TEST-01 — Synthetic test\n\n"
    for i, title in enumerate(validator.HEADINGS, 1):
        number = f"{i:02d}"
        if number in prose:
            body += f"## {number} {title}\n\n{prose[number]}\n\n"
    return "---\n" + yaml.safe_dump(data, sort_keys=False) + "---\n\n" + body


class ContractTests(unittest.TestCase):
    def check_rule(self, text, rule, expected="FAIL"):
        report = validator.validate(text)
        result = next(row for row in report["results"] if row["rule"] == rule)
        self.assertEqual(expected, result["status"], report)

    def test_valid_mirrors_and_references(self):
        report = validator.validate(artifact())
        self.assertTrue(report["mechanical_pass"], report)
        self.assertEqual(1, report["counts"]["gating"])
        self.assertTrue(report["manual_checks_required"])

    def test_duplicate_yaml_key(self):
        self.check_rule(artifact().replace("template_version: '2.0'", "template_version: '2.0'\ntemplate_version: '2.0'"), "parse")

    def test_alias_rejected(self):
        self.check_rule("---\nvalue: &a [test]\nother: *a\n---\n", "parse")

    def test_header_errors(self):
        for field, value in [("refined_against_sha", "abc"), ("version", True), ("type", "other"), ("target_branch", "other")]:
            with self.subTest(field=field):
                data, prose = fixture()
                data["story"][field] = value
                self.check_rule(artifact(data, prose), "1_header_shape_sha_format")
        data, prose = fixture()
        del data["environment"]
        self.check_rule(artifact(data, prose), "1_header_shape_sha_format")

    def test_invalid_type_fails_closed(self):
        data, prose = fixture()
        data["story"]["risk"] = {"invalid": "type"}
        self.assertFalse(validator.validate(artifact(data, prose))["mechanical_pass"])

    def test_id_collisions(self):
        data, prose = fixture()
        data["story"]["id"] = "FR-1"
        self.check_rule(artifact(data, prose), "2_logical_id_uniqueness")
        data, prose = fixture()
        data["criteria"].append(copy.deepcopy(data["criteria"][0]))
        self.check_rule(artifact(data, prose), "2_logical_id_uniqueness")
        data, prose = fixture()
        data["coverage"][0]["id"] = "FR-1"
        self.check_rule(artifact(data, prose), "2_logical_id_uniqueness")
        data, prose = fixture()
        prose["06"] += "\n- GL-1: Another definition"
        self.check_rule(artifact(data, prose), "2_logical_id_uniqueness")
        data, prose = fixture()
        prose["19"], prose["20"] = prose["20"], prose["19"]
        self.check_rule(artifact(data, prose), "2_logical_id_uniqueness")

    def test_references(self):
        for field, value in [("links", "BR-99"), ("covers", "GL-1"), ("fixture", "D-1"), ("fixture", "FX-99")]:
            with self.subTest(field=field, value=value):
                data, prose = fixture()
                if field == "links":
                    data["criteria"][0][field].append(value)
                else:
                    data["coverage"][0][field] = [value] if field == "covers" else value
                self.check_rule(artifact(data, prose), "3_reference_resolution")

    def test_prose_registration(self):
        data, prose = fixture()
        prose["04"] = "FR-1 merely mentioned without elaboration."
        self.check_rule(artifact(data, prose), "4_criteria_prose_registration")
        data, prose = fixture()
        prose["05"] = "- BR-1: Required synthetic rule"
        self.check_rule(artifact(data, prose), "4_criteria_prose_registration")

    def test_gating_and_counts(self):
        data, prose = fixture()
        data["coverage"] = []
        self.check_rule(artifact(data, prose), "5_gating_coverage")
        data["criteria"][0]["verified_in"] = "post_deploy"
        self.check_rule(artifact(data, prose), "5_gating_coverage", "PASS")
        self.assertEqual(1, validator.validate(artifact(data, prose))["counts"]["follow_up"])
        data["criteria"][0].update(verified_in="pipeline", obligation="SHOULD_NOT")
        self.assertEqual(1, validator.validate(artifact(data, prose))["counts"]["advisory"])
        data["criteria"][0]["obligation"] = "MAY"
        self.assertEqual(1, validator.validate(artifact(data, prose))["counts"]["not_judged"])

    def test_sections(self):
        for content in ["", "N/A", "| ID | Domain term | Precise meaning | Name in code |\n|---|---|---|---|\n| GL-1 | | | |"]:
            with self.subTest(content=content):
                data, prose = fixture()
                prose["03"] = content
                self.check_rule(artifact(data, prose), "7_sections")
        data, prose = fixture()
        del prose["15"]
        self.check_rule(artifact(data, prose), "7_sections")

    def test_overlap(self):
        data, prose = fixture()
        data["scope"]["prohibited_paths"] = ["src/**"]
        self.check_rule(artifact(data, prose), "8_path_overlap")
        self.assertTrue(validator.might_overlap("src/**/*.java", "src/**/*.md"))
        self.assertFalse(validator.might_overlap("src/**", "docs/**"))

    def test_removal_reason(self):
        data, prose = fixture()
        data["scope"]["permitted_test_removals"] = [{"test_id_pattern": "OldTest#case", "reason": ""}]
        self.check_rule(artifact(data, prose), "9_test_removal_reasons")

    def test_size_threshold_all_fr(self):
        data, prose = fixture()
        for i in range(2, 12):
            item = copy.deepcopy(data["criteria"][0])
            item.update(id=f"FR-{i}", obligation="MAY")
            data["criteria"].append(item)
            prose["04"] += f"\n| FR-{i} | MAY | Synthetic {i} |"
        self.check_rule(artifact(data, prose), "fr_size_guard")

    def test_draft_wrapper(self):
        text = "# Blocking\n\n- Pending mechanical preflight.\n\n<!-- refined-story-candidate -->\n" + artifact()
        self.assertTrue(validator.validate(text)["mechanical_pass"])

    def test_markers_et0(self):
        data, prose = fixture()
        prose["11"] = "TBD"
        self.check_rule(artifact(data, prose), "settled_markers_et0")
        data, prose = fixture()
        prose["23"] = "N/A — synthetic fixture"
        self.check_rule(artifact(data, prose), "settled_markers_et0")

    def test_unknown_expectation_field(self):
        data, prose = fixture()
        data["checks"][0]["expect"]["arbitrary_command"] = "never execute"
        self.check_rule(artifact(data, prose), "1_header_shape_sha_format")

    def test_input_boundary(self):
        for path in ["/tmp/TEST-01.md", "docs/stories/refined/../TEST-01.md", "docs/stories/refined/TECH-CONTEXT.md", "src/TEST-01.md"]:
            with self.subTest(path=path), self.assertRaises(ValueError):
                validator.input_path(path)

    def test_missing_parser(self):
        text = artifact()
        with patch.object(validator, "yaml", None):
            self.assertFalse(validator.validate(text)["mechanical_pass"])

    def test_v2_frontmatter_and_permission_examples(self):
        opencode_dir = Path(__file__).resolve().parents[3]
        agent = yaml.safe_load((opencode_dir / "agents/story-refiner.md").read_text().split("---", 2)[1])
        skill = yaml.safe_load((opencode_dir / "skills/refine-story/SKILL.md").read_text().split("---", 2)[1])
        self.assertEqual("primary", agent["mode"])
        self.assertEqual("refine-story", skill["name"])
        self.assertTrue(agent["description"] and skill["description"])
        self.assertNotIn("permission", agent)

        # Documentation-based last-match model, not a live OpenCode sandbox test.
        def effect(action, resource):
            answer = "ask"
            for rule in agent["permissions"]:
                self.assertEqual({"action", "resource", "effect"}, set(rule))
                pattern = rule["resource"]
                matched = fnmatch.fnmatchcase(resource, pattern) or (action == "shell" and pattern.endswith(" *") and resource == pattern[:-2])
                if fnmatch.fnmatchcase(action, rule["action"]) and matched:
                    answer = rule["effect"]
            return answer

        examples = [
            ("edit", "docs/stories/refined/REVIEW-01.md", "allow"),
            ("edit", "src/main/java/academy/devdojo/File.java", "deny"),
            ("edit", "pom.xml", "deny"),
            ("edit", "docs/plans/idea.md", "deny"),
            ("edit", ".opencode/agents/story-refiner.md", "deny"),
            ("edit", "AGENTS.md", "deny"),
            ("shell", "git status", "ask"),
            ("shell", "git cat-file -e " + "a" * 40, "ask"),
            ("shell", "git cat-file -p " + "a" * 40, "deny"),
            ("shell", "git push origin main", "deny"),
            ("shell", "git diff", "deny"),
            ("shell", "./mvnw test", "deny"),
            ("shell", "git add -- src/File.java", "deny"),
            ("shell", "git add -- docs/stories/refined/REVIEW-01.md", "ask"),
            ("shell", "git commit --only -m 'Approved message' -- docs/stories/refined/REVIEW-01.md", "ask"),
            ("shell", "python3 -B .opencode/skills/refine-story/scripts/validate_story.py docs/stories/refined/drafts/REVIEW-01.md", "ask"),
            ("shell", "python3 -m pip install PyYAML", "deny"),
            ("webfetch", "https://example.com", "deny"),
            ("execute", "*", "deny"),
            ("external_directory", "/outside/*", "deny"),
            ("subagent", "general", "deny"),
            ("skill", "refine-story", "allow"),
            ("skill", "other-skill", "deny"),
        ]
        for action, resource, expected in examples:
            with self.subTest(action=action, resource=resource):
                self.assertEqual(expected, effect(action, resource))


if __name__ == "__main__":
    unittest.main()
