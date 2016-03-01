# Global Rule Logic

The following guidance applies to all rules, unless the rule documentation specifies otherwise

## Rule Numbering Format

The message code of each DQC message is as follows:  DQC.US.nnnn.mmm where nnnn is the rule identifier (e.g., 0015 for non-negative rules) and mmm is the index of test within the rule. (The index does not have leading zeros.)

## Reporting Period End Date

The reporting period end date is the ending date of the Required Context as defined in the SEC EDGAR Filer Manual.

## Existence of Components

If one of the components in a comparison does not exist then the comparison will not occur. For example if the rule tests Assets = LiabilitiesAndShareholdersEquity and one of the elements is missing, the test will not run. 

## Element Name Comparison

When portions of an element name are matched to comparison strings, the comparison is case insensitive unless otherwise stated in the rule. When elements are matched based on their full qualified name (QName), the element name (local part of the QName) comparison is case sensitive and the namespace (URI) comparison follows IETF rules. Element labels are not used for matching unless otherwise stated in the rule.

## Decimal Comparison

When comparing two numeric fact values in a rule, the comparison needs to take into account different decimals. Numbers are compared based on the lowest decimal value rounded per XBRL specification. For example, the number 532,000,000 with decimals of -6 is considered to be equivalent to 532,300,000 with a decimals value of -5. In this case the 532,300,000 is rounded to a million and then compared to the value of 532,000,000.  (Note that XBRL specifies "round half to nearest even" so 532,500,000 with decimals -6 rounds to 532,000,000, and 532,500,001 rounds to 533,000,000.)

## Dimensional Equivalence

All comparisons between fact values occur between facts of equivalent dimensions.  A rule will produce a message for each occurrence of the compared facts in equivalent dimensions.

## Units

If a non numeric fact is compared with a numeric fact then the rule does not match on units. 

## Message Format Syntax

The rule message template contains text and parametric reference to arguments of the rule operation, using the syntax ${parameter} to indicate that insertion of a parameter's value is to occur.  

Each rule has a dynamic message associated with it that uses ${..} to define the parametric references to elements that may be facts or other data of the filing.

### Fact Properties

**Facts identified by number**

Messages for rules that return facts as model object references can refer to those facts ordinally, beginning with index 1. The references to these facts can include the following properties:

* ${fact1.name}  Prefixed name of the fact's concept.

* ${fact1.localName}  The local name (without prefix) of the fact's concept.

* ${fact1.label}  The label of the fact (standard role, English, although a tool may provide options to select another role, such as terse, and another language).  The label is obtained from the extension (filing) taxonomy.  If there is no label, the prefixed name is shown instead.

* ${fact1.value}  The value of the fact.  If numeric, field separators are provided for thousands (comma in en-US locale).   

* ${fact1.decimals}  The value of the decimals attribute if numeric.

* ${fact1.period}  The period (forever, instant date, or start-end dates).

    * ${fact1.period.startDate}  Start date

    * ${fact1.period.endDate}  End date or instant date

    * ${fact1.period.instant}  Instant date

    * ${fact1.period.durationDays}  End date - start date, in days

* ${fact1.dimensions}  prefixed dimension name = prefixed member name, for each non-defaulted dimension, or "none" if no or all-defaulted dimensions

* ${fact1.unit}  non-prefixed unit names, e.g., USD or shares, or "none" if no units.

**Facts identified by prefixed name**

Facts which are not ordinal arguments may be specified by prefixed name, such as dei:DocumentPeriodEndDate.fact.  These are specified as ${dei:DocumentPeriodEndDate.fact.name}, ${dei:DocumentPeriodEndDate.fact.value}, etc.  The fields are same as for ordinal fact references, as in the section above. The ".fact." must appear between the prefixed name and property name.

**Concepts identified by prefixed name**

Concepts may be provided for message argument fact dimensions and their members, for example ${my:FooAxis.label} or ${my:BarMember.label}.  Concepts have the following properties:

* ${fact1.name}  Prefixed name of the concept.

* ${fact1.localName}  The local name (without prefix) of the concept.

* ${fact1.label}  The label of the concept (standard role, English, although a tool may provide options to select another role, such as terse, and another language).  The label is obtained from the extension (filing) taxonomy.  If there is no label, the prefixed name is provided instead.

If there are variable references that can't be resolved, such as missing facts, prefixed named concepts not passed in argument facts or their dimensions, or for any other reason, an error message is logged when using Arelle to indicate the unresolved references.  The variable reference substitutes as "unavailable" in the expanded message text in addition to the error indicating unresolved references.


© Copyright 2015 - 2016, XBRL US Inc. All rights reserved.   
See [License](../../License.md) for license information.  
See [Patent Notice](../../PatentNoticer.md) for patent infringement notice.
