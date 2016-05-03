# Amendments to existing rule DQC_0015
## Member Exclusions

In certain cases negative values associated with a line item will not indicate an error.  This occurs when certain members or axes are used which indicate a reversal of an account. Rule DQC_0015 included a list of these members, axes,  and a list of text matches that could be performed to identify such cases.  With the rollout of the rule a number of additions and/or changes to the exclusion list have been identified

Change “Reconciliat” TO “Reconcili”
Add the axis ErrorCorrectionsAndPriorPeriodAdjustmentsRestatementByRestatementPeriodAndAmountAxis
Add the Axis AdjustmentsForChangeInAccountingPrincipleAxis
Add the Axis AdjustmentsForNewAccountingPronouncementsAxis
Add the Axis ProspectiveAdoptionOfNewAccountingPronouncementsAxis
Add the axis QuantifyingMisstatementInCurrentYearFinancialStatementsByNatureOfErrorAxis
Add the Member SubsidiaryIssuerMember to the Legal Entity Axis


## Line Items

The line item element is currently identified as being unable to be entered as a negative value.
AllocatedShareBasedCompensationExpense (Allocated Share-based Compensation Expense)
ExcessTaxBenefitFromShareBasedCompensationFinancingActivities
InterestCreditedToPolicyOwnerAccounts (Element has incorrect balance type)
PaymentsForProceedsFromFederalReserveBankStock
NoncashOrPartNoncashAcquisitionNetNonmonetaryAssetsAcquiredLiabilitiesAssumed1 (This element was originally added as it ws believed a company would assume more liabilities than assets, however the non cash portions may differ so this is possible)


1This line item can be negative when management increases its estimated employee forfeiture rate in a given year. see FASB 718-20-55-15
