---
applyTo: "*.xule"
---
# Project general rule coding standards

## Naming Conventions
- Use camelCase for variables, functions, and methods
- Use ALL_CAPS for constants
- use UPPERCASE for key words such as ASSERT, OUTPUT, MESSAGE, IF, ELSE, SKIP, SEVERITY, RULE-NAME-PREFIX, SATISFIED, UNSATISFIED, FILTER, NAVIGATE etc.

## Commenting
- Use `/** comment **/` for multi-line comments
- Use `// comment` for single line comments

## Rule Metadata
- Include the following metadata at the start of each rule file:
  - `ASSERT <rule_id> SATISFIED`
  - `/** DQCRT RULE **/`
  - `if not applicable_form(rule-name()) skip else` (if applicable)
  - `$ruleId = (rule-name().split('.'))[rule-name().split('.').length];`

## Rule Structure
- An IF statement does not use a THEN keyword. Should be IF condition  action   ELSE action
- Use indentation to improve readability, especially for nested conditions and actions.
- Always include a SEVERITY level (e.g., ERROR, WARNING, INFO) for each rule.
- Always include a RULE-FOCUS for each rule.
- always include an effectiveDate  in the format $effective_dates[$rule_id]