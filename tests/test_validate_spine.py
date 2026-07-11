import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "skill/epic-spine/scripts/validate_spine.py"
spec = importlib.util.spec_from_file_location("validate_spine", SCRIPT)
validator = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(validator)


class ValidatorCompatibilityTests(unittest.TestCase):
    def test_v1_template_has_only_warnings_for_v2_rules(self):
        result = validator.validate(ROOT / "skill/epic-spine/assets/epic-spine-template.md")
        self.assertEqual([], result["errors"])
        self.assertTrue(result["warnings"])

    def test_default_cli_keeps_v1_compatible_but_strict_promotes_warnings(self):
        template = ROOT / "skill/epic-spine/assets/epic-spine-template.md"
        default = subprocess.run([sys.executable, str(SCRIPT), str(template)], check=False)
        strict = subprocess.run([sys.executable, str(SCRIPT), "--strict", str(template)], check=False)
        self.assertEqual(0, default.returncode)
        self.assertEqual(1, strict.returncode)

    def test_superseded_redirect_warning(self):
        source = (ROOT / "skill/epic-spine/assets/epic-spine-template.md").read_text()
        source = source.replace("Status: draft | ready | active | pending — DISPATCH ONLY AFTER <condition> | CLOSED | ON HOLD | SUPERSEDED by <path> — do not execute from this document", "Status: SUPERSEDED")
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as handle:
            handle.write(source)
            path = Path(handle.name)
        try:
            result = validator.validate(path)
            self.assertTrue(any("SUPERSEDED status" in warning for warning in result["warnings"]))
        finally:
            path.unlink()


if __name__ == "__main__":
    unittest.main()
