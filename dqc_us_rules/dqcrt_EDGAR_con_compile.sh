# !/bin/bash
#
# build DQCRT ruleset for EDGAR
#
REPOS_DIR=/Users/hermf/temp/plugin/DQC
ARELLE_DIR=/Users/hermf/Documents/projects/Arelle/ArelleProject/edgrXule
ARELLE_XULE_RESOURCES_DIR=${ARELLE_DIR}/arelle/plugin/EDGAR/validate/resources/xule
CACHE_DIR=/Users/hermf/Library/Caches/Arelle
for yr in 2023 2024 2025
do
  # for source_dir from hermfischer-wf git use this
  SOURCE_DIR="${REPOS_DIR}/dqc_us_rules/dqc_us_rules/source"
  # for source_dir from https://github.com/davidtauriello/dqc_us_rules/tree/v26-hf-con/
  #SOURCE_DIR="${REPOS_DIR}/dqc_us_rules-26-hf-con-reorg/dqc_us_rules/source"
  echo Source dir for build $SOURCE_DIR
  
  TEMP_DIR="${REPOS_DIR}/DQCRT"
  SRC_CAL="${CACHE_DIR}/https/xbrl.fasb.org/us-gaap/${yr}"
  DEST_CALC="${REPOS_DIR}/us-gaap-cal-${yr}-all.xsd"
  DEST_ZIP="${REPOS_DIR}/dqcrt-us-${yr}-ruleset.zip"
  DEST_CONSTS="${REPOS_DIR}/dqcrt-us-${yr}-constants.json"
  rm -fr ${TEMP_DIR} ${DEST_ZIP} ${DEST_CALC}
  mkdir ${TEMP_DIR}
  
  cat > ${DEST_CALC} << EOF
<?xml version='1.0' encoding='UTF-8'?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
<xs:annotation>
<xs:appinfo>
EOF
  find ${SRC_CAL} -name \*cal\*xml -exec cat {} >> ${TEMP_DIR}/temp.xsd \;
  sed -e '/xml version=/d' -e "/\.\.\/elts.us-/s//https:\/\/xbrl.fasb.org\/us-gaap\/${yr}\/elts\/us-/g" ${TEMP_DIR}/temp.xsd >> ${DEST_CALC}
  cat >> ${DEST_CALC} << EOF
</xs:appinfo>
</xs:annotation>
</xs:schema>
EOF
  rm ${TEMP_DIR}/temp.xsd

  for f in ${SOURCE_DIR}/us/${yr}/[a-z]*.xule
  do
    cp -p ${f} ${TEMP_DIR}
  done
  echo ls buildConstants 

  # compile the rule set
  echo Compiling ${yr} rule set for build_constants
  python3.12 ${ARELLE_DIR}/arelleCmdLine.py --plugins xule --xule-arg RESOURCES_DIR=${REPOS_DIR}/ --xule-compile ${TEMP_DIR} --xule-rule-set ${DEST_ZIP} --xule-crash

  # output constants file, needs a sample instance for  $DEI-NAMESPACE determination
  echo Output constants file
  python3.12 ${ARELLE_DIR}/arelleCmdLine.py --plugin xule --xule-arg RESOURCES_DIR=${REPOS_DIR}/ --xule-rule-set ${DEST_ZIP}  --xule-output-constants "ACCRUAL_ITEMS,CALC_RELATIONSHIPS,MEMBER_USGAAP_FAIR_VALUE,CALC_NETWORKS,DEP_CONCEPTS,DEFINED_BENEFIT_COST_EXT_ENUM,DEFINED_BENEFIT_COST_FS_LINE_ITEMS,DERIVATIVE_LIABILITIES_FS_LINE_ITEMS,DERIVATIVE_ASSETS_FS_LINE_ITEMS,OCI_SECURITY_RELATED_ITEMS,LIQUIDATION_BASIS_CONCEPTS,TAXONOMY_DEFAULTS,NONALLOWED_ROOT_ELEMENTS_CASHFLOW,NETWORK_730000_TARGET_NON_ABSTRACT_QNAMES,ASU201517_TRANSITION_ELEMENTS,MBR_RECL_OUT_ACCUM_CMP_INC_AXS,MEM_LEG_ENT_AXS,MEM_FHLB_AXS,MBR_SCH_EQT_INV_NM_AXS,MBR_PLN_NM_AXS,MEM_DEF_CNT_PLN_NM_AXS,MEM_RNG_AXS,MEM_SRT_CUR_AXS,MEM_CUR_AXS,MEM_POS_AXS,MEM_FAR_VAL_MSR_FRQ_AXS,MEM_FAR_VAL_MSR_BAS_AXS,DEF_FAR_VAL_MSR_BAS_AXS,MEM_HDG_DSG_AXS,MEM_PRD_SVC_AXS,MEM_AIR_TP_AXS,MEM_SCH_MPR_INS_AXS,MEM_PPE_TP_AXS,MEM_RSV_QTY_RSV_AXS,MEM_PUB_UTL_INV_AXS,MEM_CON_ITM_AXS,MEM_NOT_ALLOWED_RET_TREE,MEM_AWD_DT_AXS,MEM_SUB_EVT_AXS,MBR_STM_EQY_CMP_AXS,MBR_STM_CLS_STK_AXS,MBR_STM_SCN_AXS,MBR_PRF_UNT_NM_AXS,MBR_RET_PLN_NM_AXS,MBR_OWNRSHP_AXS,MBR_MAJ_CST_AXS,MBR_BUS_ACQ_AXS,MBR_STM_BIS_SEG_AXS,MBR_AST_ACQ_AXS,MBR_STM_GEO_AXS,FINANCIAL_DATA_EQUITY_METHOD_INVESTMENTS,NCI,NON_FINANCIAL_DATA_EMI,EXT_ENUM,IDENTIFICATION,EXCLUDE_NON_NEG_STRING_MEMBERS,EXCLUDE_NON_NEG_MEMBERS,EXCLUDE_NON_NEG_AXIS_MEMBERS_PRE,EXCLUDE_NON_NEG_AXIS_MEMBERS,EXCLUDE_NON_NEG_AXIS,effective_dates,NON_NEG_ITEMS,DIM_EQUIVALENTS,EXTENSION_ITEMS,ELEMENTS_EXCLUDED_FROM_RULE,CHILD_ELEMENTS_PROMOTABLE_TO_SIBLING_OF_PARENT_ELEMENT,SIBLINGS_DEMOTABLE_TO_CHILD,CHILD_ELEMENTS_PROMOTABLE_TO_SIBLING,PARENT_ELEMENTS_WITH_CHILDREN_PROMOTABLE_TO_SIBLING,SIBLING_ELEMENTS_WITH_SIBLINGS_DEMOTABLE_TO_DESCENDANT,MATURITY_SCHEDULE_ELEMENTS,MESSAGE_FOR_RULE_9277,MESSAGE_FOR_RULE_9278,NON_CF_ITEMS,SET_NON_CF_ABSTRACTS1,SSH_EXCEPTIONS,ASSET_TYPES,SET_CONCENTRATION_RISK_ITEMS,SET_BENCHMARK_ITEMS" --xule-output-constants-file ${DEST_CONSTS}

  rm -fr ${TEMP_DIR} ${DEST_ZIP}
  mkdir ${TEMP_DIR}

  #
  #for f in 0001 0004 0005 0006 0008 0009 0013 0014 0015 0033 0036 0041 0043 0044 0045 0046 0047 0048 0051 0052 0053 0054 0055 0057  0060  0061 0062_2017 0065 0068 0069 0070 0071  0072 0073  0076 0077 0078 0079  0081 0084  0085 0089 0090 0091 0094 0116 0117 0121 0122 0123 0126 0127 0128 0133 0134 0135 0136 0137 0141
  #for f in 0041 0045 0068 0133
  for f in 0001 0004 0005 0006 0008 0009 0013 0014 0015 0033 0036 0041 0043 0044 0045 0046 0047 0048 0051 0052 0053 0054 0055 0057  0060  0061 0062_2017 0065 0068 0069 0070 0071  0072 0073  0076 0077 0078 0079  0084  0085 0089 0090 0091 0095 0098 0099 0108 0109 0112 0118 0119 0123 0126 0128 0133 0134 0135 0136 0137 0141  
  do
    # uncomment to use prefix DQC without changing to DQCRT
    cp -p ${SOURCE_DIR}/us/${yr}/DQC_${f}.xule ${TEMP_DIR}
    # uncomment to change prefix from DQC to DQCRT
    # sed -e '/rule-name-prefix DQC/Is//rule-name-prefix DQCRT/g' ${SOURCE_DIR}/us/${yr}/DQC_${f}.xule > ${TEMP_DIR}/DQC_${f}.xule 
  done

  for f in ${SOURCE_DIR}/us/${yr}/[a-z]*.xule ${SOURCE_DIR}/lib/*.xule
  do
    cp -p ${f} ${TEMP_DIR}
  done

  # compile the rule set
  echo Compiling ${yr} rule set for production
  python3.12 ${ARELLE_DIR}/arelleCmdLine.py --plugins xule --xule-arg RESOURCES_DIR=${REPOS_DIR}/ --xule-compile ${TEMP_DIR} --xule-rule-set ${DEST_ZIP} --xule-crash --xule-args-file ${DEST_CONSTS}

done
