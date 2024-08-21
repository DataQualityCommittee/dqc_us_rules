-- Identify use of the new calculation linkbase in prod

select * 
	from dts_network n
	join report r on r.dts_id = n.dts_id
where n.arcrole_uri_id = 7326229
limit 10

-- Identify uri id

select * from uri where uri ='https://xbrl.org/2023/arcrole/summation-item'

-- Get Common stock member negatives

select r.entity_name, r.entry_url, r.creation_software, f.fact_id, accession_id, effective_value, element_namespace, element_local_name, dimension_count 
from fact f
	join context_dimension_explicit cde on f.context_id = cde.context_id
	join report r on r.report_id = f.accession_id
where f.element_local_name in ('SharesOutstanding', 
                                    'CommonStockSharesOutstanding', 
                                    'StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest',
                                    'StockIssuedDuringPeriodValueNewIssues',
                                    'StockIssuedDuringPeriodSharesNewIssues',
                                    'StockIssuedDuringPeriodValueIssuedForServices',
                                    'StockIssuedDuringPeriodSharesIssuedForServices',
                                    'StockGrantedDuringPeriodValueSharebasedCompensationGross',
                                    'StockGrantedDuringPeriodValueSharebasedCompensationForfeited',
                                    'StockGrantedDuringPeriodValueSharebasedCompensation',
	'ShareBasedCompensationArrangementByShareBasedPaymentAwardOptionsGrantsInPeriodGross',
                                    'ShareBasedCompensationArrangementByShareBasedPaymentAwardOptionsForfeituresInPeriod',
                                    'ShareBasedCompensationArrangementByShareBasedPaymentAwardOptionsGrantsInPeriod',
                                    'StockIssuedDuringPeriodValueShareBasedCompensationGross',
                                    'StockIssuedDuringPeriodValueShareBasedCompensationForfeited',
                                    'StockIssuedDuringPeriodValueShareBasedCompensation',
                                    'StockIssuedDuringPeriodSharesShareBasedCompensationGross',
                                    'StockIssuedDuringPeriodSharesShareBasedCompensationForfeited',
                                    'StockIssuedDuringPeriodSharesShareBasedCompensation',
                                    'StockIssuedDuringPeriodValueRestrictedStockAwardGross',
                                    'StockIssuedDuringPeriodValueRestrictedStockAwardForfeitures',
                                    'StockIssuedDuringPeriodValueRestrictedStockAwardNetOfForfeitures',
                                    'StockIssuedDuringPeriodSharesRestrictedStockAwardGross',
                                    'StockIssuedDuringPeriodSharesRestrictedStockAwardForfeited',
                                    'StockIssuedDuringPeriodSharesRestrictedStockAwardNetOfForfeitures',
                                    'StockIssuedDuringPeriodValueStockOptionsExercised',
                                    'StockIssuedDuringPeriodSharesStockOptionsExercised',
                                    'StockIssuedDuringPeriodValueEmployeeStockOwnershipPlan',
                                    'StockIssuedDuringPeriodSharesEmployeeStockOwnershipPlan',
                                    'StockIssuedDuringPeriodValueEmployeeStockPurchasePlan',
                                    'StockIssuedDuringPeriodSharesEmployeeStockPurchasePlans',
                                    'StockIssuedDuringPeriodValueEmployeeBenefitPlan',
                                    'StockIssuedDuringPeriodSharesEmployeeBenefitPlan',
                                    'StockIssuedDuringPeriodValueAcquisitions',
                                    'StockIssuedDuringPeriodSharesAcquisitions',
                                    'StockIssuedDuringPeriodValueConversionOfConvertibleSecurities',
                                    'StockIssuedDuringPeriodSharesConversionOfConvertibleSecurities',
                                    'StockIssuedDuringPeriodValueConversionOfConvertibleSecuritiesNetOfAdjustments',
                                    'StockIssuedDuringPeriodValueConversionOfUnits',
                                    'StockIssuedDuringPeriodSharesConversionOfUnits',
                                    'StockIssuedDuringPeriodValueStockDividend',
                                    'CommonStockDividendsShares',
                                    'StockDividendsShares',
                                    'StockIssuedDuringPeriodValueDividendReinvestmentPlan',
                                    'StockIssuedDuringPeriodSharesDividendReinvestmentPlan',
                                    'StockIssuedDuringPeriodValuePurchaseOfAssets',
                                    'StockIssuedDuringPeriodSharesPurchaseOfAssets',
                                    'StockIssuedDuringPeriodValueOther',
                                    'StockIssuedDuringPeriodSharesOther',
                                    'StockIssuedDuringPeriodSharesStockSplits',
                                    'StockIssuedDuringPeriodSharesReverseStockSplits', 
                                    'StockRepurchasedAndRetiredDuringPeriodValue',
                                    'StockRepurchasedAndRetiredDuringPeriodShares',
                                    'StockRepurchasedDuringPeriodValue',
                                    'StockRepurchasedDuringPeriodShares',
                                    'StockRedeemedOrCalledDuringPeriodValue',
                                    'StockRedeemedOrCalledDuringPeriodShares',
                                    'TreasuryStockRetiredParValueMethodAmount',
                                    'TreasuryStockRetiredCostMethodAmount',
                                    'TreasuryStockSharesRetired',
                                    'AmortizationOfESOPAward')
	and member_local_name = 'CommonStockMember'
	and f.effective_value < 0
	and f.dimension_count > 0
	and f.element_namespace in ('http://fasb.org/us-gaap/2023','http://fasb.org/us-gaap/2024')
	limit 10