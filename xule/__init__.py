"""__init__.py

Xule is a rule processor for XBRL (X)brl r(ULE). 

This is the package init file.

DOCSKIP
See https://xbrl.us/dqc-license for license information.  
See https://xbrl.us/dqc-patent for patent infringement notice.
Copyright (c) 2017 - 2018 XBRL US, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

$Change: 22349 $
DOCSKIP
"""
#from .XuleParser import parseRules

from .XuleProcessor import process_xule, XuleProcessingError
#from .XuleRuleSet import XuleRuleSet, XuleRuleSetError
from . import XuleRuleSet as xr
from . import XuleUtility as xu
from .XuleContext import XuleGlobalContext, XuleRuleContext
from .XuleConstants import RULE_SET_MAP
from optparse import OptionParser, SUPPRESS_HELP
from arelle import FileSource
from arelle import ModelManager
from arelle.CntlrWebMain import Options
import optparse
import os 

__version__ = '3.0.' + '$Change: 22349 $'[9:-2]

_cntlr = None
_options = None

def xuleMenuOpen(cntlr, menu):
    pass

def xuleMenuTools(cntlr, menu):
    pass

def xuleCmdOptions(parser):
    # extend command line options to compile rules
    if isinstance(parser, Options):
        parserGroup = parser
    else:
        parserGroup = optparse.OptionGroup(parser,
                                           "Xule Business rule")
        parser.add_option_group(parserGroup)
    
    parserGroup.add_option("--xule-compile", 
                      action="store", 
                      dest="xule_compile", 
                      help=_("Xule files to be compiled.  "
                             "This may be a file or directory.  When a directory is provided, all files in the directory will be processed.  "
                             "Multiple file and directory names are separated by a '|' character. "))
    
    parserGroup.add_option("--xule-rule-set",
                      action="store",
                      dest="xule_rule_set",
                      help=_("RULESET to use (this is the directory where compile rules are stored."))
    
    parserGroup.add_option("--xule-run",
                      action="store_true",
                      dest="xule_run",
                      help=_("Indicates that the rules should be processed."))
    
    parserGroup.add_option("--xule-add-packages",
                           action="store",
                           dest="xule_add_packages",
                           help=_("Add packages to a xule rule set. Multiple package files are separated with a |."))

    parserGroup.add_option("--xule-remove-packages",
                           action="store",
                           dest="xule_remove_packages",
                           help=_("Remove packages from a xule rule set. Multiple package files are separated with a |."))
    
    parserGroup.add_option("--xule-show-packages",
                     action="store_true",
                     dest="xule_show_packages",
                     help=_("Show list of packages in the rule set."))    

    parserGroup.add_option("--xule-bypass-packages",
                     action="store_true",
                     dest="xule_bypass_packages",
                     help=_("Indicates that the packages in the rule set will not be activated."))  
    
    parserGroup.add_option("--xule-time",
                     action="store",
                     type="float",
                     dest="xule_time",
                     help=_("Output timing information. Supply the minimum threshold in seconds for displaying timing information for a rule."))
    
    parserGroup.add_option("--xule-trace",
                     action="store_true",
                     dest="xule_trace",
                     help=_("Output trace information."))
    
    parserGroup.add_option("--xule-trace-count",
                      action="store",
                      dest="xule_trace_count",
                      help=_("Name of the file to write a trace count."))
    
    parserGroup.add_option("--xule-debug",
                     action="store_true",
                     dest="xule_debug",
                     help=_("Output trace information."))    

    parserGroup.add_option("--xule-debug-table",
                     action="store_true",
                     dest="xule_debug_table",
                     help=_("Output trace information."))  
    
    parserGroup.add_option("--xule-debug-table-style",
                       action="store",
                       dest="xule_debug_table_style",
                       help=_("The table format. The valid values are tabulate table formats: plain, simple, grid, fancy_gri, pipe, orgtbl, jira, psql, rst, mediawiki, moinmoin, html, latex, latex_booktabs, textile."))  
    
    parserGroup.add_option("--xule-crash",
                     action="store_true",
                     dest="xule_crash",
                     help=_("Output trace information."))
    
    parserGroup.add_option("--xule-pre-calc",
                      action="store_true",
                      dest="xule_pre_calc",
                      help=_("Pre-calc expressions"))
    
    parserGroup.add_option("--xule-filing-list",
                      action="store",
                      dest="xule_filing_list",
                      help=_("File name of file that contains a list of filings to process"))
    
    parserGroup.add_option("--xule-server",
                     action="store",
                     dest="xule_server",
                     help=_("Launch the webserver."))

    parserGroup.add_option("--xule-multi",
                     action="store_true",
                     dest="xule_multi",
                     help=_("Turns on multithreading"))
    
    parserGroup.add_option("--xule-cpu",
                     action="store",
                     dest="xule_cpu",
                     help=_("overrides number of cpus per processing to use"))
    
    parserGroup.add_option("--xule-async",
                     action="store_true",
                     dest="xule_async",
                     help=_("Outputs onscreen output as the filing is being processed"))

    parserGroup.add_option("--xule-numthreads",
                     action="store",
                     dest="xule_numthreads",
                     help=_("Indicates number of concurrents threads will run while the Xule Server is active"))
    
    parserGroup.add_option("--xule-skip",
                      action="store",
                      dest="xule_skip",
                      help=_("List of rules to skip"))
    
    parserGroup.add_option("--xule-no-cache",
                      action="store_true",
                      dest="xule_no_cache",
                      help=_("Turns off local caching for a rule."))
    
    parserGroup.add_option("--xule-precalc-constants",
                      action="store_true",
                      dest="xule_precalc_constants",
                      help=_("Pre-calculate constants that do not depend on the instance."))

    parserGroup.add_option("--xule-exclude-nils",
                      action="store_true",
                      dest="xule_exclude_nils",
                      help=_("Indicates that the processor should exclude nil facts. By default, nils are included."))
    
    parserGroup.add_option("--xule-include-dups",
                      action="store_true",
                      dest="xule_include_dups",
                      help=_("Indicates that the processor should include duplicate facts. By default, duplicate facts are ignored."))    
    
    parserGroup.add_option("--xule-version",
                      action="store_true",
                      dest="xule_version",
                      help=_("Display version number of the xule module."))
    
    parserGroup.add_option("--xule-update-rule-set-map",
                           action="store",
                           dest="xule_update_rule_set_map",
                           help=_("Update the rule set map currently used. The supplied file will be merged with the current rule set map."))

    parserGroup.add_option("--xule-replace-rule-set-map",
                           action="store",
                           dest="xule_replace_rule_set_map",
                           help=_("Replace the rule set map currently used."))
    
    parserGroup.add_option("--xule-reset-rule-set-map",
                           action="store_true",
                           dest=("xule_reset_rule_set_map"),
                           help=("Reset the rule set map to the default."))
    

def xuleCmdUtilityRun(cntlr, options, **kwargs): 
    # Save the controller and options in the module global variable
    global _cntlr
    _cntlr = cntlr
    global _options
    _options = options 
    
    #check option combinations
    parser = OptionParser()
    
    if getattr(options, "xule_version", False):
        cntlr.addToLog("Xule version: %s" % __version__)
        cntlr.close()

    if getattr(options, "xule_cpu", None) is not None and not getattr(options, 'xule_multi', None):
            parser.error(_("--xule-multi is required with --xule_cpu."))

#     if  getattr(options, "xule_run", None) is not None and not getattr(options, 'xule_rule_set', None):
#             parser.error(_("--xule-rule-set is required with --xule-run."))
    
    if getattr(options, "xule_server", None) is not None and not getattr(options, 'xule_rule_set', None):
            parser.error(_("--xule-rule-set is required with --xule_server."))
            
    if getattr(options, "xule-numthreads", None) == None:
        setattr(options, "xule-numthreads", 1)   
    
    if getattr(options, 'xule_add_packages', None) is not None and not getattr(options, 'xule_rule_set', None):
        parser.error(_("--xule-rule-set is required with --xule-add-packages.")) 

    if getattr(options, 'xule_remove_packages', None) is not None and not getattr(options, 'xule_rule_set', None):
        parser.error(_("--xule-rule-set is required with --xule-remove-packages.")) 

    if getattr(options, 'xule_show_packages', None) is not None and not getattr(options, 'xule_rule_set', None):
        parser.error(_("--xule-rule-set is required with --xule-show-packages.")) 

    from os import name
    if getattr(options, "xule_multi", False) and name == 'nt':
        parser.error(_("--xule-multi can't be used in Windows"))    

    if not getattr(options, "xule_multi", False) and getattr(options, "xule_cpu", None) is not None:
        parser.error(_("--xule-cpu can only be used with --xule-multi enabled"))    

    if len([x for x in (getattr(options, "xule_update_rule_set_map", False),
                       getattr(options, "xule_replace_rule_set_map", False),
                       getattr(options, "xule_reset_rule_set_map", False)) if x]) > 1:
        parser.error(_("Cannot use --xule-update-rule-set-map or --xule-replace-rule-set-map or --xule-reset-rule-set-map the same time."))
        
    #compile rules
    if getattr(options, "xule_compile", None):
        compile_destination = getattr(options, "xule_rule_set", "xuleRules") 
        from .XuleParser import parseRules
        parseRules(options.xule_compile.split("|"),compile_destination)
    
    #add packages
    if getattr(options, "xule_add_packages", None):
        rule_set = xr.XuleRuleSet(cntlr)
        rule_set.open(getattr(options, "xule_rule_set"), open_packages=False, open_files=False)
        packages = options.xule_add_packages.split('|')
        rule_set.manage_packages(packages, 'add')

    #remove packages
    if getattr(options, "xule_remove_packages", None):
        rule_set = xr.XuleRuleSet(cntlr)
        rule_set.open(getattr(options, "xule_rule_set"), open_packages=False, open_files=False)
        packages = options.xule_remove_packages.split('|')
        rule_set.manage_packages(packages, 'del')
    
    #show packages
    if getattr(options, "xule_show_packages", False):
        rule_set = xr.XuleRuleSet(cntlr)
        rule_set.open(getattr(options, "xule_rule_set"), open_packages=False, open_files=False)
        print("Packages in rule set:")
        for package_info in rule_set.get_packages_info():
            print('\t' + package_info.get('name') + ' (' + os.path.basename(package_info.get('URL')) + ')' )
    
    #update rule set map
    if getattr(options, 'xule_update_rule_set_map', None):
        xu.update_rule_set_map(cntlr, getattr(options, 'xule_update_rule_set_map'))
    
    #replace rule set map
    if getattr(options, 'xule_replace_rule_set_map', None):
        xu.update_rule_set_map(cntlr, getattr(options, 'xule_replace_rule_set_map'), overwrite=True)
    
    #reset rule set map
    if getattr(options, 'xule_reset_rule_set_map', False):
        xu.reset_rule_set_map(cntlr)
    
    if getattr(options, "xule_server", None):
        from .XuleMultiProcessing import run_constant_group, output_message_queue
        from threading import Thread
        
        try:
            rule_set = xr.XuleRuleSet()
            rule_set.open(options.xule_rule_set, False)
        except xr.XuleRuleSetError:
            raise

        # Create global Context
        global_context = XuleGlobalContext(rule_set, cntlr=cntlr, options=options#,
                                           #multi=getattr(options, "xule_multi", False), 
                                           #async=getattr(options, "xule_async", False),
                                           #cpunum=getattr(options, "xule_cpu", None))
                                           )
        #global_context.show_timing = getattr(options, "xule_time", None)
        #global_context.show_debug = getattr(options, "xule_debug", False)
        #global_context.show_debug_table = getattr(options, "xule_debug_table", False)
        #global_context.show_trace = getattr(options, "xule_trace", None)
        #global_context.crash_on_error = getattr(options, "xule_crash", False)

        global_context.message_queue.print("Using %d processors" % (global_context.num_processors)) 

        # Start Output message queue
        if getattr(options, "xule_multi", False):
            t = Thread(target=output_message_queue, args=(global_context,))
            t.start()
        
#         #load rules taxonomy
#         global_context.message_queue.logging("Loading rules taxonomy")
#         global_context.get_rules_dts()        
# #        rules_dts = global_context.get_rules_dts()
# #        from .XuleProcessor import load_networks
# #        load_networks(rules_dts)
         
        global_context.message_queue.logging("Building Constant and Rule Groups")
        global_context.all_constants = rule_set.get_grouped_constants()
        global_context.all_rules = rule_set.get_grouped_rules()        

        
        for g in global_context.all_constants:
            global_context.message_queue.logging("Constants: %s - %d" % (g, len(global_context.all_constants[g])))
        #    for c in global_context.all_constants[g]:
        #        print(" -- %s" % (c))

        for g in global_context.all_rules:
            global_context.message_queue.logging("Rules: %s - %d" % (g, len(global_context.all_rules[g])))
            #for c in global_context.all_rules[g]:
            #    print(" -- %s" % (c))


        # evaluate valid constants (no dependency, rules taxonomy)
        global_context.message_queue.logging("Calculating and Storing Constants")
        run_constant_group(global_context, 'c', 'rtc')

                                   
        # Add precalculated information to the cntlr to pass to XuleServer
        setattr(cntlr, "xule_options", options)
        setattr(cntlr, "rule_set", global_context.rule_set)        
        setattr(cntlr, "constant_list", global_context._constants)
        setattr(cntlr, "all_constants", global_context.all_constants)
        setattr(cntlr, "all_rules", global_context.all_rules)        


        global_context.message_queue.logging("Finished Server Initialization")
        
        # stop message_queue
        global_context.message_queue.stop()
        
        if getattr(options, "xule_multi", False):
            t.join()
    else:
        if options.entrypointFile is None:
            #try running the xule processor
            xuleCmdXbrlLoaded(cntlr, options, None)
    #process filing list
    if getattr(options, "xule_filing_list", None):
        try:
            with open(options.xule_filing_list, "r") as filing_list:
                for line in filing_list:

                    filing = line.strip()
                    print("Processing filing", filing)
                    filing_filesource = FileSource.openFileSource(filing, cntlr)            
                    modelManager = ModelManager.initialize(cntlr)
                    modelXbrl = modelManager.load(filing_filesource) 
                    xuleCmdXbrlLoaded(cntlr, options, modelXbrl)
                    modelXbrl.close()

        except FileNotFoundError:
            print("Filing listing file '%s' is not found" % options.xule_filing_list)

def xuleCmdXbrlLoaded(cntlr, options, modelXbrl, entryPoint=None):   
    if getattr(options, "xule_run", None):
        runXule(cntlr, options, modelXbrl)
        
def runXule(cntlr, options, modelXbrl):
        try:
            if getattr(options, "xule_multi", True) and \
                getattr(cntlr, "rule_set", None) is not None:
                rule_set =  getattr(cntlr, "rule_set")
            else:
                if getattr(options, 'xule_rule_set', None) is not None:
                    rule_set_location = options.xule_rule_set
                else:
                    # Determine the rule set from the model.
                    rule_set_location = xu.determine_rule_set(modelXbrl, cntlr)
                    if rule_set_location is None:
                        # The rule set could not be determined.
                        raise xr.XuleRuleSetError('The rule set to used could not be determined. Check that there is a rule set map at {} and verify that there is an appropiate mapping for the filing.'.format(RULE_SET_MAP))
                    
                rule_set = xr.XuleRuleSet(cntlr)              
                rule_set.open(rule_set_location, open_packages=not getattr(options, 'xule_bypass_packages', False))
        except xr.XuleRuleSetError:
            raise

        if getattr(options, "xule_multi", False):
            from .XuleMultiProcessing import start_process
            start_process(rule_set, 
                         modelXbrl, 
                         cntlr, 
                         options
                         )
        else:
            if modelXbrl is None:
                #check if there are any rules that need a model
                for rule in rule_set.catalog['rules'].values():
                    if rule['dependencies']['instance'] == True and rule['dependencies']['rules-taxonomy'] != False:
                        raise xr.XuleRuleSetError('Need instance to process rules')
                    
                    
            process_xule(rule_set,
                         modelXbrl, 
                         cntlr, 
                         options,
                         )
            
def xuleValidate(val):
    global _cntlr
    global _options
    if _cntlr is not None and _options is not None:
        if not getattr(_options, "xule_run", False):
            # Only run on validate if the --xule-run option was not supplied. If --xule-run is supplied, it has already been run
            runXule(_cntlr, _options, val.modelXbrl)

def xuleTestStart(modelTestcaseVariation):        
    pass

def xuleTestXbrlLoaded(modelTestcaseVariation):
    pass

def xuleModelTestVariationReadMe(modelTestcaseVariation):
    pass

def xuleModelTestVariationExpectedResult(modelTestcaseVariation):
    pass

def xuleModelTestVariationExpectedSeverity(modelTestcaseVariation):
    pass

def xuleDialogRssWatchFileChoices(dialog, frame, row, options, cntlr, openFileImage, openDatabaseImage):
    pass

def xuleRssWatchHasWatchAction(rssWatchOptions):
    pass

def xuleRssDoWatchAction(modelXbrl, rssWatchOptions, rssItem):
    pass

__pluginInfo__ = {
    'name': 'DQC XBRL rule processor (xule)',
    'version': '1.0',
    'description': 'This plug-in provides a DQC 1.- processor.',
    'license': 'Apache-2',
    'author': 'XBRL US Inc.',
    'copyright': '(c) 2017',
    # classes of mount points (required)
    'ModelObjectFactory.ElementSubstitutionClasses': None, 
    'CntlrWinMain.Menu.File.Open': xuleMenuOpen,
    'CntlrWinMain.Menu.Tools': xuleMenuTools,
    'CntlrCmdLine.Options': xuleCmdOptions,
    'CntlrCmdLine.Utility.Run': xuleCmdUtilityRun,
    'CntlrCmdLine.Xbrl.Loaded': xuleCmdXbrlLoaded,
    'Validate.Finally': xuleValidate,
    'Testcases.Start': xuleTestStart,
    'TestcaseVariation.Xbrl.Loaded': xuleTestXbrlLoaded,
    'ModelTestcaseVariation.ReadMeFirstUris': xuleModelTestVariationReadMe,
    'ModelTestcaseVariation.ExpectedResult': xuleModelTestVariationExpectedResult,
    'ModelTestcaseVariation.ExpectedSeverity': xuleModelTestVariationExpectedSeverity,
    'DialogRssWatch.FileChoices': xuleDialogRssWatchFileChoices,
    'DialogRssWatch.ValidateChoices': xuleRssWatchHasWatchAction,
    'RssWatch.HasWatchAction': xuleRssWatchHasWatchAction,
    'RssWatch.DoWatchAction': xuleRssDoWatchAction
    }
