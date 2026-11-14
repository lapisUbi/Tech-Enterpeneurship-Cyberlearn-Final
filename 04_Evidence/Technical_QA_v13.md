# Technical verification | package v13, build 2.1.1
Review date: 13 November 2026 (Asia/Qyzylorda). All test records are synthetic.

## Passed
- JavaScript parse and nine complete component paths: three languages x three roles; 12 unique items per shift, balanced threat/routine items, scoring, JSON/CSV payloads, in-memory state, validation. See Component_QA_v13.json.
- Regression_v13.cjs: record-language CSV export; canonical duplicate comparison; early follow-up refusal; eligible follow-up uses only reserved items. Controlled synthetic timestamps are used only for software QA, never human follow-up evidence.
- Receiver_QA.py: 15 in-process checks including token requirements, loopback reviewer restriction, actual temporary JSON/HTML writes, duplicate/conflict responses, malformed records, premature follow-up and selective deletion. See Receiver_QA_v13.json.
- Finance: 1,693 formula values independently evaluated, zero significant cache mismatches and no evaluator errors/cycles. Seven scenarios rebuilt; this is not native Excel execution.
- Both MP4 files decoded with FFmpeg without reported errors. Advertisement metadata: 46 seconds, 1920 x 1080, H.264 video / AAC audio.

## Fixes
1. CSV previously used the reviewer interface language while declaring the participant record language. It now uses q.text[r.lang].
2. Offline importer previously classified every repeated ID as an ordinary duplicate, even when its answers or feedback differed. It now rejects a conflicting record using a canonical fingerprint; matching data and irrelevant derived-summary differences remain duplicates.
3. Windows installer now copies READ_ME_EN.txt as well as the application and receiver.

## Not verified here
Chromium launch failed because the execution environment denied socket creation (Operation not permitted). No actual browser UI, file-origin persistence, download, keyboard/mobile layout, live HTTP/LAN transport or Windows installer execution is claimed. The in-process handler harness bypasses socket transport. Human comprehension, accessibility with assistive technology, and retained learning require people.

## Reproduce
From 04_Evidence: node Technical_QA_component.cjs; node Regression_v13.cjs; python Receiver_QA.py.
From 06_Finance: python Audit_Financial_Model.py.
Browser_Rehearsal.cjs is an additional Playwright test supplied for a machine where Chromium can run; its presence is not a pass result. It uses synthetic records and temporary browser contexts.
Historical Technical_QA files describe v12; this file and v13 JSON results describe the patched release.
