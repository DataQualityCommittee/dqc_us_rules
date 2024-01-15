
###-----------------------------------------------------------------------------------------------------------------------------------------------------------------
# COMPILE RULES
###-----------------------------------------------------------------------------------------------------------------------------------------------------------------

#COMPILE RULES FOR US IN GIT HUB ---

python ~/arelle/Arelle-master/arellecmdline.py --plugins xule --xule-compile /Users/campbellpryde/Documents/GitHub/xule.dqc/dqc_us_rules/source/us/2020/ --xule-rule-set /Users/campbellpryde/Documents/GitHub/xule.dqc/dqc_us_rules/dqc-us-2020-V$1-ruleset.zip --xule-crash  --xule-stack-size=20 --xule-compile-workers=0

python ~/arelle/Arelle-master/arellecmdline.py --plugins xule --xule-compile /Users/campbellpryde/Documents/GitHub/xule.dqc/dqc_us_rules/source/us/2021/ --xule-rule-set /Users/campbellpryde/Documents/GitHub/xule.dqc/dqc_us_rules/dqc-us-2021-V$1-ruleset.zip --xule-crash --xule-stack-size=20 --xule-compile-workers=0

python ~/arelle/Arelle-master/arellecmdline.py --plugins xule --xule-compile /Users/campbellpryde/Documents/GitHub/xule.dqc/dqc_us_rules/source/us/2022/ --xule-rule-set /Users/campbellpryde/Documents/GitHub/xule.dqc/dqc_us_rules/dqc-us-2022-V$1-ruleset.zip --xule-crash --xule-stack-size=20 --xule-compile-workers=0

python ~/arelle/Arelle-master/arellecmdline.py --plugins xule --xule-compile /Users/campbellpryde/Documents/GitHub/xule.dqc/dqc_us_rules/source/us/2023/ --xule-rule-set /Users/campbellpryde/Documents/GitHub/xule.dqc/dqc_us_rules/dqc-us-2023-V$1-ruleset.zip --xule-crash --xule-stack-size=20 --xule-compile-workers=0

python ~/arelle/Arelle-master/arellecmdline.py --plugins xule --xule-compile /Users/campbellpryde/Documents/GitHub/xule.dqc/dqc_us_rules/source/us/2024/ --xule-rule-set /Users/campbellpryde/Documents/GitHub/xule.dqc/dqc_us_rules/dqc-us-2024-V$1-ruleset.zip --xule-crash --xule-stack-size=20 --xule-compile-workers=0

# Add Packages ---

python ~/arelle/Arelle-master/arellecmdline.py --plugins xule --xule-add-packages /Users/campbellpryde/Documents/GitHub/xule.dqc/dqc_us_rules/resources.zip --xule-rule-set  /Users/campbellpryde/Documents/GitHub/xule.dqc/dqc_us_rules/dqc-us-2020-V$1-ruleset.zip

python ~/arelle/Arelle-master/arellecmdline.py --plugins xule --xule-add-packages /Users/campbellpryde/Documents/GitHub/xule.dqc/dqc_us_rules/resources.zip --xule-rule-set  /Users/campbellpryde/Documents/GitHub/xule.dqc/dqc_us_rules/dqc-us-2021-V$1-ruleset.zip 

python ~/arelle/Arelle-master/arellecmdline.py --plugins xule --xule-add-packages /Users/campbellpryde/Documents/GitHub/xule.dqc/dqc_us_rules/resources.zip --xule-rule-set  /Users/campbellpryde/Documents/GitHub/xule.dqc/dqc_us_rules/dqc-us-2022-V$1-ruleset.zip

python ~/arelle/Arelle-master/arellecmdline.py --plugins xule --xule-add-packages /Users/campbellpryde/Documents/GitHub/xule.dqc/dqc_us_rules/resources.zip --xule-rule-set  /Users/campbellpryde/Documents/GitHub/xule.dqc/dqc_us_rules/dqc-us-2023-V$1-ruleset.zip 

python ~/arelle/Arelle-master/arellecmdline.py --plugins xule --xule-add-packages /Users/campbellpryde/Documents/GitHub/xule.dqc/dqc_us_rules/resources.zip --xule-rule-set  /Users/campbellpryde/Documents/GitHub/xule.dqc/dqc_us_rules/dqc-us-2024-V$1-ruleset.zip 


# COMPILE RULES FOR IFRS --- IN GIT HUB

python ~/arelle/Arelle-master/arellecmdline.py --plugins xule --xule-compile /Users/campbellpryde/Documents/GitHub/xule.dqc/dqc_us_rules/source/ifrs/2020/ --xule-rule-set /Users/campbellpryde/Documents/GitHub/xule.dqc/dqc_us_rules/dqc-ifrs-2020-V$1-ruleset.zip --xule-crash --xule-stack-size=20 --xule-compile-workers=0

python ~/arelle/Arelle-master/arellecmdline.py --plugins xule --xule-compile /Users/campbellpryde/Documents/GitHub/xule.dqc/dqc_us_rules/source/ifrs/2021/ --xule-rule-set /Users/campbellpryde/Documents/GitHub/xule.dqc/dqc_us_rules/dqc-ifrs-2021-V$1-ruleset.zip --xule-crash --xule-stack-size=20 --xule-compile-workers=0

python ~/arelle/Arelle-master/arellecmdline.py --plugins xule --xule-compile /Users/campbellpryde/Documents/GitHub/xule.dqc/dqc_us_rules/source/ifrs/2022/ --xule-rule-set /Users/campbellpryde/Documents/GitHub/xule.dqc/dqc_us_rules/dqc-ifrs-2022-V$1-ruleset.zip --xule-crash --xule-stack-size=20 --xule-compile-workers=0

python ~/arelle/Arelle-master/arellecmdline.py --plugins xule --xule-compile /Users/campbellpryde/Documents/GitHub/xule.dqc/dqc_us_rules/source/ifrs/2023/ --xule-rule-set /Users/campbellpryde/Documents/GitHub/xule.dqc/dqc_us_rules/dqc-ifrs-2023-V$1-ruleset.zip --xule-crash --xule-stack-size=20 --xule-compile-workers=0

# Add Packages IFRS ---

python ~/arelle/Arelle-master/arellecmdline.py --plugins xule --xule-add-packages /Users/campbellpryde/Documents/GitHub/xule.dqc/dqc_us_rules/resources.zip --xule-rule-set  /Users/campbellpryde/Documents/GitHub/xule.dqc/dqc_us_rules/dqc-ifrs-2020-V$1-ruleset.zip

python ~/arelle/Arelle-master/arellecmdline.py --plugins xule --xule-add-packages /Users/campbellpryde/Documents/GitHub/xule.dqc/dqc_us_rules/resources.zip --xule-rule-set  /Users/campbellpryde/Documents/GitHub/xule.dqc/dqc_us_rules/dqc-ifrs-2021-V$1-ruleset.zip

python ~/arelle/Arelle-master/arellecmdline.py --plugins xule --xule-add-packages /Users/campbellpryde/Documents/GitHub/xule.dqc/dqc_us_rules/resources.zip --xule-rule-set  /Users/campbellpryde/Documents/GitHub/xule.dqc/dqc_us_rules/dqc-ifrs-2022-V$1-ruleset.zip

python ~/arelle/Arelle-master/arellecmdline.py --plugins xule --xule-add-packages /Users/campbellpryde/Documents/GitHub/xule.dqc/dqc_us_rules/resources.zip --xule-rule-set  /Users/campbellpryde/Documents/GitHub/xule.dqc/dqc_us_rules/dqc-ifrs-2023-V$1-ruleset.zip 

# COMPILE RULES FOR ESEF --- IN GIT HUB

python ~/arelle/Arelle-master/arellecmdline.py --plugins xule --xule-compile /Users/campbellpryde/Documents/GitHub/xule.dqc/dqc_us_rules/source/esef/esef-2022/ --xule-rule-set /Users/campbellpryde/Documents/GitHub/xule.dqc/dqc_us_rules/dqc-esef-2022-V$1-ruleset.zip --xule-crash --xule-stack-size=20 --xule-compile-workers=0

python ~/arelle/Arelle-master/arellecmdline.py --plugins xule --xule-compile /Users/campbellpryde/Documents/GitHub/xule.dqc/dqc_us_rules/source/esef/esef-2021/ --xule-rule-set /Users/campbellpryde/Documents/GitHub/xule.dqc/dqc_us_rules/dqc-esef-2021-V$1-ruleset.zip --xule-crash --xule-stack-size=20 --xule-compile-workers=0

python ~/arelle/Arelle-master/arellecmdline.py --plugins xule --xule-compile /Users/campbellpryde/Documents/GitHub/xule.dqc/dqc_us_rules/source/esef/esef-2020/ --xule-rule-set /Users/campbellpryde/Documents/GitHub/xule.dqc/dqc_us_rules/dqc-esef-2020-V$1-ruleset.zip --xule-crash --xule-stack-size=20 --xule-compile-workers=0