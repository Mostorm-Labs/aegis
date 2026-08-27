#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.aegis_skillset.distribution import validate_generated_skills

errors = validate_generated_skills(ROOT)
if errors:
    for error in errors:
        print("INVALID:", error)
    raise SystemExit(1)
print("SKILLS_VALID")
