import json
import subprocess
import sys
import unittest

from tests.verification_productization.ecv0_fixtures import load_required_module, valid_verification_spec
from tools.aegis_proof.spec import VerificationSpecValidator


class CliParityTests(unittest.TestCase):
    def test_EC_S17_library_and_cli_validation_are_semantically_equivalent(self):
        load_required_module("tools.aegis_proof.cli")
        spec = valid_verification_spec()
        direct = VerificationSpecValidator.validate(spec)
        expected = {
            "valid": direct.valid,
            "findings": [
                {"code": f.code, "message": f.message, "path": f.path}
                for f in direct.findings
            ],
        }
        proc = subprocess.run(
            [sys.executable, "-m", "tools.aegis_proof", "validate-spec"],
            input=json.dumps(spec),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout), expected)
        self.assertEqual(proc.stderr, "")

    def test_cli_contract_failure_is_nonzero_and_structured(self):
        load_required_module("tools.aegis_proof.cli")
        proc = subprocess.run(
            [sys.executable, "-m", "tools.aegis_proof", "validate-spec"],
            input="not-json",
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertNotEqual(proc.returncode, 0)
        payload = json.loads(proc.stdout)
        self.assertFalse(payload["ok"])
        self.assertIn("error", payload)
        self.assertTrue(proc.stderr)

    def test_EC_M16_weakened_cli_semantics_are_detected_by_parity_oracle(self):
        cli = load_required_module("tools.aegis_proof.cli")
        invalid = valid_verification_spec()
        invalid["schema_version"] = "999"
        direct = VerificationSpecValidator.validate(invalid)
        production = cli.execute("validate-spec", invalid)
        weakened_mutant = {"valid": True, "findings": []}
        self.assertNotEqual(weakened_mutant, production)
        self.assertEqual(production["valid"], direct.valid)
        self.assertFalse(production["valid"])


if __name__ == "__main__":
    unittest.main()
