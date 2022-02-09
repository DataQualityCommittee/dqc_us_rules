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

