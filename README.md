# Data Quality Committee Rules &amp; Guidance

The following automated checks have been drawn from experience with IFRS filings to the SEC and form the initial XBRL International Data Quality Rules in the Beta Release. 

The specification of the current ESEF DQR rules can be found below:

| Number | Short name | Rule version |
| ----- | ----- | ----- |
| [DQC_IFRS_0008](docs/DQC_IFRS_0008/DQC_0008.md) | Reversed calculation | 17 |
| [DQC_IFRS_0041](docs/DQC_IFRS_0041/DQC_0041.md) | Axis with a default member that differs from the IFRS Taxonomy | 17 |
| [DQC_IFRS_0080](docs/DQC_IFRS_0080/DQC_0080.md) | Negative Values | 17 |
| [DQC_IFRS_0092](docs/DQC_IFRS_0092/DQC_0092.md) | Non Positive Items | 17 |
| [DQC_IFRS_0093](docs/DQC_IFRS_0093/DQC_0093.md) | Durational Aggregation | 17 |
| [DQC_IFRS_0101](docs/DQC_IFRS_0101/DQC_0101.md) | Movement of Concepts between Calculation Trees | 17 |
| [DQC_IFRS_0102](docs/DQC_IFRS_0102/DQC_0102.md) | Element Values Are Equal | 17 |
| [DQC_IFRS_0103](docs/DQC_IFRS_0103/DQC_0103.md) | Invalid Value for Percentage Items | 17 |
| [DQC_IFRS_0104](docs/DQC_IFRS_0104/DQC_0104.md) | Axis with Inappropriate Members | 17 |
| [DQC_IFRS_0105](docs/DQC_IFRS_0105/DQC_0105.md) | FS with No Associated Calculation | 17 |
| [DQC_IFRS_0115](docs/DQC_IFRS_0115/DQC_0115.md) | Fact Value Consistency Over Time | 17 |
| [DQC_IFRS_0118](docs/DQC_IFRS_0118/DQC_0118.md) | Financial Statement Tables Calculation Check of Required Context | 17 |
| [DQC_IFRS_0126](docs/DQC_IFRS_0126/DQC_0126.md) | FS Calculation Check with Non Dimensional Data | 17 |
| [DQC_IFRS_0127](docs/DQC_IFRS_0127/DQC_0127.md) | Incorrect Dimensional Item Used on Financial Statements | 17 |
| [DQC_IFRS_0128](docs/DQC_IFRS_0128/DQC_0128.md) | Dimensional Values Larger than the Default | 17 |
| [DQC_IFRS_0129](docs/DQC_IFRS_0129/DQC_0129.md) | Dimensional Equivalents | 17 |
| [DQC_IFRS_0130](docs/DQC_IFRS_0130/DQC_0130.md) | Earnings Per Share Calculation | 17 |
| [DQC_IFRS_0138](docs/DQC_IFRS_0138/DQC_0138.md) | Missing Abstract from Financial Statements | 17 |

## Documentation definitions

The rules definitions make reference to the following terms:

* The **report taxonomy** is the DTS of XBRL Report, and includes the extension taxonomy.
* The **base taxonomy** is the IFRS taxonomy corresponding to the ruleset version.  The entry point used for each ruleset is shown below.

## IFRS Entry Points

The following entry points define the _base taxonomy_ for each version of the ruleset:

| Version | Entry point |
| ------- | ----------- |
| ESEF DQR 2019 | `http://xbrl.ifrs.org/taxonomy/2019-03-27/full_ifrs_entry_point_2019-03-27.xsd` |
| ESEF DQR 2020 | `http://xbrl.ifrs.org/taxonomy/2020-03-16/full_ifrs_entry_point_2020-03-16.xsd` | 
| ESEF DQR 2021 | `http://xbrl.ifrs.org/taxonomy/2021-03-24/full_ifrs_entry_point_2021-03-24.xsd` | 

## Reference implementation

A reference implementation of the ESEF DQR rules is also available.  The reference implementation is defined using the [XULE language](https://xbrl.us/home/use/what-is-xule) developed by XBRL US.  The language is free to use, and an open source [XULE engine](https://github.com/xbrlus/xule/releases/latest) is available for the [Arelle](https://arelle.org/pub) XBRL processor.   


© Copyright 2015 - 2022 XBRL US, Inc. All rights reserved.   
See [License](https://xbrl.us/dqc-license) for license information.  
See [Patent Notice](https://xbrl.us/dqc-patent) for patent infringement notice.  
