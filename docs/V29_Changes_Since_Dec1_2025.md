# DQC US Rules V29 — Changes Since December 1, 2025

This document summarises all changes made to the V29 DQC US GAAP rules since December 1, 2025. Changes apply across taxonomy years 2022–2026 unless otherwise noted. The document is organised by rule number.

---

## New Rules

### DQC_0234 — Income Tax Authority Axis Validation *(2026 only)*

**Added:** February 3, 2026

Three new assertions (US.0234.10928, US.0234.10929, US.0234.10930) were added to detect improper use of `IncomeTaxAuthorityAxis` and missing `TaxJurisdictionOfDomicileExtensibleEnumeration`. Each assertion defines concept lists, constructs error messages, and sets severity and effective date. 

> **Note:** These rules are currently disabled (pending migration to V30).

---

### DQC_0235 — Collateral Axis Rules *(2026 only)*

**Added:** February 13, 2026

Two new assertions (US.0235.10931 and US.0235.10932) detect use of `CollateralAxis` with specific concepts:
- `FinancialAssetsSoldUnderAgreementsToRepurchaseGrossIncludingNotSubjectToMasterNettingArrangement`
- `SecuritiesLoanedIncludingNotSubjectToMasterNettingArrangementAndAssetsOtherThanSecuritiesTransferred`

The rules recommend using `CollateralPledgedInSecuredBorrowingAxis` for disaggregation instead.

> **Note:** These rules are currently disabled (pending migration to V30).

---

## Removed Rules

### DQC_0205 — Balance Sheet Location Axis Validation *(Removed)*

**Removed:** December 15, 2025

The `DQC_0205.xule` rule files were deleted across all taxonomy years (2022–2026). This rule previously validated use of `BalanceSheetLocationAxis`.

---

### DQC_0229 — Multiple "Other" Concepts in Calculation Network *(Removed)*

**Removed:** December 10, 2025

The `DQC_0229.xule` rule files and associated documentation were removed for all years (2022–2025). This rule was removed due to duplication with DQC_0230, which covers the same validation scope.

---

## Modified Rules

### DQC_0087 — Lease Liability Reporting

**Modified:** March 5, 2026

- Added reporting-period filtering: facts with `fact.period.end < $ReportingPeriod - P1Y3M` are now ignored, preventing stale/historical lease facts from triggering the rule.
- Expanded the accepted `DocumentType` set to include amended and alternate form variants (e.g. `10-K/A`, `20-F/A`, `40-F/A`).
- Applied to checks for `OperatingLeaseLiability`, `OperatingLeaseLiabilityCurrent`, `OperatingLeaseLiabilityNoncurrent`, and statement-of-financial-position variants.

---

### DQC_0121 — Remaining Rule Retired *(2026 only)*

**Modified:** February 13, 2026

The remaining portion of rule 121 was commented out and removed from the 2026 taxonomy rule file. No assertions remain active in DQC_0121 for 2026.

---

### DQC_0124 — Missing Disaggregated Revenue Elements

**Modified:** March 5, 2026

- Added historical-period filtering: introduced `$ReportingPeriod` and `$PeriodToIgnore = $ReportingPeriod - P1Y3M`, restricting checks to facts with `fact.period.end >= $PeriodToIgnore`.
- Broadened the accepted `DocumentType` set to include amended/alternative forms (e.g. `10-K/A`, `20-F/A`, `40-F/A`).

---

### DQC_0135 — Dimensional Equivalents (Income Statement)

**Modified:** March 5, 2026

- Added reporting-period logic introducing `$InstantPeriodToIgnore` and `$DurationPeriodToIgnore` thresholds; facts outside the financial statements' coverage window are excluded.
- Added exclusions for `@@RestructuringCostAndReserveAxis` and `@@srt:ProductOrServiceAxis` in income-statement checks to prevent over-mapping.
- Expanded accepted `DocumentType` values.
- Minor message spacing fixes.

---

### DQC_0187 — Property Plant and Equipment Components

**Modified:** February 13, 2026

Replaced the strict arithmetic comparison (`$ppe_gross < $ppe_Gross_dim_components_sum`) with a `tolerance_for_decimals_greater_than(...)` check using `ppe_gross.decimals` with a tolerance of `2`. This accounts for rounding and decimal precision differences when comparing `PropertyPlantAndEquipmentGross` to the aggregated dimensional components, reducing false positives.

---

### DQC_0190 — Employee Benefit Plan Reporting

**Modified:** Multiple dates (December 2025 – March 2026)

Several significant changes were made across multiple commits:

1. **Rule-focus added** (February 13, 2026): Added explicit `rule-focus` statements to all rule blocks in the 2024, 2025, and 2026 files to make evaluation context explicit.

2. **LegalEntityAxis member handling refactored** (February 23, 2026): Replaced covered-fact filtering with a taxonomy `navigate` approach to retrieve `LegalEntityAxis` members. The logic now iterates over `.local-name`, skips `EntityDomain`, and uses refined `regex-match` check branching. The old approach is preserved as a commented block.

3. **Rule 5 removed** (March 6, 2026): The FASB/Rule 5 assertion and related rule block were commented out in the 2024, 2025, and 2026 files following a decision to remove Rule 5 (per discussion with S. Wavrin and S. Jablonski). Explanatory comments were added in the 2026 file about excluding the legal-entity axis that represents totals to avoid false positives.

---

### DQC_0195 — Retained Earnings and Dividends

**Modified:** March 6, 2026

Added a treasury-stock exception to suppress the rule when a retained earnings increase is driven by a gain on treasury stock paired with a corresponding reduction in treasury stock. The change:

- Adds a `$TreasuryStock` existence check against `TreasuryStockCommonMember`.
- Defines an exception list: `StockIssuedDuringPeriodValueEmployeeBenefitPlan` and `StockIssuedDuringPeriodValueShareBasedCompensation`.
- When both conditions match the rule short-circuits (`returns false`) to avoid false positives.

---

### DQC_0197 — Income Statement Concepts (Preferred Stock Grouping)

**Modified:** February 18, 2026 *(2024, 2025, 2026 only)*

Fixed incorrect grouping logic for preferred stock items. `$Pref_stock_items` are now added to `$INCOME_STATEMENT_CONCEPTS` before subtracting `$Pref_stock_items_allowed`. Previously the subtraction was applied only to `$Pref_stock_items` in isolation, which could produce incorrect membership in `$income_statement_items`.

---

### DQC_0198 — Effective Tax Rate

**Modified:** Multiple dates (December 2025 – March 6, 2026)

This rule underwent the most extensive revision in the period, across five separate commits:

1. **Period end date filter added** (December 2025): Added a `fact.period.end` filter to the tax-check scope.

2. **EGC/REIT detection and tax-network checks** (February 10, 2026): Added new constants `$INCOME_TAX_STRUCTURE_ELEMENTS`, `$INCOME_TAX_NETWORKS`, `$REIT_IDENTIFIER_ELEMENTS`, and `$REIT_NETWORKS`. Introduced an EGC exemption flag (`$EGCFlag`) and required not `$EGCFlag` plus presence of an income-tax network before enforcing equivalent-tax-rate checks in 10-Ks. Equivalent-rate calculations are skipped for identified REIT networks. The conflicting assertion `US.0198.10661` (IncomeTaxAuthorityAxis vs TaxJurisdictionOfDomicileExtensibleEnumeration) was removed and replaced with a comment noting removal per FASB guidance.

3. **Zero tax fact filtering** (February 13, 2026): Added `and $fact != 0` to existence predicates for equivalent tax-rate concepts, preventing the rule from firing when the reported tax amount is zero.

4. **EGC logic adjusted for 2025/2026** (February 13, 2026): For 2025 and 2026 rule variants, the EGC flag logic was changed so filers with `DocumentPeriodEndDate >= 2026-12-15` are treated as non-EGC (`false`) for this rule.

5. **Network filtering and NCI logic** (March 5, 2026): Introduced `$NETWORK_TAX_CONCEPTS` to limit equivalent-tax-rate checks to concepts present in income-tax presentation networks. Required `fact.period.days > 350` when validating network facts. Added an alternative NCI-adjustment calculation and messaging (`RegularMessage` / `NCI_Message`) to handle filings where effective tax rates are calculated after deducting non-controlling interest, gated by `$NCI_ADJUSTMENT_NOT_VALID`.

6. **Nonils predicate** (February 13, 2026): Added the `nonils` predicate to existence checks for equivalent tax rate concepts so nil-valued facts are not considered present when validating paired percentage/amount facts. *(Applied to 2022–2025 files.)*

7. **Bracketed fact selectors** (December 2025): Updated to use bracketed fact selectors throughout.

---

### DQC_0214 — Equity Items on Balance Sheet

**Modified:** January 20, 2026 and January 20, 2026

Two changes were made in close succession:

1. **Refined 10-Q vs 10-K handling** (January 20, 2026): Updated to distinguish error handling between `10-K` and `10-Q` filings. For `10-Q`, the rule now checks if items are in the equity presentation network or are material relative to total assets before raising an error.

2. **Simplified equity check and added AOCI guidance** (January 20, 2026): Removed the conditional logic based on filing type and `$TotalAssets` introduced in the previous commit and added an additional message referencing the FASB implementation guide for Accumulated Other Comprehensive Income (`AOCI`) when applicable.

---

### DQC_0221 — Segment Reporting Disclosure

**Modified:** December 3, 2025 and January 13, 2026

1. **Expanded reportable flag check** (December 3, 2025 — 2022–2025): Added `NumberOfReportableSegmentsDisclosedByDefinition` to the reportable flag check so either extension concept can satisfy the rule when `NumberOfReportableSegments` is not reported.

2. **Corrected flag name** (January 13, 2026 — 2022–2026): Replaced `NumberOfReportableSegmentsDisclosedByDefinition` with `NumberOfReportableSegmentsDisclosedByDefinitionFlag` in both logic and error messages to reference the correct extension concept name.

---

### DQC_0222 — Inconsistent Disclosure of Public Float

**Modified:** March 5, 2026 (threshold) and February 6, 2026 (small-filer logic)

1. **Public float threshold raised to 2.5B** (March 5, 2026): Updated the upper bound threshold from `250,000,000` to `2,500,000,000`. This adjusts the conditional logic that evaluates public float vs. revenue so that larger public float values are handled by the rule.

2. **Small-filer revenue exception added** (February 6, 2026): Extended the rule to account for small-filer exceptions based on revenue. Adds sets of revenue concepts (including financial-services revenue), computes `revenue_facts` for the small-filer period, and implements a conditional: if revenue is less than `$100M` and public float is between `$250M` and `$700M`, the scaling-error flag for `EntityPublicFloat` is suppressed. Also adds `rule-focus` on the public float fact.

---

### DQC_0226 — US GAAP Taxonomy Detection

**Modified:** February 18, 2026 *(2024, 2025, 2026 only)*

Replaced the prior taxonomy concept name intersection with a fact-driven approach:

- Collects covered facts for US-GAAP concepts into `$factValues`.
- Derives the top-10 concept names from those facts.
- Checks presence by `$factValues.length`.

This more reliably detects US-GAAP elements actually used in the filing rather than relying solely on taxonomy concept lists.

---

### DQC_0227 — Extensible Enumerations (Scale Check)

**Modified:** February 10, 2026

Added a `perShareItemTolerance` of `0.01` for concepts with datatype `dtr-types:perShareItemType`. The interval comparison checks (`greaterThanLowerBound` and `lessThanUpperBound`) now add/subtract this tolerance, so per-share rounding differences are tolerated and do not produce false positives.

---

### DQC_0228 — Calculation Consistency

**Modified:** December 2025 onwards

Multiple updates to refine equality logic for calculation comparisons. Adjustments were made to how values are compared, including improvements to whitespace handling and edge-case equality checks. *(Multiple small commits across the period.)*

---

### DQC_0230 — Missing Calculation for "Other" Items

**Modified:** Multiple dates (December 3, 2025 – February 13, 2026)

This rule received several expansions to broaden missing-calculation detection:

1. **Added receivables and interest** (December 3, 2025): Added `AccountsAndOtherReceivablesNetCurrent` and `InterestExpenseOther` to the calculation network logic. Updated message text to clarify that calculated concepts should only have "other" concepts that can comprise them.

2. **Expanded intersection set** (February 6, 2026): Replaced the previous OR check for `AccountsAndOtherReceivablesNetCurrent` and `InterestExpenseOther` with a set intersection that also includes `InvestmentsAndOtherNoncurrentAssets` and `PrepaidExpenseAndOtherAssetsCurrent`, detecting when these concepts are present in `$unallowedOtherUsedInNetwork`.

3. **Added PropertyPlantAndEquipmentOtherNet** (February 10, 2026): Added `PropertyPlantAndEquipmentOtherNet` to the set of items checked for missing calculations across all years (2022–2026).

4. **Added disposal-group items** (February 13, 2026): Added three `DisposalGroupIncludingDiscontinuedOperation` asset concepts to `$missingCalculationForItem`:
   - `DisposalGroupIncludingDiscontinuedOperationOtherCurrentAssets`
   - `DisposalGroupIncludingDiscontinuedOperationOtherNoncurrentAssets`
   - `DisposalGroupIncludingDiscontinuedOperationPrepaidAndOtherAssetsCurrent`

---

## Infrastructure / Cross-Cutting Changes

### Rule-Focus Directives Added

**Added:** December 2025 – March 2026

`rule-focus` statements were added to multiple rule files to make evaluation context explicit and avoid relying on implicit/default focus behaviour. Rules updated include:

| Rule | Dates Applied | Years |
|------|--------------|-------|
| DQC_0004 | December 2025 | 2022–2026 |
| DQC_0015 | December 2025 | 2022–2025 |
| DQC_0084 | December 2025 | 2025–2026 |
| DQC_0108 | December 2025 | Various |
| DQC_0120 | December 2025 | Various (removed from some files) |
| DQC_0139 | December 2025 | Various |
| DQC_0150 | December 2025 | 2022–2025 |
| DQC_0190 | February 13, 2026 | 2024–2026 |
| DQC_0198 | December 2025 | Various |

---

### FILIN_COMPONENTS_OF_NET_INC_LOSS Constant Relocated

**Modified:** March 6, 2026 *(2023–2026)*

The `FILIN_COMPONENTS_OF_NET_INC_LOSS` constant was moved from the per-taxonomy `constant-us-gaap.xule` files into the shared `constant.xule` files for 2023–2026. The definition navigates `parent-child` descendants from `IncomeStatementAbstract` / `StatementOfIncomeAndComprehensiveIncomeAbstract` where the target is a monetary concept.

---

### 2026 US GAAP Taxonomy — New Rule Files Added

**Added:** December 2025

A complete set of rule files for the 2026 US GAAP taxonomy was added, porting all existing rules forward and adding 2026-specific axis/member and concept references. The 2026 ruleset ZIP (`dqc-us-2026-V29-ruleset.zip`) was produced and iterated throughout the period.

---

### Ruleset ZIP Files Updated

The V29 ruleset ZIP files for all years (2022–2026) were refreshed multiple times throughout the period as rule changes were compiled and packaged.

---

*© Copyright 2016 – 2026, XBRL US, Inc. All rights reserved.*
