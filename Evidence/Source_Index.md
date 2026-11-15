# CyberLearn evidence source index - 15 November 2026

## Primary project records
- Human_Test_Results/CyberLearn_*.json: five original exports, unchanged. Analysis_Final.json lists exact IDs, UTC timestamps, duration, raw-score recalculation and hashes. Analysis_v15.json is retained as the prior hash and control record used by Recheck_Results.py. It is not a separate dataset.
- Human_Test_Results/Feedback_Record_RU.txt: supplied coded summaries of five feedback blocks, including quoted fragments and mapping/ratings limitations. It is not a verbatim interview transcript. A/B individual mapping is unknown; C is provisional; D/E are explicitly paired.
- Staff_Test_Register.csv: five supplied completed sessions. Roles/languages come from the application; participation is team-confirmed. Consent, device, help and unaided observation remain unknown.
- The team confirmed completion in the supplied project conversation. Roles, consent, attention and assistance were not independently verified.

## Methods and absent evidence
- Discovery_Design_EN.md: ten-question guide, eight role cases and secondary project questionnaire summaries. The original A3/A4/A5 reports and survey export were not available to recheck. The earlier mainly student survey cannot establish staff prevalence or purchasing demand.
- Fieldwork_EN.md: future observed-test protocol and proposed targets, not a retrospective observation log.
- Buyer_Interview_Register.csv: uncompleted two-buyer template. No completed interview, commitment or sale is asserted.
- Team_Contribution_Record.csv: three names with unfilled declarations. Proposed risk ownership or speaking roles do not establish historical contribution.

## Implementation and reproducible checks
- ../MVP/CyberLearn.html and classroom.py: distributed 2.2.0 source; unchanged bank in HTML and bank_rules.json. Source functions scoreGuide, progressSummary and handoffGuide identify the three new improvements.
- QA_Application.cjs / .json: 204 assertions using the complete distributed script with a minimal host DOM adapter. Nine twelve-question language/role routes, error handling, generated markup, state, payloads, imports, duplicates, deletion and day-seven logic. Not a browser engine or human usability test.
- QA_Receiver_HTTP.py / .json: 21 actual loopback HTTP assertions with synthetic records and temporary storage.
- Receiver_QA.py / .json: 15 in-process handler checks, including non-loopback reviewer denial.
- QA_Regression.cjs / .json: four additional synthetic regression results for CSV language, duplicate fingerprint and follow-up gating.
- Risk_Register.csv / Risk_Register_Note.txt: seven planning risks, likelihood/impact scores explicitly labelled analyst judgements, proposed owners and residual risk.
- Feature_Priorities.txt and ../CHANGELOG.txt: prioritisation and actual change trace.

## Finance and media
- ../Finance/CyberLearn_A6_Model.xlsx: unchanged original forecast; SHA-256 e2c48132892a4f72626ccf24c26ce426b73a7e929b7ddc09a4c997125b9a59be.
- ../Finance/Audit_Financial_Model.py and Finance_Audit_Results.json: 1,693 formula comparisons and independent economic rebuild. Native spreadsheet recalculation and demand validation were not performed.
- ../Finance/Price_Sensitivity.py: separate conditional 600/700 calculation, no workbook change.
- ../Media/: unchanged 46-second advertisement and 32.25-second silent earlier-build demo; Media_Review.txt distinguishes current checks from production notes.
- Media_Inspection.json and Media_Rights/: current metadata/hashes and retained historical audio/font records. Production stems referenced by the old note are not included and were not independently reverified.

## Public sources read for this revision
1. Bureau of National Statistics (2025), Higher education at the beginning of 2025-2026. The page states 116 institutions. The 200-seat and 600-KZT assumptions are ours, not BNS data.
https://stat.gov.kz/en/industries/socialstatistics/stat-edu-science-inno/publications/470854/
2. Verizon (2022), 2022 Data Breach Investigations Report, summary of findings, p. 8. Human element includes stolen credentials, phishing, misuse and error; 82% is historical and not a university prevalence estimate. The report is mirrored at the URL below. The official infographic independently states the 82% headline; the direct official full-PDF fetch timed out in this review.
https://d110erj175o600.cloudfront.net/wp-content/uploads/2022/05/24124727/2022-data-breach-investigations-report-dbir.pdf
https://www.verizon.com/business/resources/reports/dbir/2022-dbir-infographic.pdf
3. Merritt et al. (2024), NIST SP 800-50 Rev. 1. Official publication page supports lifecycle learning and evaluation guidance; it does not validate CyberLearn's instrument.
https://csrc.nist.gov/pubs/sp/800/50/r1/final
https://doi.org/10.6028/NIST.SP.800-50r1
4. KnowBe4 pricing, retrieved 15 November 2026: 101-250 seats, USD 1.97 Foundation or 3.19 Advanced per seat/month on a three-year term; May 2026 listing, taxes excluded, regional variation. Not a Kazakhstan quote.
https://www.knowbe4.com/products/security-awareness-training/pricing
5. Hoxhunt official pricing and phishing-training pages, retrieved 15 November 2026. Adaptive phishing training; employee/capability-based quote. No numeric quote obtained.
https://hoxhunt.com/pricing
https://hoxhunt.com/product/phishing-training
6. SoSafe official pricing page, retrieved 15 November 2026. Core/Advanced packages and scale-dependent tailored pricing. No numeric price used in this comparison. An alternate /new-pricing/ search result failed direct retrieval, so it was not used as a pricing basis.
https://sosafe-awareness.com/pricing/
7. Microsoft Defender for Office 365 official page, retrieved 15 November 2026. Plan 2 lists USD 5/user/month paid yearly, includes attack simulation training and wider security capabilities. Existing entitlement and local terms need buyer confirmation.
https://www.microsoft.com/en-us/security/business/siem-and-xdr/microsoft-defender-office-365
Vendor descriptions are not independent effectiveness evaluations. No competitor product was purchased or tested.

## Assessment and final verification
- Final_Exam_Requirements.pdf: complete supplied 11-page rubric, authoritative for this revision.
- ../Rubric_Compliance.pdf / .csv: requirement-level audit and remaining evidence gaps.
- ../Team_Tasks.txt: human declarations, consent, translation, rehearsal and defence actions.
- Package_Manifest.json: checksums and file-level parse/decode scope for the completed package.
- AI_Process_Notes.txt: material AI assistance, verification and unresolved human review.
