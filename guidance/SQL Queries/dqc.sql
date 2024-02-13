select * from xuscc.cc_list_report
where run_date > '2024-02-10 12:38:09'
--and error_source = 'DQC'
--and error_source = 'xule:error'
--and detail not ilike '%DQC.US.0177.1013%'
--and detail not ilike '%DQC.US.0178.10142%'
--and detail not ilike '%DQC.IFRS.0176.10119%'
--and detail not ilike '%DQC.IFRS.0176.10118%'
--and detail not ilike '%DQC.IFRS.0167.10105%'
--and detail not ilike '%DQC.US.0178.10137%'
--and error_code = 'DQC.US.0179.10153'
and error_code = 'DQC.US.0185.10165'
--limit 10


select 
(get_simple_fact_by_accession('dei','EntityFilerCategory',r.report_id, 'text'::character varying))::varchar,
(get_simple_fact_by_accession('dei','EntitySmallBusiness',r.report_id, 'text'::character varying)),
*
from report r
where  r.properties ->> 'document_type'::text  = '20-F'
and r.properties ->> 'filing_date'::text  > '01-01-2023'
and (get_simple_fact_by_accession('dei','EntityFilerCategory',r.report_id, 'text'::character varying)) is null
order by report_id desc
limit 10



select * from fact
where element_local_name = 'DividendsDeclaredTableTextBlock'
and accession_id = '553562'
limit 10

select * from report
where source_report_identifier = '0001437749-23-004919'
limit 10