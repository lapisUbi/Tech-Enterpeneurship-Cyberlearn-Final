# CyberLearn financial model audit

Review prepared for Submission_v12_2026-11-10. Currency: KZT.

## Scope and method

The reviewed file is CyberLearn_A6_Model.xlsx, 95,674 bytes. Its SHA-256 is:

e2c48132892a4f72626ccf24c26ce426b73a7e929b7ddc09a4c997125b9a59be

The source workbook and submission copy have the same checksum. Neither was edited.

Two read-only checks were performed:
1. Extract the workbook's stored formulas and values from its OOXML package and independently evaluate all 1,693 formulas, including dependencies, ranges and the functions actually used.
2. Rebuild annual revenue, costs and cash flow, the base 60-month cash schedule, and all seven scenarios directly from the input drivers. This separately checks the business arithmetic rather than only comparing stored formula text.

All 1,693 formula results agree with their saved values within 0.000001 KZT. The maximum numeric difference is 0.000000029802322387695312, attributable to floating-point arithmetic. No formula errors, circular dependencies or missing formula caches were found. The base monthly cash-flow and cumulative-balance differences are below 0.000001 KZT. Indicators!B30:B34 and B36 are zero.

This is not a native Microsoft Excel or LibreOffice recalculation. Native application behaviour, formatting and editing boundaries were not tested. The supplied script is limited to the formula language used in this workbook.

## Base-case controls

| Measure | Verified result | Workbook location |
| --- | ---: | --- |
| Year-zero launch investment | 8,100,000.00 | Startup!D11 |
| Five-year forecast receipts | 235,434,672.00 | Indicators!B6 |
| Total project costs, including launch once | 179,734,635.86 | Indicators!B7 |
| Undiscounted five-year net benefit | 55,700,036.14 | Indicators!B8 |
| Present value of benefits | 116,298,842.59 | Indicators!B9 |
| Present value of costs | 98,947,093.92 | Indicators!B10 |
| Net present value, 20% nominal annual rate | 17,351,748.67 | Indicators!B11 |
| Discounted benefit-cost ratio | 1.175364 | Indicators!B12 |
| Five-year cost-based ROI | 30.9902% | Indicators!B14 |
| Annual interpolated payback | 3.305526 years | Indicators!B16 |
| Monthly-model payback | 3.575585 years | Indicators!B17 |
| Discounted annual payback | 3.884907 years | Indicators!B18 |
| Peak cash financing gap | 21,169,104.00 | Indicators!B19 |
| 15% liquidity reserve | 3,175,365.60 | Indicators!B20 |
| Base funding capacity including reserve | 24,344,469.60 | Indicators!B21 |
| NPV break-even monthly seat price | 504.371247 | Indicators!B26 |

The peak deficit occurs in month 18, June of operating year 2. Monthly payback is approximately 42.907 months, with the crossing in month 43, July of operating year 4. The annual and monthly payback values differ because customer cohorts start in July; annual interpolation smooths that timing.

Annual net cash flows for years 1–5 are −8,736,000.00; 94,752.00; 9,864,066.05; 22,509,300.96; and 40,067,917.13 KZT. The reviewed BusinessPlan section 8 agrees with the workbook at its stated rounding.

## Scenario checks

The following measures reproduce Sensitivity!G5:J11. Payback in this table is annual interpolation, not monthly-model payback.

| Scenario | NPV, KZT | Discounted BCR | Five-year ROI | Annual payback, years |
| --- | ---: | ---: | ---: | ---: |
| Base | 17,351,748.67 | 1.175364 | 30.9902% | 3.305526 |
| New contracts −25% | −5,960,790.87 | 0.936033 | 4.9569% | 4.580151 |
| Seat price −20% | −4,422,140.22 | 0.955308 | 6.3444% | 4.457971 |
| Operating costs +20% | −817,670.12 | 0.993018 | 9.9846% | 4.240779 |
| Retention 80% | 6,206,677.82 | 1.063710 | 17.8978% | 3.724225 |
| Combined downside | −29,928,480.49 | 0.702009 | −22.0784% | Beyond year 5 |
| New contracts +25% | 40,664,288.21 | 1.388354 | 53.8929% | 2.631249 |

The combined downside means 25% fewer new contracts, 10% lower seat price, 80% retention and 10% higher operating costs. A positive undiscounted ROI can coexist with negative NPV because the latter also reflects the timing of cash and the assumed required return.

## Limitations and interpretation

- These are forecasts, not sales evidence. Prices, volumes, retention, staffing rates and conversion remain planning assumptions.
- ROI uses all project costs in the denominator and covers all five years. It is neither an annual return nor a return on initial equity alone.
- The model is pre-tax and unlevered, with no VAT, income tax, debt service, terminal value or payment delay. It assumes monthly collection and year-end annual discounting.
- Funding capacity of 24.34 million KZT is a base-case result, not a downside guarantee. It already includes the launch outlay; do not add another 8.10 million KZT.
- A supplemental monthly rebuild using the same timing logic gives a combined-downside cash deficit of 46,440,721.72 KZT in month 54, or 53,406,829.98 KZT including a 15% reserve. These are independent audit calculations, not cells in the original workbook. All scenario monthly results are labelled separately in the JSON.
- Inputs!B9, the paid-year fraction, is entered separately from the cohort start month in Inputs!B25. If the month changes, B9 must equal (B24 − B25 + 1) / B24. The existing Indicators!B36 check detects inconsistency. Current inputs are coherent.
- Retention is applied at each calendar-year start, including after a new July cohort's first six months. This is a disclosed simplified convention, not an anniversary-based renewal schedule.
- Scenario operating capacity follows the existing staffing plan while variable service costs scale with customers. The audit does not validate whether that capacity is commercially sufficient.

No current arithmetic correction is required by this review.

## Reproduce the checks

From this folder, run:

python3 Audit_Financial_Model.py > Finance_Audit_Results.json

An optional workbook path may be supplied as the first argument. The script uses only Python's standard library, reads the workbook and prints JSON; it does not edit the workbook. Formula mismatches or evaluation errors produce a non-zero exit status. The JSON contains the input checksum and script checksum. Finance_Audit_SHA256.txt lists the delivered workbook, report, script and result hashes.
