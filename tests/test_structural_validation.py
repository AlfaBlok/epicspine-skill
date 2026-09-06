"""Strict structural/data gates remain independent from prose preferences."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_validate_spine import validate_spine as v

ROOT = Path(__file__).parents[1]


class StructuralValidationTests(unittest.TestCase):
    def document(self, text):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'EPIC.md'
            path.write_text(text)
            return v.validate_local(path)

    def source(self, profile='full', dialect='v2'):
        if profile == 'full':
            return (ROOT / f'tests/fixtures/{"sprint-v2" if dialect == "v2" else "legacy-v1"}.md').read_text()
        text = (ROOT / 'examples/EPIC-COMPACT-EXAMPLE.md').read_text()
        if dialect == 'v2':
            text = text.replace('Spine dialect: v1', 'Spine dialect: v2\nAcceptance surface: cli')
            old = v.parse_sections(text)['Definition Of Done']
            text = text.replace(old, self.acceptance())
        return text

    def acceptance(self, outcome='The input prints its greeting.', method='cli: Invoke the executable with a sample and save the returned text and process status.'):
        return f'SHIP\n\nAcceptance outcome: {outcome}\nEvidence method: {method}\n\n- [ ] Exercise the sample once.\n\nHARDEN\n\n- [ ] Later performance work.'

    def test_equivalent_free_phrasing_and_one_step_pass_in_both_profiles(self):
        for profile in ('full', 'compact'):
            for wording in ('A greeting appears for the supplied name.', 'The supplied name is included in the returned greeting.'):
                source = self.source(profile)
                source = source.replace(v.parse_sections(source)['Definition Of Done'], self.acceptance(wording))
                doc = self.document(source)
                self.assertFalse(doc.fails(strict=True), doc.diagnostics)
                self.assertTrue(any(d['category'] == 'advisory' for d in doc.diagnostics))
                self.assertFalse(any('5-12' in d['message'] for d in doc.diagnostics))

    def test_surface_qualified_methods_need_no_magic_prose(self):
        for surface in v.ACCEPTANCE_SURFACES:
            source = self.source('compact').replace('Acceptance surface: cli', f'Acceptance surface: {surface}')
            source = source.replace(v.parse_sections(source)['Definition Of Done'], self.acceptance(method=f'{surface}: Exercise the described sample and retain the observed result for review.'))
            self.assertFalse(self.document(source).fails(strict=True))

    def test_missing_placeholder_or_wrong_surface_evidence_is_required(self):
        for profile in ('full', 'compact'):
            for method in ('', 'cli: <fill>', 'cli: none', 'browser: Capture the screen.'):
                source = self.source(profile)
                source = source.replace(v.parse_sections(source)['Definition Of Done'], self.acceptance(method=method))
                doc = self.document(source)
                self.assertTrue(doc.fails(strict=True))
                self.assertTrue(any(d['rule_id'] == 'ES-D-EVIDENCE' and d['fails_strict'] for d in doc.diagnostics))

    def test_copied_legacy_boilerplate_does_not_replace_missing_evidence(self):
        source = self.source().replace('Evidence: exact commands, inputs, exit codes and outputs.\n', '')
        doc = self.document(source)
        self.assertTrue(doc.fails(strict=True))
        self.assertTrue(any(d['rule_id'] == 'ES-D-EVIDENCE' for d in doc.diagnostics))

    def test_unresolved_explicit_outcome_cannot_hide_behind_steps(self):
        for value in ('', '<outcome>', 'tbd'):
            source = self.source('compact')
            source = source.replace(v.parse_sections(source)['Definition Of Done'], self.acceptance(outcome=value))
            doc = self.document(source)
            self.assertTrue(doc.fails(strict=True))
            self.assertTrue(any(d['rule_id'] == 'ES-D-ACCEPTANCE' for d in doc.diagnostics))

    def test_all_profiles_and_dialects_keep_malformed_table_and_missing_data_gates(self):
        for profile in ('full', 'compact'):
            for dialect in ('v1', 'v2'):
                source = self.source(profile, dialect)
                doc = self.document(source.replace('|---|', '|--|', 1))
                self.assertTrue(doc.errors)
                self.assertTrue(doc.fails())
                self.assertTrue(any(d['rule_id'] == 'ES-S-TABLE' for d in doc.diagnostics))
                doc = self.document(source.replace('Repository: example/repo', 'Repository: <repo>').replace('Repository: example/validator', 'Repository: <repo>'))
                self.assertTrue(doc.fails(strict=True))
                self.assertTrue(any(d['category'] == 'required-data' for d in doc.diagnostics))

    def test_empty_acceptance_body_is_required_in_every_profile(self):
        for profile in ('full', 'compact'):
            source = self.source(profile, 'v1')
            doc = self.document(source.replace(v.parse_sections(source)['Definition Of Done'], ''))
            self.assertTrue(doc.fails(strict=True))

    def test_explicit_no_blocker_values_are_resolved_but_blank_is_not(self):
        source = self.source('compact', 'v1')
        header = '| Spine ID | Relationship | Spine | Purpose | Status | Health / Blocker | Latest Evidence | Last Rolled Up | Next Action |\n|---|---|---|---|---|---|---|---|---|\n'
        for value in ('none', 'no blocker', 'no blockers', ''):
            doc = self.document(source + '\n## Spine Map\n\n' + header + f'| child | child | child.md | Test | ready | {value} | report.md | 2026-09-06 | Review |\n')
            self.assertEqual(value == '', any('Health / Blocker' in w for w in doc.warnings))

    def test_diagnostics_include_graph_errors_added_after_local_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'EPIC.md'
            path.write_text(self.source('compact', 'v1'))
            doc = v.validate_local(path)
            self.assertFalse(doc.errors)
            v.validate_graph([doc])
            self.assertTrue(any(d['rule_id'] == 'ES-S-GRAPH' for d in v.result_for(doc)['diagnostics']))
            self.assertTrue(doc.fails())

    def test_cli_json_keeps_legacy_keys_and_reports_advisory_without_failure(self):
        source = self.source('compact')
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'EPIC.md'; path.write_text(source)
            result = subprocess.run([sys.executable, str(ROOT/'skill/epic-spine/scripts/validate_spine.py'), '--strict', '--json', str(path)], capture_output=True, text=True)
            self.assertEqual(0, result.returncode, result.stdout)
            import json
            data = json.loads(result.stdout)[0]
            self.assertTrue({'path', 'errors', 'warnings', 'diagnostics'} <= data.keys())
            self.assertTrue(all(not d['fails_strict'] for d in data['diagnostics']))
