select * 
from xuscc.cc_list_report
where true
and run_date > '2022-02-07'
and error_code = 'xule:error'
limit 3

select count(*)
from xuscc.cc_list_report
where true
and run_date > '2022-02-08'


select * 
from xuscc.cc_list_report
where true
and run_date > '2021-02-07'
and error_code = 'DQC.IFRS.0104.9554'
limit 3

select r.* 
from dts_relationship r 
join element ef ON r.from_element_id = ef.element_id
join element et ON r.to_element_id = et.element_id
join qname qf ON qf.qname_id = ef.qname_id
join qname qt ON qt.qname_id = et.qname_id
where qf.local_name = 'TreasuryStockValue'
and qt.local_name = 'TreasuryStockCommonValue' 


