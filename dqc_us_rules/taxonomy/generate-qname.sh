#Generate Taxonomy files

python3 Arelle-master/arellecmdline.py --plugin xule/savexuleqnames --xule-qnames-dir '/Users/campbellpryde/Documents/GitHub/filer_membership/taxonomies/IFRS/2019/' --xule-qnames-format json -f 'https://www.sec.gov/Archives/edgar/data/831609/000106299320003303/cxxif-20200131.xsd'


python3 Arelle-master/arellecmdline.py --plugin xule/savexuleqnames --xule-qnames-dir '/Users/campbellpryde/Documents/GitHub/filer_membership/taxonomies/IFRS/2020/' --xule-qnames-format json -f 'http://xbrl.ifrs.org/taxonomy/2020-03-16/full_ifrs_entry_point_2020-03-16.xsd'


python3 Arelle-master/arellecmdline.py --plugin xule/savexuleqnames --xule-qnames-dir '/Users/campbellpryde/Documents/GitHub/filer_membership/taxonomies/IFRS/2018/' --xule-qnames-format json -f 'http://xbrl.ifrs.org/taxonomy/2018-03-16/full_ifrs_entry_point_2018-03-16.xsd'


python3 Arelle-master/arellecmdline.py --plugin xule/savexuleqnames --xule-qnames-dir '/Users/campbellpryde/Documents/GitHub/filer_membership/taxonomies/2020/' --xule-qnames-format json -f 'http://xbrl.fasb.org/us-gaap/2020/dqcrules/dqcrules-2020-01-31.xsd'

python3 Arelle-master/arellecmdline.py --plugin xule/savexuleqnames --xule-qnames-dir '/Users/campbellpryde/Documents/GitHub/F6-Rules/Form714/taxonomy/' --xule-qnames-format json -f 'https://eCollection.ferc.gov/taxonomy/form714/2020-01-01/form/Form714/form-714_2020-01-01.xsd'