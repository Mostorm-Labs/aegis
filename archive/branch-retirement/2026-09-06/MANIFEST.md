# Aegis Branch Retirement Archive — 2026-09-06

Status: **HISTORICAL / NON-CURRENT / NON-AUTHORITY**

This archive preserves branch-only control and evidence artifacts before their remote branches are retired.

Nothing under this archive becomes Current Authority, an executable package, a current Gate decision, or a release claim merely because it is present on `main`.

Archive baseline:

```yaml
repository: Mostorm-Labs/aegis
archive_parent: 893f9ef9aab70edf4c1ea3b2fcff699576ca494e
archive_date: 2026-09-06
purpose: preserve branch-only historical bytes before branch deletion
content_policy: byte-identical source blobs copied by Git blob SHA
```

## Preserved sources

| Source branch | Source commit | Original path | Source blob SHA | Archived path | Classification |
| --- | --- | --- | --- | --- | --- |
| `aegis/release-v0.2.0-beta.2-control` | `5b9787b9b751383fcde59a616b35ccf01e56238d` | `docs/aegis-v0.2.0-beta.2-release-candidate-task-package.md` | `7b032d0a79614bddc3e254d0a7f09d4834649bfa` | `archive/branch-retirement/2026-09-06/files/docs/aegis-v0.2.0-beta.2-release-candidate-task-package.md` | historical release-control package |
| `aegis/release-v0.2.0-beta.2-control` | `5b9787b9b751383fcde59a616b35ccf01e56238d` | `docs/superpowers/plans/2026-09-06-aegis-v0.2.0-beta.2-release-candidate.md` | `34acfab1353974a5299d97dd6655bd92ef2feee6` | `archive/branch-retirement/2026-09-06/files/docs/superpowers/plans/2026-09-06-aegis-v0.2.0-beta.2-release-candidate.md` | historical implementation plan |
| `chatgpt/verification-productization-vp-i01-p31-02` | `b979f1fc59178c16285449a92f02dd5964e523d0` | `docs/verification-productization-vp-i01-task-package-v0.2.md` | `082ebb5e24fd3f0db054eebe8136808f32fc5e79` | `archive/branch-retirement/2026-09-06/files/docs/verification-productization-vp-i01-task-package-v0.2.md` | historical P31 package |
| `chatgpt/verification-productization-vp-i01-p36-evidence` | `9f8c689c7cc54a7972cd515689dcc13c824c4256` | `artifacts/verification-productization/vp-i01/p36-mutant-qualification.json` | `0dce453f0d9fb47e9fd6acdca46d67d06663dcf6` | `archive/branch-retirement/2026-09-06/files/artifacts/verification-productization/vp-i01/p36-mutant-qualification.json` | historical P36 evidence |
| `chatgpt/verification-productization-vp-i02-evidence` | `1c6753f5998cd063d4300e426d8f80a868088c6d` | `artifacts/verification-productization/vp-i02-p32-execution-evidence.json` | `7de99d99b94ec6ccdf38e4a22c2231498b642fe8` | `archive/branch-retirement/2026-09-06/files/artifacts/verification-productization/vp-i02-p32-execution-evidence.json` | historical P32 evidence |
| `chatgpt/verification-productization-vp-i02-p36-evidence` | `3f6e51fd9364793eb4694c0a9ba56c4366b14231` | `artifacts/verification-productization/vp-i02-p36/accumulated-verification-productization.txt` | `ca33137e9830b36e46ef45047afe7925ec719265` | `archive/branch-retirement/2026-09-06/files/artifacts/verification-productization/vp-i02-p36/accumulated-verification-productization.txt` | historical P36 evidence |
| `chatgpt/verification-productization-vp-i02-p36-evidence` | `3f6e51fd9364793eb4694c0a9ba56c4366b14231` | `artifacts/verification-productization/vp-i02-p36/focused-vp-i02.txt` | `844b507c247d1f1d342e91f27533f71dba3cf037` | `archive/branch-retirement/2026-09-06/files/artifacts/verification-productization/vp-i02-p36/focused-vp-i02.txt` | historical P36 evidence |
| `chatgpt/verification-productization-vp-i02-p36-evidence` | `3f6e51fd9364793eb4694c0a9ba56c4366b14231` | `artifacts/verification-productization/vp-i02-p36/manifest.json` | `c17807c0ddafa76358c8b76f554703899286fdc2` | `archive/branch-retirement/2026-09-06/files/artifacts/verification-productization/vp-i02-p36/manifest.json` | historical P36 evidence manifest |

## Retirement rule

The five source branches may be deleted only after this archive commit is merged into `main` and the archived file blob SHAs are re-read from the merged revision and confirmed equal to the source blob SHAs above.

This archive does not modify `.aegis/**`, does not supersede any Authority, does not issue P34 PASS, and does not alter release artifacts or Project State v0.6 work.
