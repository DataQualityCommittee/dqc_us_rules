# Using DQC Rules with Arelle - from a command prompt [return to README](README.md#using)

### Confirm the DQC Arelle plugin is installed by running `arelleCmdLine --plugins xule` to return:

`
[info] Activation of plug-in DQC XBRL rule processor (xule) successful, version 1.0. - xule
`

The DQC ruleset files are part of each [downloaded release archive (v5 or later)](https://github.com/DataQualityCommittee/dqc_us_rules/releases) as .zip files in the folder "dqc_us_rules". Copy the "dqc_us_rules" folder to your environment to run them locally, or reference them from the Internet using this format `https://github.com/DataQualityCommittee/dqc_us_rules/`***raw***`/`**vMajor.Minor.FixRelease**`/dqc_us_rules/dqc-us-`**TaxonomyYear**`-V`**MajorRelease**`-ruleset.zip` when running the plugin from the command line (see below). The extracted files for US GAAP Taxonomies from 2015, 2016 and 2017 are also in the "dqc_us_rules" folder as the reference implementation for the DQC rules.   

The minimum parameters that need to be passed are the following:
* **`--plugins xule`** : Loads the DQC plugin. When running with an SEC filing, the SEC transformations are also needed for Inline XBRL filings. Both plugins can be specified using **--plugins "xule|transforms/SEC"**. The pipe character `|` separates the plugins. Specifying the SEC transforms plugins will have no affect on traditional XBRL filings, so it can be included for all SEC filings.
* **`-f`** : The location of the instance file to be evaluated. This will take a zip file, XML instance or inline XBRL file.
* **`--xule-run`**  or **`-v`**: Instructs the processor to run the rules. The **-v** option will run all Arelle validations including the DQC rules. The **--xule-run** option will only run the DQC rules.

A typical command line syntax for Arelle is as follows (including optional parameters defined below:

`
arelleCmdLine --plugins "xule|transforms/SEC" -f {instance file or zip file} --xule-run --noCertificateCheck --logFile {log file name}
`

**Examples:**  
`
arelleCmdLine --plugins "xule|transforms/SEC" -f https://www.sec.gov/Archives/edgar/data/xxx-20170930.xml  --xule-rule-set dqc-us-2017-V5-ruleset.zip --xule-run --noCertificateCheck --logFile DQC-output.xml
`  
or  
`
arelleCmdLine --plugins "xule|transforms/SEC" -f https://www.sec.gov/Archives/edgar/data/xxx-20170930.xml  --xule-rule-set https://github.com/DataQualityCommittee/dqc_us_rules/raw/v5.0.0/dqc_us_rules/dqc-us-2017-V5-ruleset.zip --xule-run --noCertificateCheck --logFile DQC-output.xml
`  

In addition the following optional parameters can be passed:

* **`--logFile`** : Specifies where the output of running the rules should be sent. To get an XML file the file needs to end with .xml. To get a json file it needs to end with .json. If a log file is not specified, output will be displayed in the command window.
* **`--noCertificateCheck`** : This is used to ensure that files from the internet are not rejected if there is no SSL certificate on the machine running the DQC plugin.
* **`--xule-bypass-packages`** : This option will ignore packages included in the ruleset. (See *Managing the Ruleset File* below)  
* **`--packages`** : This option will accept additional taxonomy packages
* **`--xule-rule-set`** : The location of the compiled ruleset to use. 

To get additional options use the option `--help` (eg. `arelleCmdLine --plugins xule --help`)

The DQC plugin options will be displayed at the bottom of the list under the title "Xule Business Rule". All DQC specific options start with `--xule`.

**Every XBRL instance has a specific taxonomy that it uses.** When running the DQC plugin the correct ruleset must be run against the XBRL instance. If the XBRL instance uses the US GAAP 2017 taxonomy then the dqc_us_rules that apply to the 2017 taxonomy must be used. 

There is a separate *dqc_us_rules* file for every *year* and *taxonomy* released. The format of the ruleset file is as follows:

`dqc-{`*`taxonomy`*`}-{`*`year`*`}-{`*`dqc_us_rules version`*`}-ruleset.zip`

For example, the ruleset for the 2017 us-gaap taxonomy for the version 5 release would be called:

`dqc-us-2017-V5-ruleset.zip`

The ruleset for the 2017 ifrs taxonomy for the version 6 release would be called:

`dqc-ifrs-2017-V6-ruleset.zip`

### [return to README](README.md#using)
 
© Copyright 2015 - 2018 XBRL US, Inc. All rights reserved.   
See [License](https://xbrl.us/dqc-license) for license information.  
See [Patent Notice](https://xbrl.us/dqc-patent) for patent infringement notice.
