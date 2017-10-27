#!/bin/bash
# the next line restarts using wish -*- tcl -*- \
#exec /aurproj/tools/ActiveState/$(/bin/uname -s)/tcl8.4/bin/tclsh "$0" "$@"
#exec /usr/local/bin/tclsh/ "$0" "$@"

################################################################################
# Name               : parseFocusLog
# Function Objective : Extract TL1,CLI, and PCTA commands from APME log into output
#                      html file and make links in InstantStatus.html.
# Input Parameters   : -type Command type to parse
#                      -log  input APME log
#                      -out  output command file
#
# Output Parameters  : none
#
# Author           Release       Date        Comment 
# Koen Hermans     N/A           3/09/2015   Creation
# Koen Hermans     N/A           3/26/2015   Loop 2 times through log file
################################################################################

#######################################################################################################################
# Help Procedure
#######################################################################################################################
proc printUsage {} {
  global argv0
  puts {USAGE:}
  puts " parseApmeLog.tcl -log <APME log path> -local <0|1> -atc <atc name> -onlyparse <0|1>"
  puts {    Arguments:}
  puts {}
  puts {      -log <APME log path>        The path to the APME log to be parsed. If ommited it looks for TS_focus.log1.}
  puts {}
  puts {      -local <0|1>	          Run on a local directory and edit InstantStatus.html file. Default [0].}
  puts {}
  puts {      -atc <atc name>	          Force a non-TI ATC to be parsed. Used to compare good and faulty runs. }
  puts {}
  puts {      -onlyparse <0|1>	          Only parse faulty ATCs. Do not touch InstantStatus.html file. Default [0]. }
  puts {}
}

######################################################################################################################
# Proc to edit InstantStatus.html file
######################################################################################################################
proc pEditInstant {sDirHtml sDirLogs sTestCase sIteration} {
  
  set bFoundTC 0
  set bEditOk 0
  set iIterNmb 0
  
  set iInFileTiInfo [open "$sDirHtml/TiOkInfo.html" r]
  set iOutFileTiInfo [open "$sDirHtml/TiInfo.html" w]

  while {[gets $iInFileTiInfo sLogLine] >= 0} {
    if {$bEditOk} {
      puts $iOutFileTiInfo $sLogLine
      continue
    }
    if {!$bFoundTC} { 
      if {[string match "<td>$sTestCase*" $sLogLine]} {
	incr iIterNmb
	if {$iIterNmb == $sIteration} {
	  set bFoundTC 1
	}
      }
      puts $iOutFileTiInfo $sLogLine
    } else {
      if {[regexp {(.*)FAIL(.*)} $sLogLine sMatch s1 s2]} {
	puts $iOutFileTiInfo "$s1<a href=\"${sDirLogs}/${sTestCase}_${sIteration}.html\" target=\"_top\">FAIL</a>$s2"
	set bEditOk 1
      } else {
	puts $iOutFileTiInfo $sLogLine
      }
    }
  }
  close $iOutFileTiInfo
  close $iInFileTiInfo
  file copy -force "$sDirHtml/TiInfo.html" "$sDirHtml/TiOkInfo.html"
  file delete "$sDirHtml/TiInfo.html"
}

###############################################################################################################
# Proc to loop through log file and capture ATCs that fail and put them in list
################################################################################################################
proc pCheckLogForTestFail {sLogFile sAtc} {
  
  set bFailInTestCase 0
  set bFirstTestCase 1
  set sTestCase ""
  set sPrevTestCase ""
  set sPStyle "STYLE='font-size:13px;font-family:consolas;line-height:110%'"
  array set aTestCases {}
  
  set iLogFileId [open $sLogFile r]
  set sOutFileAlarms "../Alarms.html"
  set iOutFileAlarms [open $sOutFileAlarms w]
  puts $iOutFileAlarms "<!DOCTYPE html PUBLIC \"-//IETF//DTD HTML 2.0//EN\"><HTML><HEAD> <TITLE>Alarms</TITLE>\
	</HEAD><BODY $sPStyle><P>"
  puts $iOutFileAlarms "_______________________________________________ Alarms ______________________________________<br>"

  # Read Log by line till EOF
  while {[gets $iLogFileId sLogLine] >= 0} {
      if {[regexp {TEST_START TP_IsamTopLevelTest: (.*) on.*} $sLogLine sMatch sTestCaseDir]} {
	if {[regexp {(.*)\.ars} $sTestCaseDir sMatch sFull]} {
	  set lDirElem [split $sFull "/"]
	  set sTestCase [lindex $lDirElem end]
	}
	if {!$bFirstTestCase} {
	  if {$bFailInTestCase} {
	    set aAllTestCases(${sPrevTestCase},$aTestCases(${sPrevTestCase})) F
	    set bFailInTestCase 0
	  } else {
	    #set aAllTestCases(${sPrevTestCase},$aTestCases(${sPrevTestCase})) P
      set aAllTestCases(${sPrevTestCase},$aTestCases(${sPrevTestCase})) F
	  }
	}
	if {$sAtc == $sTestCase} {
	  set bFailInTestCase 1
	}
	if {![info exists aTestCases(${sTestCase})]} {
	  set aTestCases(${sTestCase}) 1
	} else {
	  incr aTestCases(${sTestCase})
	}
	set bFirstTestCase 0
	set sPrevTestCase $sTestCase
      } elseif {!$bFailInTestCase && $sAtc == ""} {
	  if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s1013 TEST_FAIL (.*)} $sLogLine sMatch sTimeStamp sTestResult]} {
	    set bFailInTestCase 1
	  } elseif {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s+(\d+\/\d+\/\d+)\s(\d+:\d+:\d+)\s(.*)(\s+alarm\s+)(occurred|cleared)\s+(.*)}\
		      $sLogLine sMatch sTimeStamp sDate sTime sType s1 sOccCle sAlarmMsg]} {
	    if {$sOccCle == "occurred"} {
	      set sBgColor "#FF0000"
	    } else {
	      set sBgColor "#00CC00"
	    }
	    puts $iOutFileAlarms "<P $sPStyle>$sTimeStamp: <span style=\"color:#FFFFFF; background-color:${sBgColor}\">\
				      ALARM:</span> $sDate $sTime $sType $s1 $sOccCle $sAlarmMsg</p>"
	}	
      }
  }
  if {$bFailInTestCase} {
    set aAllTestCases(${sPrevTestCase},$aTestCases(${sPrevTestCase})) F
  } else {
    #set aAllTestCases(${sPrevTestCase},$aTestCases(${sPrevTestCase})) P
    set aAllTestCases(${sPrevTestCase},$aTestCases(${sPrevTestCase})) F
  }
  close $iLogFileId
  close $iOutFileAlarms
  return [array get aAllTestCases]
}

###############################################################################################################
# Proc to check with HG who changed an ATC the last time. Return CIL, date and commit msg
################################################################################################################
proc pHgCheckAtc sAtc {
  
  global env
  
  set lReturnValue {}
  set sFullDirAtc "cm8/auto/testcases/Design${sAtc}"
  if {[info exists env(REPO)]} {
    set sHgOutput [exec hg log -l 1 $sFullDirAtc --cwd $env(REPO)]
    set lHgOutput [split $sHgOutput "\n"]
    foreach sHgLine $lHgOutput {
      if {[string first "user" $sHgLine] > -1} {
	lappend lReturnValue [string trim [lindex [split $sHgLine ":"] 1]]
      }
      if {[string first "date" $sHgLine] > -1} {
	set sHgLine [join $sHgLine ","]
	set lDate [split $sHgLine ","]
	set sDate "[lindex $lDate 3] [lindex $lDate 2] [lindex $lDate 5]"
	lappend lReturnValue $sDate
      }
      if {[string first "summary" $sHgLine] > -1} {
	lappend lReturnValue [string trim [lindex [split $sHgLine ":"] 1]]
      }
    }
  } else {
    puts "Need environment variable \$REPO to be set to use Mercurial"
  }
  return $lReturnValue
}

###############################################################################################################
# Begin Main Program
################################################################################################################
global env

if {[expr {$argc  % 2}] || ($argc == 0)} {
  puts "Error:  You must supply an even number of arguments"
  printUsage
  exit 1
}

#Read input args
array set aArgs $argv
if {[info exists aArgs(-log)]} {
  set sLogFile $aArgs(-log)
} else {
  set sLogFile "TS_focus.log1"
}
if {[info exists aArgs(-local)]} {
  set iRunLocal $aArgs(-local)
} else {
  set iRunLocal 0
}
if {[info exists aArgs(-atc)]} {
  set sAtc $aArgs(-atc)
} else {
  set sAtc ""
}
if {[info exists aArgs(-onlyparse)]} {
  set bOnlyParse $aArgs(-onlyparse)
} else {
  set bOnlyParse 0
}

# Initialization
set bLogLineHandled 0
set sTestCaseHandled ""
set sTestCase ""
set sPrevCLI ""
set lFailSteps {}
set lTclErrors {}
set lAlarms {}
set iStepCount 0
set bCleanTestCase 1
set sPStyle "STYLE='font-size:13px;font-family:consolas;line-height:110%'"
set sTextCaseHandledNmb 0
set iOutFileFrameUp ""
set iOutFileFrame ""
set sTestCaseDirHandled ""
set sPrevLogLine ""
set bBatchAborted 0
set bHgOk 0
set iAppendNextLine 0
set sCopyLogLine ""

# Call proc to loop through log file and capture ATCs that fail and put them in array
array set aAllTestCases [pCheckLogForTestFail $sLogFile $sAtc]

# Init: make Logs dir, set directories for files and open Alarms file
if {$sAtc == ""} {
  #set sDirLogs "../apelogs/Logs"
  set sDirLogs "TS_focus_parsed"
} else {
  set sDirLogs "Logs"
}
set sDirHtml "../HTML_Temp"
file mkdir $sDirLogs

if {[info exists env(TP_DOMAIN)]} {
  set sDomain $env(TP_DOMAIN)
} else {
  set sDomain ""
}
if {[info exists env(TEST_COVERAGE)]} {
  set sCoverage [string toupper $env(TEST_COVERAGE)]
} else {
  set sCoverage ""
}
if {![catch {exec hg --version} sHgVersion]} {
  if {[lindex [split $sHgVersion " "] 0] == "Mercurial"} {
    if {[info exists env(REPO)]} {
      set bHgOk 1
    } else {
      puts "Need environment variable \$REPO to be set to use Mercurial"
    }
  }
}

# Open Log file again to parse failed tests
set iLogFileId [open $sLogFile r]

###############################################################################################################
# Loop through all lines in Log file
################################################################################################################
# Read Log by line till EOF
while {[gets $iLogFileId sLogLine] >= 0} {
  if {$iAppendNextLine == 1} {
    set sLogLine [append sCopyLogLine $sLogLine]
    set iAppendNextLine 2
  } else {
    set sCopyLogLine $sLogLine  
  }
  # Test Case Comments
  set bLogLineHandled 0
  
  if {[regexp {TEST_START TP_IsamTopLevelTest: Starting (.*) on(.*)} $sLogLine sMatch sTestCaseDir sBrdDom]} {
    if {[string first "domain" $sBrdDom] > 0} {
      if {[regexp {(.*) domain is (.*)} $sBrdDom sMatch sBrd sDom]} {
	set sBoard [string trim $sBrd]
      }
    } else {
      set sBoard [string trim $sBrdDom]
    }
    set sBoard [string map {" " ""} $sBoard]
    if {$sBoard == "allapplicableboards" || $sBoard == ""} {
      set sBoard "ALL"
    }
    if {[regexp {(.*)\.ars} $sTestCaseDir sMatch sFull]} {
      set lDirElem [split $sFull "/"]
      set sTestCase [lindex $lDirElem end]
      if {![info exists aHandledTestCases(${sTestCase})]} {
	set aHandledTestCases(${sTestCase}) 1
      } else {
	incr aHandledTestCases(${sTestCase})
      }
    }
  
    # Check if testcase has fails in it
     if {$aAllTestCases(${sTestCase},$aHandledTestCases(${sTestCase})) == "F"} {
      set bCleanTestCase 0
      puts -nonewline " F"
      
      flush stdout
      if {$iRunLocal} {
	pEditInstant $sDirHtml $sDirLogs $sTestCase $aHandledTestCases(${sTestCase})
      }
      
      # New failed testcase. Handle counters and close previous failed testcase files
      if {[info exists iOutFileTestCase]} {
	#puts "TC = ${sTestCase} - TCHandled = ${sTestCaseHandled} - TCNmb = $aHandledTestCases(${sTestCase}) - TCPrevNmb = $sTextCaseHandledNmb"
	set sNmbTstFail "TEST_FAIL: "
	foreach sStepNmb $lFailSteps {
	  set sPrevStepNmb [expr $sStepNmb - 1]
	  incr iStepCount
	  if {[expr $iStepCount % 15] == 0} {
	    append sNmbTstFail "<a href=\"${sTestCaseHandled}_${sTextCaseHandledNmb}_down.html#Step$sPrevStepNmb\"  target=\"down\">${sStepNmb}.B</a>&nbsp;<a href=\"${sTestCaseHandled}_${sTextCaseHandledNmb}_down.html#Step$sStepNmb\"  target=\"down\">${sStepNmb}.E</a>&nbsp;<br>"
	  } else {
	    append sNmbTstFail "<a href=\"${sTestCaseHandled}_${sTextCaseHandledNmb}_down.html#Step$sPrevStepNmb\"  target=\"down\">${sStepNmb}.B</a>&nbsp;<a href=\"${sTestCaseHandled}_${sTextCaseHandledNmb}_down.html#Step$sStepNmb\"  target=\"down\">${sStepNmb}.E</a>&nbsp;"
	  }
	}
	set sTclErrors "TCL Errors: "
	foreach sStepNmb $lTclErrors {
	  set sStepTcl [expr $sStepNmb + 1]
	  append sTclErrors "<a href=\"${sTestCaseHandled}_${sTextCaseHandledNmb}_down.html#TCL$sStepTcl\"  target=\"down\">$sStepTcl</a>&nbsp;&nbsp;"
	}
	set sAlarms "Alarms: "
	foreach sAlarmNmb $lAlarms {
	  append sAlarms "<a href=\"${sTestCaseHandled}_${sTextCaseHandledNmb}_down.html#Alarm$sAlarmNmb\"  target=\"down\">$sAlarmNmb</a>&nbsp;&nbsp;"
	}
		
	puts $iOutFileFrameUp "$sNmbTstFail<br>"
	puts $iOutFileFrameUp "$sTclErrors<br>"
	puts $iOutFileFrameUp "$sAlarms<br>"
	
	#Call proc to check with HG who modified this ATC the last time
	if {$bHgOk} {
	  set lHgValues [pHgCheckAtc $sTestCaseDirHandled]
	  if {[llength $lHgValues] > 0} {
	    puts $iOutFileFrameUp "ATC Last Modified: [lindex $lHgValues 0] on [lindex $lHgValues 1] with msg \"[lindex $lHgValues 2]\""
	  }
	}
	
	close $iOutFileTestCase
	close $iOutFileFrame
	close $iOutFileFrameUp
      }
      
      # Open files for new failed testcase
      set iOutFileFrame [open "${sDirLogs}/${sTestCase}_$aHandledTestCases(${sTestCase}).html" w]
      set iOutFileFrameBoard [open "${sDirLogs}/${sTestCase}_$sBoard.html" w]
      set iOutFileFrameUp [open "${sDirLogs}/${sTestCase}_$aHandledTestCases(${sTestCase})_up.html" w]
      set iOutFileTestCase [open "${sDirLogs}/${sTestCase}_$aHandledTestCases(${sTestCase})_down.html" w]
      puts $iOutFileTestCase "<!DOCTYPE html PUBLIC \"-//IETF//DTD HTML 2.0//EN\"><HTML><HEAD> <TITLE>$sTestCase</TITLE>\
			      </HEAD><BODY $sPStyle><P>"
      puts $iOutFileFrameUp "<!DOCTYPE html PUBLIC \"-//IETF//DTD HTML 2.0//EN\"><HTML><HEAD> <TITLE>$sTestCase</TITLE>\
			      </HEAD><BODY $sPStyle><P>"
      puts $iOutFileFrame "<!DOCTYPE html PUBLIC \"-//IETF//DTD HTML 2.0//EN\"><HTML><HEAD> <TITLE>$sTestCase</TITLE>\
			      </HEAD><FRAMESET ROWS=\"83, *\"><FRAME NAME=\"up\" SRC=\"${sTestCase}_$aHandledTestCases(${sTestCase})_up.html\">\
			      <FRAME NAME=\"down\" SRC=\"${sTestCase}_$aHandledTestCases(${sTestCase})_down.html\"></FRAMESET></HTML>"
      puts $iOutFileFrameUp "____________${sCoverage}_______${sDomain}_______${sTestCase} on ${sBoard}_____________Links:_<a href=\"../../AtcInfo.html\" title=\"ATC Info\" target=\"_top\">A</a>__<a href=\"../../ARIES/DATA/data_cli.txt\" title=\"DataLines\" target=\"_top\">D</a>__<a href=\"../../trace_log_report.html\" title=\"Error Records\" target=\"_blank\">E</a>__<a href=\"../../InstantStatus.html\" title=\"Go back to InstantStatus.html\" target=\"_top\">I</a>__<a href=\"../../Alarms.html\" title=\"Show Alarms\" target=\"_blank\">L</a>__<a href=\"../../apelogs/TS_focus.log1.gz\" title=\"Open TS_focus.log1.gz file\" target=\"_top\">O</a>__<a href=\"../../apelogs/Logs/${sTestCase}_$aHandledTestCases(${sTestCase}).html\" title=\"Reload testcase (goto begin)\" target=\"_top\">R</a>__<a href=\"../../.\" title=\"SB Dir List\" target=\"_top\">S</a>__<a href=\"../../testsummary.log\" title=\"Test Summary\" target=\"_top\">T</a>___________<br>"
      puts $iOutFileTestCase "$sPrevLogLine"
      puts $iOutFileFrameBoard "<!DOCTYPE HTML><html lang=\"en-US\"><head><meta http-equiv=\"refresh\" content=\"0;\
				url=${sTestCase}_$aHandledTestCases(${sTestCase}).html\"></head></html>"
      close $iOutFileFrameBoard
      
      # Re-initialize variables
      set sTestCaseHandled $sTestCase
      set sTestCaseDirHandled $sTestCaseDir 
      set sTextCaseHandledNmb $aHandledTestCases(${sTestCase})
      set lFailSteps {}
      set lTclErrors {}
      set lAlarms {}
      set iStepCount 0
    } else {
      set bCleanTestCase 1
      puts -nonewline " P"
      flush stdout
    }
    continue
  } elseif {$bCleanTestCase} {
      set sPrevLogLine $sLogLine
      continue
  }
  
######################################################################################################################
# Parse all Log lines by using regular expressions
######################################################################################################################

    # [RLOG message in A2A batches
    if {[regexp {^\[RLOG.*} $sLogLine sMatch]} {
      puts $iOutFileTestCase "$sLogLine<br>"
      continue
    }
    if {[regexp {\s+\d+\s\S+\s\S+\s\S+:\s+\[RLOG.*} $sLogLine sMatch]} {
      puts $iOutFileTestCase "$sLogLine<br>"
      continue
    }
    if {$iAppendNextLine == 0} {  
      if {[regexp {\s+\d+\s\S+\s\S+\s\S+:\s+$} $sLogLine sMatch]} {
	set iAppendNextLine 1
        continue
      }
    } elseif {$iAppendNextLine == 2} {
      set iAppendNextLine 0
    }
    
    ##################################################################################################################################
    # Check for "1030 ITF_BEGIN" in logline and handle if true
    if {[regexp {\s+\d+\s\S+\s\S+\s\S+:\s+1030 ITF_BEGIN.*} $sLogLine sMatch]} {
    
      # Traffic PCTA
      if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s1030 ITF_BEGIN ars_report_msg: ITF_BEGIN:::llp_traffic_PCTA_issue_cmd: -command \{(.*)\s(.*)\}.*} \
			      $sLogLine sMatch sTimeStamp sTrafCommand sTrafParam]} {
	      if {[string match "*start_capt*" $sTrafCommand]} {set sTrafCommand "</span><span style=\"background-color:#FFCC00; color:#006600\">$sTrafCommand</span>"}
	      if {[string match "*stop_capt*" $sTrafCommand]} {set sTrafCommand "</span><span style=\"background-color:#FFCC00; color:#990000\">$sTrafCommand</span>"}
	      if {[string match "*send*" $sTrafCommand]} {set sTrafCommand "</span><span style=\"background-color:#FFCC00; color:#000066\">$sTrafCommand</span>"}
	      puts $iOutFileTestCase "<P $sPStyle>$sTimeStamp: <span style=\"color:#660066\">TRAFFIC PCTA: $sTrafCommand $sTrafParam</span></p>"
	      set bLogLineHandled 1
	      continue
      }
      
      # Traffic STC
      if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s1030 ITF_BEGIN ars_report_msg: ITF_BEGIN:::llp_traffic_STC_(\S+): (.*)}\
			      $sLogLine sMatch sTimeStamp sStcCommand sTrafCommand]} {
	      puts $iOutFileTestCase "<P $sPStyle>$sTimeStamp: <span style=\"color:#660066\">TRAFFIC STC:\
			      </span><span style=\"background-color:#FFCC00; color:#000066\">$sStcCommand</span> $sTrafCommand</span></p>"
	      set bLogLineHandled 1
	      continue
      }
  
      # ITF_BEGIN report message
      if {!$bLogLineHandled} {
	if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s1030 ITF_BEGIN ars_report_msg: ITF_BEGIN::(.*)} $sLogLine sMatch sTimeStamp sBeginMsg]} {
	    if {[info exists iOutFileTestCase]} {
	      if {[regexp {.*(^llp_\S+)(.*)} $sBeginMsg sMatch sLlp s1]} {
		set sBeginMsg "<span style=\"background-color:#99FF99\">$sLlp</span> $s1"
	      } elseif {[regexp {.*(^LLP_\S+)(.*)} $sBeginMsg sMatch sLlp s1]} {
		set sBeginMsg "<span style=\"background-color:#99FF99\">$sLlp</span> $s1"
	      } elseif {[regexp {.*:(llp_\S+):(.*)} $sBeginMsg sMatch sLlp s1]} {
		set sBeginMsg "<span style=\"background-color:#99FF99\">$sLlp</span> $s1"
	      } elseif {[regexp {.*:(hlp_\S+):(.*)} $sBeginMsg sMatch sLlp s1]} {
		set sBeginMsg "<span style=\"background-color:#99FF99\">$sLlp</span> $s1"
	      } elseif {[regexp {.*:(LLP_\S+):(.*)} $sBeginMsg sMatch sLlp s1]} {
		set sBeginMsg "<span style=\"background-color:#99FF99\">$sLlp</span> $s1"
	      } elseif {[regexp {.*:(feature_\S+):(.*)} $sBeginMsg sMatch sLlp s1]} {
		set sBeginMsg "<span style=\"background-color:#99FF99\">$sLlp</span> $s1"
	      }
	      puts $iOutFileTestCase "<P $sPStyle>$sTimeStamp: <span style=\"background-color:#CCFFCC\">ITF_BEGIN:</span> $sBeginMsg</p>"
	      set bLogLineHandled 1
	    }
	  continue
	}
      }
    }
    
    # ITF_END report message
    if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s1031 ITF_END ars_report_msg: ITF_END::(.*)} $sLogLine sMatch sTimeStamp sEndMsg]} {
	  if {[info exists iOutFileTestCase]} {
	    if {[regexp {.*(^llp_\S+)(.*)} $sEndMsg sMatch sLlp s1]} {
	      set sEndMsg "<span style=\"background-color:#FF9966\">$sLlp</span> $s1"
	    } elseif {[regexp {.*(^LLP_\S+)(.*)} $sEndMsg sMatch sLlp s1]} {
	      set sEndMsg "<span style=\"background-color:#FF9966\">$sLlp</span> $s1"
	    } elseif {[regexp {.*:(llp_\S+):(.*)} $sEndMsg sMatch sLlp s1]} {
	      set sEndMsg "<span style=\"background-color:#FF9966\">$sLlp</span> $s1"
	    } elseif {[regexp {.*:(hlp_\S+):(.*)} $sEndMsg sMatch sLlp s1]} {
	      set sEndMsg "<span style=\"background-color:#FF9966\">$sLlp</span> $s1"
	    } elseif {[regexp {.*:(LLP_\S+):(.*)} $sEndMsg sMatch sLlp s1]} {
	      set sEndMsg "<span style=\"background-color:#FF9966\">$sLlp</span> $s1"
	    } elseif {[regexp {.*:(feature_\S+):(.*)} $sEndMsg sMatch sLlp s1]} {
	      set sEndMsg "<span style=\"background-color:#FF9966\">$sLlp</span> $s1"
	    }
	    puts $iOutFileTestCase "<P $sPStyle>$sTimeStamp: <span style=\"background-color:#FFCC99\">ITF_END:</span> $sEndMsg</p>"
	    set bLogLineHandled 1
	  }
	continue
    }

    ##################################################################################################################################
    # Check for "0 INFORMATIONAL" in logline and handle if true
    if {[regexp {\s+\d+\s\S+\s\S+\s\S+:\s+0 INFORMATIONAL.*}  $sLogLine sMatch]} {
    
      # ARS report message (INFO::)
      if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s0 INFORMATIONAL ars_report_msg: INFO::(.*)}  $sLogLine sMatch sTimeStamp sReportMsg]} {
	    if {[info exists iOutFileTestCase]} {
	      puts $iOutFileTestCase "<P $sPStyle>$sTimeStamp: <span style=\"color:#CC3300\">INFO: $sReportMsg</span></p>"
	      set bLogLineHandled 1
	      continue
	    }
      }
  
      # ARS report message (ars_startup)
      if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s0 INFORMATIONAL ars_startup: (.*)}  $sLogLine sMatch sTimeStamp sReportMsg]} {
	    if {[info exists iOutFileTestCase]} {
	      puts $iOutFileTestCase "<P $sPStyle>$sTimeStamp: <span style=\"color:#CC3300\">INFO: $sReportMsg</span></p>"
	      set bLogLineHandled 1
	      continue
	    }
      }
      
      # Information ARS message
      if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s0 INFORMATIONAL ars_report_msg: (.*)}  $sLogLine sMatch sTimeStamp sFyi]} {
	    if {[info exists iOutFileTestCase]} {
	      puts $iOutFileTestCase "<P $sPStyle>$sTimeStamp: <span style=\"color:#CC3300\">INFO: $sFyi</span></p>"
	      set bLogLineHandled 1
	      continue
	    }
      }
      
      # TP_Test (REQUIRED PASS)
      if {!$bLogLineHandled} {
	if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s+0 INFORMATIONAL (TP_RequiredPASS):\s(.*)}  $sLogLine sMatch sTimeStamp sTP sTest]} {
	      puts $iOutFileTestCase "<P $sPStyle>$sTimeStamp: <span style=\"color:#FFFFFF; background-color:#0000FF\">${sTP}</span>\
				      <span style=\"color:#FFFFFF; background-color:#3366FF\"> $sTest</span></p>"
	      set bLogLineHandled 1
	      continue
	}
      }
     
      # Step # message
      if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s0 INFORMATIONAL (\S*): (Step # )(\d+) : (.*)}  $sLogLine sMatch sTimeStamp sTP sStep sStepNmb sStepRes]} {
	      puts $iOutFileTestCase "<a name=\"Step${sStepNmb}\"></a>"
	      if {$sTP == "apme_report_ars_step"} {set sTP ""}
	      if {$sStepRes == "pass"} {set sStepRes "</span><span style=\"background-color:#00CC00\">&nbsp;pass&nbsp;</span>"}
	      if {$sStepRes == "fail"} {set sStepRes "</span><span style=\"background-color:#FF0000\">&nbsp;fail&nbsp;</span>"}
	      puts $iOutFileTestCase "<P $sPStyle>$sTimeStamp: <span style=\"color:#FFFFFF; background-color:#660066\">$sTP $sStep$sStepNmb&nbsp;</span> :\
				      $sStepRes</p>"
	      set bLogLineHandled 1
	      continue
      }
      
      # Information other messages
      if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s+0 INFORMATIONAL (.*)}  $sLogLine sMatch sTimeStamp sFyi]} {
	    if {[info exists iOutFileTestCase]} {
	      puts $iOutFileTestCase "<P $sPStyle>$sTimeStamp: <span style=\"color:#CC3300\">INFO: $sFyi</span></p>"
	      set bLogLineHandled 1
	      continue
	    }
      }
    }
    
    ##################################################################################################################################
    # Check for "1024 FYI " in logline and handle if true
    if {[regexp {\s+\d+\s\S+\s\S+\s\S+:\s1024 FYI\s.*}  $sLogLine sMatch]} {
      
      # Table accessed Lines ignore
      if {[regexp {\s+\d+\s\S+\s\S+\s\S+:\s1024 FYI search_data: # ============================== #}  $sLogLine sMatch]} {
	      set bLogLineHandled 1
	      continue
      }

      # Table accessed message
      if {[info exists iOutFileTestCase]} {
	if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s1024 FYI search_data: # TABLE_ACCESSED :: (.*)  #}  $sLogLine sMatch sTimeStamp sTableMsg]} {
	      puts $iOutFileTestCase "<P $sPStyle>$sTimeStamp: <span style=\"color:#CC0099\"; background-color:#000000>Table Access: $sTableMsg</span></p>"
	      set bLogLineHandled 1
	      continue
	}
      }
          
      # Table dump name
      if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s1024 FYI dump_table: # ====== Results for: -name: \[(.*)\]}  $sLogLine sMatch sTimeStamp sTableName]} {
	      puts $iOutFileTestCase "<P $sPStyle>$sTimeStamp: <span style=\"color:#CC0099\">Table Dump Name: $sTableName</span></p>"
	      set bLogLineHandled 1
	      continue
      }
      
      # Table dump columns
      if {!$bLogLineHandled} {
	if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s1024 FYI dump_table: # ====== (.*)}  $sLogLine sMatch sTimeStamp sTableColumns]} {
	      puts $iOutFileTestCase "<P $sPStyle>$sTimeStamp: <span style=\"color:#CC0099\">Table Dump Columns: $sTableColumns</span></p>"
	      set bLogLineHandled 1
	      continue
	}	
      }
      
      # Table dump rows
      if {!$bLogLineHandled} {
	if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s1024 FYI dump_table: # \D+ # number of rows: (.*)\.}  $sLogLine sMatch sTimeStamp sTableRows]} {
	      puts $iOutFileTestCase "<P $sPStyle>$sTimeStamp: <span style=\"color:#CC0099\">Table Dump Rows: $sTableRows</span></p>"
	      set bLogLineHandled 1
	      
	}
      }
      
      # Table dump content
      if {!$bLogLineHandled} {
	if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s1024 FYI dump_table: (.*)}  $sLogLine sMatch sTimeStamp sTableContent]} {
	      puts $iOutFileTestCase "<P $sPStyle>$sTimeStamp: <span style=\"color:#CC0099\">Table Dump Content: $sTableContent</span></p>"
	      set bLogLineHandled 1
	}
      }
      
      # Table create
      if {[info exists iOutFileTestCase]} {
	if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s1024 FYI create_table: (.*)}  $sLogLine sMatch sTimeStamp sTableContent]} {
	      puts $iOutFileTestCase "<P $sPStyle>$sTimeStamp: <span style=\"color:#CC0099\">Table Create: $sTableContent</span></p>"
	      set bLogLineHandled 1
	}
      }
    }

    ##################################################################################################################################
    # Check for "1036 DEBUG" in logline and handle if true
    if {[regexp {\s+\d+\s\S+\s\S+\s\S+:\s1036 DEBUG.*}  $sLogLine sMatch]} {
    
      # ARS DEBUG portprot report message
      if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s1036 DEBUG ars_report_msg: DEBUG::::::portprot::(.*)}  $sLogLine sMatch sTimeStamp sReportMsg]} {
	      puts $iOutFileTestCase "<P $sPStyle>$sTimeStamp: <span style=\"color:#000099\">DBG PORTPROT: $sReportMsg</span><br>"
	      set bLogLineHandled 1
	      continue
      }
      
      # ARS DEBUG TA report message
      if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s1036 DEBUG ars_report_msg: DBG_TA::::(.*)}  $sLogLine sMatch sTimeStamp sReportMsg]} {
	      puts $iOutFileTestCase "<P $sPStyle>$sTimeStamp: <span style=\"color:#000099\">DBG_TA: $sReportMsg</span><br>"
	      set bLogLineHandled 1
	      continue
      }
      
      # ARS DEBUG TA "no frames captured" report message
      if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s1036 DEBUG ars_report_msg: DBG_TA:::(llp_traffic_PCTA_stop_capture: )(-- No frames captured --)}  $sLogLine sMatch sTimeStamp sLlp sNoFrames]} {
	      puts $iOutFileTestCase "<P $sPStyle>$sTimeStamp: <span style=\"color:#000099\">DBG_TA: $sLlp </span><span style=\"color:#FFFFFF; background-color:#CC0000\">$sNoFrames</span><br>"
	      set bLogLineHandled 1
	      continue
      }
      
      # ARS DEBUG RES report message
      if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s1036 DEBUG ars_report_msg: DBG_RES:(.*)}  $sLogLine sMatch sTimeStamp sReportMsg]} {
	      puts $iOutFileTestCase "<P $sPStyle>$sTimeStamp: <span style=\"color:#000099\">DBG_RES: $sReportMsg</span><br>"
	      set bLogLineHandled 1
	      continue
      }
  
      # ARS DEBUG ALL message ignore
      if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s1036 DEBUG ars_report_msg: DBG_ALL:(.*)}  $sLogLine sMatch sTimeStamp sReportMsg]} {
	      #puts $iOutFileTestCase "<P $sPStyle>$sTimeStamp: <span style=\"color:#000099\">DBG_ALL: $sReportMsg</span><br>"
	      set bLogLineHandled 1
	      continue
      }
   
      # Other DEBUG messages
      if {$bLogLineHandled == 0} {
	if {[info exists iOutFileTestCase]} {
	  if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s1036 DEBUG (.*)}  $sLogLine sMatch sTimeStamp sReportMsg]} {
	      puts $iOutFileTestCase "<P $sPStyle>$sTimeStamp: <span style=\"color:#000099\">DEBUG: $sReportMsg</span><br>"
	      set bLogLineHandled 1
	      continue
	  }
	}
      }
    }	

    ##################################################################################################################################
    # Check for XML code, otherwise skip
    if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s+<(.*)}  $sLogLine sMatch sTimeStamp sXML]} {
      if {[string trim $sXML] != ""} {
    
	# XML <?xml version
	if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s+<\?xml version.*}  $sLogLine sMatch sTimeStamp]} {
		set bLogLineHandled 1
		continue
	}
	
	# XML <configuration-data
	if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s+<configuration-data.*}  $sLogLine sMatch sTimeStamp]} {
		set bLogLineHandled 1
		continue
	}
    
	# XML <runtime-data
	if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s+<runtime-data.*}  $sLogLine sMatch sTimeStamp]} {
		set bLogLineHandled 1
		continue
	}
	
	# XML <hierarchy name
	if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s+<hier.*}  $sLogLine sMatch sTimeStamp]} {
		set bLogLineHandled 1
		continue
	}
    
	# XML <instance
	if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s+<instance.*}  $sLogLine sMatch sTimeStamp]} {
		set bLogLineHandled 1
		continue
	}
	
	# XML <res-id name
	if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s+<res-id name="(.*)"\s\S+"\S+"\s\S+"\S+">(\S*)</res-id>}  $sLogLine sMatch sTimeStamp sParam sValue]} {
		puts $iOutFileTestCase "<P $sPStyle>$sTimeStamp: <span style=\"color:#660066\">XML: $sParam = $sValue</span></p>"
		set bLogLineHandled 1
		continue
	}
	
	# XML <hier-id name (3 params)
	if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s+<hier-id name="(.*)"\s\S+"\S+"\s\S+"\S+"\s\S+"\S+">(\S*)</hier-id>}  $sLogLine sMatch sTimeStamp sParam sValue]} {
		puts $iOutFileTestCase "<P $sPStyle>$sTimeStamp: <span style=\"color:#660066\">XML: $sParam = $sValue</span></p>"
		set bLogLineHandled 1
		continue
	}
    
	# XML <hier-id name (2 params)
	if {!$bLogLineHandled} {
	  if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s+<hier-id name="(.*)"\s\S+"\S+"\s\S+"\S+">(\S*)</hier-id>}  $sLogLine sMatch sTimeStamp sParam sValue]} {
		puts $iOutFileTestCase "<P $sPStyle>$sTimeStamp: <span style=\"color:#660066\">XML: $sParam = $sValue</span></p>"
		set bLogLineHandled 1
		continue    
	  }
	}	
	
	# XML parameter name
	if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s+<parameter name="(.*)"\s\S+"\S+"\s\S+"\S+">(\S*)</parameter>}  $sLogLine sMatch sTimeStamp sParam sValue]} {
		if {$sValue == "up"} {set sValue "</span><span style=\"background-color:#00CC00\">&nbsp;UP&nbsp;</span>"}
		if {$sValue == "down"} {set sValue "</span><span style=\"background-color:#FF0000\">&nbsp;DOWN&nbsp;</span>"}
		puts $iOutFileTestCase "$sTimeStamp: <span style=\"color:#660066\">XML: $sParam = $sValue</span><br>"
		set bLogLineHandled 1
		continue
	}
	
	# XML info name (3 params)
	if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s+<info name="(.*)"\s\S+"\S+"\s\S+"\s\S+.*">(\S*)<\/info>}  $sLogLine sMatch sTimeStamp sParam sValue]} {
		if {$sValue == "up"} {set sValue "</span><span style=\"background-color:#00CC00\">&nbsp;UP&nbsp;</span>"}
		if {$sValue == "down"} {set sValue "</span><span style=\"background-color:#FF0000\">&nbsp;DOWN&nbsp;</span>"}
		puts $iOutFileTestCase "$sTimeStamp: <span style=\"color:#660066\">XML: $sParam = $sValue</span><br>"
		set bLogLineHandled 1
		continue
	}
	
	# XML info name (2 params)
	if {!$bLogLineHandled} {
	  if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s+<info name="(.*)"\s\S+"\S+"\s\S+"\S+">(\S*)<\/info>}  $sLogLine sMatch sTimeStamp sParam sValue]} {
		if {$sValue == "up"} {set sValue "</span><span style=\"background-color:#00CC00\">&nbsp;UP&nbsp;</span>"}
		if {$sValue == "down"} {set sValue "</span><span style=\"background-color:#FF0000\">&nbsp;DOWN&nbsp;</span>"}
		puts $iOutFileTestCase "$sTimeStamp: <span style=\"color:#660066\">XML: $sParam = $sValue</span><br>"
		set bLogLineHandled 1
		continue
	  }
	}
	
	# XML info name (1 params)
	if {!$bLogLineHandled} {
	  if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s+<info name="(.*)"\s\S+"\S+">(\S*)<\/info>}  $sLogLine sMatch sTimeStamp sParam sValue]} {
		if {$sValue == "up"} {set sValue "</span><span style=\"background-color:#00CC00\">&nbsp;UP&nbsp;</span>"}
		if {$sValue == "down"} {set sValue "</span><span style=\"background-color:#FF0000\">&nbsp;DOWN&nbsp;</span>"}
		puts $iOutFileTestCase "$sTimeStamp: <span style=\"color:#660066\">XML: $sParam = $sValue</span><br>"
		set bLogLineHandled 1
		continue
	  }
	}
	
	# XML node name
	if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s+<node name="(.*)"\s\S+"\S*">}  $sLogLine sMatch sTimeStamp sValue]} {
		puts $iOutFileTestCase "$sTimeStamp: <span style=\"color:#990066\">XML: ---- Node = $sValue</span><br>"
		set bLogLineHandled 1
		continue
	}
	
	# XML end node
	if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s+</node>}  $sLogLine sMatch sTimeStamp]} {
		puts $iOutFileTestCase "$sTimeStamp: <span style=\"color:#990066\">XML: ---- Node End</span><br>"
		set bLogLineHandled 1
		continue
	}
	
	# XML </configuration-data
	if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s+</configuration-data>}  $sLogLine sMatch sTimeStamp]} {
		set bLogLineHandled 1
		continue
	}
    
	# XML </runtime-data
	if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s+</runtime-data>}  $sLogLine sMatch sTimeStamp]} {
		set bLogLineHandled 1
		continue
	}
	
	# XML <hierarchy name
	if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s+</hierarchy>}  $sLogLine sMatch sTimeStamp]} {
		set bLogLineHandled 1
		continue
	}
    
	# XML <instance
	if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s+</instance>}  $sLogLine sMatch sTimeStamp]} {
		set bLogLineHandled 1
		continue
	}
	
	# XML automation
	if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s+automation::}  $sLogLine sMatch sTimeStamp]} {
		set bLogLineHandled 1
		continue
	}
      }
    }
    
    # TEST_PASS or TEST_FAIL
    if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s1012 TEST_PASS (.*)} $sLogLine sMatch sTimeStamp sTestResult]} {
      puts $iOutFileTestCase "<P $sPStyle>$sTimeStamp: <span style=\"color:#FFFFFF; background-color:#006600\">TEST_PASS</span>\
			      <span style=\"color:#FFFFFF; background-color:#00CC00\"> $sTestResult</span></p>"
      set bLogLineHandled 1
      continue
    }
    if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s1013 TEST_FAIL (.*)} $sLogLine sMatch sTimeStamp sTestResult]} {
      lappend lFailSteps $sStepNmb
      puts $iOutFileTestCase "<P $sPStyle>$sTimeStamp: <span style=\"color:#FFFFFF; background-color:#990000\">TEST_FAIL</span>\
			      <span style=\"color:#FFFFFF; background-color:#FF0000\"> $sTestResult</span></p>"
      set bLogLineHandled 1
      continue
    }
    if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s1000 TEST (.*)} $sLogLine sMatch sTimeStamp sTestResult]} {
      puts $iOutFileTestCase "<P $sPStyle>$sTimeStamp: <span style=\"color:#FFFFFF; background-color:#006600\">TEST</span>\
			      <span style=\"color:#FFFFFF; background-color:#00CC00\"> $sTestResult</span></p>"
      set bLogLineHandled 1
      continue
    }
	
    ##################################################################################################################################
    # Check for CLI, TL1 or T&D command, otherwise skip
    if {[regexp {\s+\d+\s\S+\s\S+\s\S+:\s+1001 NMI ars_report_msg:.*}  $sLogLine sMatch]} {
      # CLI Commands CMD
      if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s1001 NMI ars_report_msg: CMD::COM_CLI:COM_CLI: <CMD#> (.*)} $sLogLine sMatch sTimeStamp sCLI]} {
	      puts $iOutFileTestCase "<P $sPStyle>$sTimeStamp: <span style=\"background-color:#FFFF00\">CLI: $sCLI</span></p>"
	      set sPrevCLI $sCLI
	      set bLogLineHandled 1
	#     if {[regexp {.*reboot.*} $sCLI sMatch]} {
	#	puts $iOutFileAlarms "<P $sPStyle>$sTimeStamp: <span style=\"background-color:#FFFF00\">CLI: $sCLI</span></p>"
	#      }
	#      if {[regexp {.*forced_active.*} $sCLI sMatch]} {
	#		puts $iOutFileAlarms "<P $sPStyle>$sTimeStamp: <span style=\"background-color:#FFFF00\">CLI: $sCLI</span></p>"
	#      }
	      continue
	  }
	  
      # CLI Commands REPLY ignore line
      if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s1001 NMI ars_report_msg: REPLY::COM_CLI:COM_CLI:<REPLY#> (.*)} $sLogLine sMatch sTimeStamp sCLI]} {
	set bLogLineHandled 1
	continue
      }
      
      # TL1 send command
      if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s1001 NMI ars_report_msg: CMD::COM_TL1:com_send_cmd:(.*)} $sLogLine sMatch sTimeStamp sTL1Command]} {
	      puts $iOutFileTestCase "<P $sPStyle>$sTimeStamp: <span style=\"background-color:#CCCC99\">TL1 SEND: $sTL1Command</span></p>"
	      set bLogLineHandled 1
	      continue
      }
      
      # TL1 reply command
      if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s1001 NMI ars_report_msg: REPLY::COM_TL1:com_check_cmd:(.*)} $sLogLine sMatch sTimeStamp sTL1Command]} {
	      puts $iOutFileTestCase "<P $sPStyle>$sTimeStamp: <span style=\"background-color:#CCCC99\">TL1 REPLY: $sTL1Command</span></p>"
	      set bLogLineHandled 1
	      continue
      }
      
      # T&D command
      if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s1001 NMI ars_report_msg: CMD::TnD:(.*)} $sLogLine sMatch sTimeStamp sTnDCommand]} {
	      puts $iOutFileTestCase "<P $sPStyle>$sTimeStamp: <span style=\"background-color:#00FFFF\">T&D: $sTnDCommand</span></p>"
	      set bLogLineHandled 1
	      continue
      }
    }

    # VOID report message
    if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s1014 TEST_VOID apme_ars_report_msg: (.*)}  $sLogLine sMatch sTimeStamp sReportMsg]} {
	    puts $iOutFileTestCase "<P $sPStyle>$sTimeStamp: <span style=\"color:#FFFFFF; background-color:#CC0000\">ERROR: $sReportMsg</span></p>"
	    set bLogLineHandled 1
	    continue
    }

    # TP_TestTrue Failing
    if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s+test TP_TestTrue\s(.*)}  $sLogLine sMatch sTimeStamp sTest]} {
	    puts $iOutFileTestCase "<P $sPStyle>$sTimeStamp: <span style=\"color:#FFFFFF; background-color:#CC0000\">ERROR: $sTest</span></p>"
	    set sStepTcl [expr $sStepNmb + 1]
	    puts $iOutFileTestCase "<a name=\"TCL$sStepTcl\"></a>"
	    lappend lTclErrors $sStepNmb
	    set bLogLineHandled 1
	    continue
    }
    
    # TP_Test (PASS/FAIL)
    if {!$bLogLineHandled} {
      if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s+test (TP_Test\S+)\s(.*)}  $sLogLine sMatch sTimeStamp sTP sTest]} {
	    puts $iOutFileTestCase "<P $sPStyle>$sTimeStamp: <span style=\"color:#FFFFFF; background-color:#0000FF\">${sTP}</span>\
				    <span style=\"color:#FFFFFF; background-color:#3366FF\"> $sTest</span></p>"
	    set bLogLineHandled 1
	    continue
      }
    }
    
    # TP_PROC 
    if {!$bLogLineHandled} {
      if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s+1025 TP_PROC (.*)}  $sLogLine sMatch sTimeStamp sTProc]} {
	    puts $iOutFileTestCase "<P $sPStyle>$sTimeStamp: <span style=\"color:#000000; background-color:#FFCCCC\">TP_PROC: ${sTProc}</span></p>"
	    set bLogLineHandled 1
	    continue
      }
    }
    
    # TP_Test (part of step)
    if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s+test TP_Test part of step.*}  $sLogLine sMatch sTimeStamp]} {
	    set bLogLineHandled 1
	    continue
    }
    
    ##################################################################################################################################
    # Check for "1002 WARNING" in logline and handle if true
    if {[regexp {\s+\d+\s\S+\s\S+\s\S+:\s1002 WARNING.*} $sLogLine sMatch]} {
      
      # WARNING report message
      if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s1002 WARNING ars_report_msg: WARNING::(.*)}  $sLogLine sMatch sTimeStamp sReportMsg]} {
	      puts $iOutFileTestCase "<P $sPStyle>$sTimeStamp: <span style=\"color:#000000; background-color:#FFCCFF\">WARNING: $sReportMsg</span></p>"
	      set bLogLineHandled 1
	      continue
      }
      
      # WARNING TP_Test report message
      if {!$bLogLineHandled} {
	if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s1002 WARNING (.*)}  $sLogLine sMatch sTimeStamp sReportMsg]} {
	      puts $iOutFileTestCase "<P $sPStyle>$sTimeStamp: <span style=\"color:#000000; background-color:#FFCCFF\">WARNING: $sReportMsg</span></p>"
	      set bLogLineHandled 1
	      continue
	}
      }
    }
    
    ##################################################################################################################################
    # Check for "KILLING SUPERBATCH"

    if {!$bLogLineHandled} {
       if {[info exists iOutFileTestCase]} {
	  if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:.*(KILLING SUPERBATCH).*}  $sLogLine sMatch sTimeStamp sReportMsg]} {
	      puts $iOutFileTestCase "<P $sPStyle>$sTimeStamp: <span style=\"color:#FFFFFF; background-color:#CC0000\">ERROR: $sReportMsg</span></p>"
	      set bLogLineHandled 1
	      set sFile "${sDirHtml}/PassFailVoid.html"
	      exec /bin/sh -c "sed -i '/<body>/a <h1 style=\"color:red\">BATCH KILLED</h1>' $sFile"
	      set bBatchAborted 1
	      continue
	  }
	}
      }
    
    ##################################################################################################################################
    # Check for "1003 ERROR" in logline and handle if true
    if {[regexp {\s+\d+\s\S+\s\S+\s\S+:\s1003 ERROR.*} $sLogLine sMatch]} {

      # ERROR batch aborted (msg: BATCH WILL NOW BE ABORTED)
      if {!$bLogLineHandled} {
	if {[info exists iOutFileTestCase]} {
	  if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s1003 ERROR.*(BATCH WILL NOW BE ABORTED)}  $sLogLine sMatch sTimeStamp sReportMsg]} {
	      puts $iOutFileTestCase "<P $sPStyle>$sTimeStamp: <span style=\"color:#FFFFFF; background-color:#CC0000\">ERROR: $sReportMsg</span></p>"
	      set bLogLineHandled 1
	      set sFile "${sDirHtml}/PassFailVoid.html"
	      exec /bin/sh -c "sed -i '/<body>/a <h1 style=\"color:red\">BATCH ABORTED</h1>' $sFile"
	      set bBatchAborted 1
	      continue
	  }
	}
      }
      
      # ERROR report message
      if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s1003 ERROR ars_report_msg: ERROR::(.*)}  $sLogLine sMatch sTimeStamp sReportMsg]} {
	      puts $iOutFileTestCase "<P $sPStyle>$sTimeStamp: <span style=\"color:#FFFFFF; background-color:#CC0000\">ERROR: $sReportMsg</span></p>"
	      set bLogLineHandled 1
	      continue
      }
      
      # ERROR report message (no ::)
      if {!$bLogLineHandled} {
	if {[info exists iOutFileTestCase]} {
	  if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s1003 ERROR (.*)}  $sLogLine sMatch sTimeStamp sReportMsg]} {
	      puts $iOutFileTestCase "<P $sPStyle>$sTimeStamp: <span style=\"color:#FFFFFF; background-color:#CC0000\">ERROR: $sReportMsg</span></p>"
	      set bLogLineHandled 1
	      continue
	  }
	}
      }
    }
         
    # TimeDelay message
    if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s1009 APE TimeDelay: (.*)}  $sLogLine sMatch sTimeStamp sTimeDelay]} {
	  if {[info exists iOutFileTestCase]} {
	    puts $iOutFileTestCase "<P $sPStyle>$sTimeStamp: <span style=\"color:#000000; background-color:#CCFFFF\">TIMEDELAY: $sTimeDelay</span></p>"
	    set bLogLineHandled 1
	    continue
	  }
    }
    
    # Alarm message
    if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s+(\d+\/\d+\/\d+)\s(\d+:\d+:\d+)\s(.*)(\s+alarm\s+)(occurred|cleared)\s+(.*)}\
		      $sLogLine sMatch sTimeStamp sDate sTime sType s1 sOccCle sAlarmMsg]} {
	    puts $iOutFileTestCase "<a name=\"Alarm${sTime}-${sType}-$sOccCle\"></a>"
	    lappend lAlarms ${sTime}-${sType}-${sOccCle}
	    if {$sOccCle == "occurred"} {
	      set sBgColor "#FF0000"
	    } else {
	      set sBgColor "#00CC00"
	    }
	    puts $iOutFileTestCase "<P $sPStyle>$sTimeStamp: <span style=\"color:#FFFFFF; background-color:${sBgColor}\">\
				      ALARM:</span> $sDate $sTime $sType $s1 $sOccCle $sAlarmMsg</p>"
	    #puts $iOutFileAlarms "<P $sPStyle>$sTimeStamp: <span style=\"color:#FFFFFF; background-color:${sBgColor}\">\
				      ALARM:</span> $sDate $sTime $sType $s1 $sOccCle $sAlarmMsg</p>"
	    set bLogLineHandled 1
	    continue
    }
  
  if {[info exists iOutFileTestCase] && $bLogLineHandled == 0} {
    # Check for empty line
      if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s+(.*)}  $sLogLine sMatch sTimeStamp s1]} {
      set s1 [string map {" " ""} $s1]
      if {[string length $s1] <= 3 || [string match "*automation::*" $s1] || [string match "*Error : *" $s1]} {
	set bLogLineHandled 1
      } else {
        if {[regexp {\s+\d+\s\S+\s(\S+)\s\S+:\s+(.*)}  $sLogLine sMatch sTime sMsg]} {
	  if {[string trim $sMsg] == "invalid token"} {	  
	    puts $iOutFileTestCase "<P $sPStyle>$sTime: <span style=\"color:#FFFFFF; background-color:#CC0000\">ERROR: invalid token</span></p>"
	  } elseif {![string match "*[string trim [string range $sMsg 0 end-1]]*" $sPrevCLI]} {
	    if {![string match {*-\[1D*} $sMsg]} {
	      
		puts $iOutFileTestCase "<span style=\"color:#000000; background-color:#CCCCCC\">$sTime:</span> [string map {" " "&nbsp;"} $sMsg]<br>"
	      
	    }
	  }
	}
      }
    }
  }
}

#Handle last failed test case
if {[info exists iOutFileTestCase]} {
  set sNmbTstFail "TEST_FAIL: "
  foreach sStepNmb $lFailSteps {
    set sPrevStepNmb [expr $sStepNmb - 1]
    incr iStepCount
    if {[expr $iStepCount % 15] == 0} {
      append sNmbTstFail "<a href=\"${sTestCaseHandled}_${sTextCaseHandledNmb}_down.html#Step$sPrevStepNmb\"  target=\"down\">${sStepNmb}.B</a>&nbsp;<a href=\"${sTestCaseHandled}_${sTextCaseHandledNmb}_down.html#Step$sStepNmb\"  target=\"down\">${sStepNmb}.E</a>&nbsp;<br>"
    } else {
      append sNmbTstFail "<a href=\"${sTestCaseHandled}_${sTextCaseHandledNmb}_down.html#Step$sPrevStepNmb\"  target=\"down\">${sStepNmb}.B</a>&nbsp;<a href=\"${sTestCaseHandled}_${sTextCaseHandledNmb}_down.html#Step$sStepNmb\"  target=\"down\">${sStepNmb}.E</a>&nbsp;"
    }
  }
  set sTclErrors "TCL Errors: "
  foreach sStepNmb $lTclErrors {
    set sStepTcl [expr $sStepNmb + 1]
    append sTclErrors "<a href=\"${sTestCaseHandled}_${sTextCaseHandledNmb}_down.html#TCL$sStepTcl\"  target=\"down\">$sStepTcl</a>&nbsp;&nbsp;"
  }
  set sAlarms "Alarms: "
  foreach sAlarmNmb $lAlarms {
    append sAlarms "<a href=\"${sTestCaseHandled}_${sTextCaseHandledNmb}_down.html#Alarm$sAlarmNmb\"  target=\"down\">$sAlarmNmb</a>&nbsp;&nbsp;"
  }
  puts $iOutFileFrameUp "$sNmbTstFail<br>"
  puts $iOutFileFrameUp "$sTclErrors<br>"
  puts $iOutFileFrameUp "$sAlarms<br>"

  #Call proc to check with HG who modified this ATC the last time
  if {$bHgOk} {
    set lHgValues [pHgCheckAtc $sTestCaseDirHandled]
    if {[llength $lHgValues] > 0} {
      puts $iOutFileFrameUp "ATC Last Modified: [lindex $lHgValues 0] on [lindex $lHgValues 1] with msg \"[lindex $lHgValues 2]\""
    }
  }
  close $iOutFileFrame
  close $iOutFileFrameUp
}


# Close files
close $iLogFileId
if {[info exists iOutFileTestCase]} {
  close $iOutFileTestCase
}
#Remove META refresh tag via sed
if {$sAtc == "" && $bOnlyParse == 0} {
  set sFile "${sDirHtml}/TiOkInfo.html"
  exec /bin/sh -c "sed -i '/<meta/d' $sFile"
  if {$bBatchAborted == 0} {
    set sFile "${sDirHtml}/PassFailVoid.html"
    exec /bin/sh -c "sed -i '/<meta/d' $sFile"
  }
}
  puts ""

