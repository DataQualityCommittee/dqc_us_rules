# !/bin/bash
#
# build DQCRT ruleset for EDGAR
#
REPOS_DIR=/Users/hermf/temp/plugin/DQC
ARELLE_DIR=/Users/hermf/Documents/projects/Arelle/ArelleProject/edgrReorg
ARELLE_XULE_RESOURCES_DIR=${ARELLE_DIR}/arelle/plugin/EDGAR/validate/resources/xule
CACHE_DIR=/Users/hermf/Library/Caches/Arelle
for yr in 2023 2024 2025
do
  # for source_dir from hermfischer-wf git use this
  #SOURCE_DIR="${REPOS_DIR}/dqc_us_rules/dqc_us_rules/source"
  SOURCE_DIR="${REPOS_DIR}/cp.xule.dqc/dqc_us_rules/source"
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
  sed -e '/xml version=/d' -e "/\'\(\.\.\/\)\{0,9\}\(elts\/\)\{0,1\}us-gaap-ebp-/s//\'https:\/\/xbrl.fasb.org\/us-gaap\/${yr}\/ebp\/elts\/us-gaap-ebp-/g" -e "/\'\(\.\.\/\)\{0,9\}\(elts\/\)\{0,1\}us-roles-/s//\'https:\/\/xbrl.fasb.org\/us-gaap\/${yr}\/elts\/us-roles-/g" -e "/\'\(\.\.\/\)\{0,9\}\(elts\/\)\{0,1\}us-gaap-/s//\'https:\/\/xbrl.fasb.org\/us-gaap\/${yr}\/elts\/us-gaap-/g" ${TEMP_DIR}/temp.xsd >> ${DEST_CALC}
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
  python3.12 ${ARELLE_DIR}/arelleCmdLine.py --plugin xule --xule-arg RESOURCES_DIR=${REPOS_DIR}/ --xule-rule-set ${DEST_ZIP}  --xule-output-constants "ACCRUAL_ITEMS,CALC_RELATIONSHIPS,MEMBER_USGAAP_FAIR_VALUE,DEP_CONCEPTS,DEFINED_BENEFIT_COST_EXT_ENUM,BANKING_MEASURES_BETWEEN_ZERO_AND_ONE,DEFINED_BENEFIT_COST_FS_LINE_ITEMS,DERIVATIVE_LIABILITIES_FS_LINE_ITEMS,DERIVATIVE_ASSETS_FS_LINE_ITEMS,OCI_SECURITY_RELATED_ITEMS,LIQUIDATION_BASIS_CONCEPTS,TAXONOMY_DEFAULTS,NONALLOWED_ROOT_ELEMENTS_CASHFLOW,NETWORK_730000_TARGET_NON_ABSTRACT_QNAMES,ASU201517_TRANSITION_ELEMENTS,MBR_RECL_OUT_ACCUM_CMP_INC_AXS,MEM_LEG_ENT_AXS,MEM_FHLB_AXS,MBR_SCH_EQT_INV_NM_AXS,MBR_PLN_NM_AXS,MEM_DEF_CNT_PLN_NM_AXS,MEM_RNG_AXS,MEM_SRT_CUR_AXS,MEM_CUR_AXS,MEM_POS_AXS,MEM_FAR_VAL_MSR_FRQ_AXS,MEM_FAR_VAL_MSR_BAS_AXS,DEF_FAR_VAL_MSR_BAS_AXS,MEM_HDG_DSG_AXS,MEM_PRD_SVC_AXS,MEM_AIR_TP_AXS,MEM_SCH_MPR_INS_AXS,MEM_PPE_TP_AXS,MEM_RSV_QTY_RSV_AXS,MEM_PUB_UTL_INV_AXS,MEM_CON_ITM_AXS,MEM_NOT_ALLOWED_RET_TREE,MEM_AWD_DT_AXS,MEM_SUB_EVT_AXS,MBR_STM_EQY_CMP_AXS,MBR_STM_CLS_STK_AXS,MBR_STM_SCN_AXS,MBR_PRF_UNT_NM_AXS,MBR_RET_PLN_NM_AXS,MBR_OWNRSHP_AXS,MBR_MAJ_CST_AXS,MBR_BUS_ACQ_AXS,MBR_STM_BIS_SEG_AXS,MBR_AST_ACQ_AXS,MBR_STM_GEO_AXS,FINANCIAL_DATA_EQUITY_METHOD_INVESTMENTS,NCI,NON_FINANCIAL_DATA_EMI,EXCLUDE_NON_NEG_STRING_MEMBERS,EXCLUDE_NON_NEG_MEMBERS,EXCLUDE_NON_NEG_AXIS_MEMBERS_PRE,EXCLUDE_NON_NEG_AXIS_MEMBERS,EXCLUDE_NON_NEG_AXIS,effective_dates,NON_NEG_ITEMS,DIM_EQUIVALENTS,EXTENSION_ITEMS,ELEMENTS_EXCLUDED_FROM_RULE,CHILD_ELEMENTS_PROMOTABLE_TO_SIBLING_OF_PARENT_ELEMENT,SIBLINGS_DEMOTABLE_TO_CHILD,CHILD_ELEMENTS_PROMOTABLE_TO_SIBLING,PARENT_ELEMENTS_WITH_CHILDREN_PROMOTABLE_TO_SIBLING,SIBLING_ELEMENTS_WITH_SIBLINGS_DEMOTABLE_TO_DESCENDANT,MATURITY_SCHEDULE_ELEMENTS,MESSAGE_FOR_RULE_9277,MESSAGE_FOR_RULE_9278,NETWORK440000,NETWORK606000,NON_CF_ITEMS,SET_NON_CF_ABSTRACTS1,SSH_EXCEPTIONS,ASSET_TYPES,SET_CONCENTRATION_RISK_ITEMS,SET_BENCHMARK_ITEMS,TRANSITION_ELTS_1,TRANSITION_ELTS_2,ALLOWABLE_FINANCING_ITEMS,NON_FINANCING_DESCENDANTS,NON_INVESTING_DESCENDANTS,FILIN_COMPONENTS_OF_NET_INC_LOSS,CHG_IN_OP_CAPTL,ECD_ADJ_TO_COMP_MBRS,APIC_ADJUSTMENTS,AOCI_MEMBERS,OCI_CONCEPTS,NI_CONCEPTS,REL_PTY_STATUS_ENUM,ASU201613_TRANSITION_ELEMENTS,DIM_EQUIV_NAMES,INCOME_STATEMENT_CONCEPTS,EXT_ENUM,IDENTIFICATION,PPE_MEMBERS,INTANGIBLE_FINITE_ASSETS_MEMBERS,INTANGIBLE_INDEFINITE_ASSETS_MEMBERS,INTANGIBLE_MONETARY_ITEMS,INTANGIBLE_DURATION_ITEMS" --xule-output-constants-file ${DEST_CONSTS}

  rm -fr ${TEMP_DIR} ${DEST_ZIP}
  mkdir ${TEMP_DIR}

  # copy all rules files
  cp -p ${SOURCE_DIR}/us/${yr}/DQC_0*.xule ${TEMP_DIR}

  for f in ${SOURCE_DIR}/us/${yr}/[a-z]*.xule ${SOURCE_DIR}/lib/*.xule
  do
    cp -p ${f} ${TEMP_DIR}
  done

  # compile the rule set
  echo Compiling ${yr} rule set for production
  python3.12 ${ARELLE_DIR}/arelleCmdLine.py --plugins xule --xule-arg RESOURCES_DIR=${REPOS_DIR}/ --xule-compile ${TEMP_DIR} --xule-rule-set ${DEST_ZIP} --xule-crash --xule-args-file ${DEST_CONSTS}

done
