# AgentReady v0.4 engineering result

Overall: PARTIAL — implementation and synthetic acceptance completed; external account/device gates remain BLOCKED.

## PASS

- v0.3.0 baseline imported and retained; 33 baseline tests passed.
- v0.4.0: existing lark-cli profile selection, explicit date range, bounded task pagination, nested error and pagination validation, missing-scope recovery, completed/cancelled record filtering.
- Personal native CLI counts through ekctl, remindctl and Dayflow, opt-in reads; no screen capture, mutations, new calendar UI, credentials or company data aggregation.
- 55 unit/regression/subprocess E2E tests passed on macOS/Python 3.12. Synthetic fixtures/executable CLIs are explicitly labeled synthetic.
- CLI E2E covers tasks/calendar/messages and scope failure without losing other source results; launch/publish/audit checks included.
- CI workflow covers macOS/Linux with Python 3.9/3.12 and uploads synthetic evidence; 14 local CI-equivalent commands passed in clean candidate.
- Public candidate has clean Git history; tree/history scan passed. Private execution handoff files are excluded from candidate history.
- Skills, Chinese setup, recovery, rollback, version and publication instructions updated; one-shot launcher preserves provider/model credentials and bypasses no security gate.
- Actual authorized live work task count read succeeded; calendar failed with explicit missing scope rather than inferred empty agenda. Only sanitized status is public.
- Actual Dayflow CLI read succeeded with zero activities. Existing application/local AI services were preserved.

## PARTIAL / BLOCKED

- Apple Calendar and Reminders reads: OS authorization pending. Test-list mutation and iPhone sync not performed.
- Dayflow real capture, visual analysis, Timeline and daily statistics: consent/non-sensitive window scope pending; zero records are not business acceptance.
- Feishu calendar: missing `calendar:calendar.event:read`; no OAuth changes or company task writes performed.
- Hermes trial: existing resource channel received a protocol-only request; reply pending. Queue receipt is not collaboration completion.
- GitHub: no usable local authenticated CLI confirmed; broker account invalid, binary transfer timed out. Release scripts/candidate prepared; no public push claimed.
- GitHub URL: NONE. Remote GitHub Actions result: NOT RUN. Local CI-equivalent result: 14/14 PASS; this does not verify remote matrix runners.
- No notification schedule, production deployment or overnight background coding service created. Engineering was actually executed in this active session; logs and commits persist locally.

## Evidence and commits

Private command logs/results: `.reports/engineering/`; clean candidate CI logs: `.reports/ci/` in the separately prepared candidate. Public material contains only generic status, not business records or host paths.
Baseline: `16789f1`. Implementation: `76bfc82`. Documentation: `fcaadd4`.
Reproduce: `python3 -m unittest discover -s tests -v`; `python3 scripts/audit_public.py` in clean candidate; `bash scripts/publish_github.sh` previews publication, explicit `--apply` requires authentication and audited clean tree.

Next external steps: native permission approval and approved capture window, iPhone readback, scoped calendar OAuth if desired, local GitHub login. Rerun affected read/CI checks afterwards without reinstalling existing applications.
