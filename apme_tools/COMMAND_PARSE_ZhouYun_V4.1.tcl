######################################################################### Author : arunprabhu.sn@alcatel-lucent.com# Creation: 28th Apr 2010# Description: Parses out the TL1/CLI commands from the APME log file#              and stored the output file in the user home dir########################################################################proc printUsage { } {  puts {}  puts {USAGE:}  puts {======}  puts {}  puts { COMMAND_PARSE_V4.1.tcl -LogPath /home/folder1/folder/log.txt -StcLog <yes/no> -PctaLog <yes/no> -Alarms <yes/no> -Mnemonic ATC1,ATC2 -RemoveShow <yes/no> -Reply <yes/no>}  puts {}  puts {    Arguments:}  puts {}  puts {    -LogPath   <Log path>      Mandatory, Absolute path to the APME log file}  puts {}  puts {    -StcLog    <yes/no>        Optional, Default - no, Include STC related commands from the log file in the parsed output. }  puts {}  puts {    -PctaLog   <yes/no>        Optional, Default - no, Include PCTA related commands from the log file in the parsed output. }  puts {}  puts {    -Alarms    <yes/no>        Optional, Default - no, Include Alarms from the log file in the parsed output. }  puts {}  puts {    -Mnemonic  <List of Mnemonics>   Optional, Parses the commands for the specified mnemonic(s) only. }  puts {                                     Mnemonics without .ars extension, seperated by "," if more than one.}  puts {}  puts {    -RemoveShow <yes/no>             Optional, Default - no, Removes "Show/RTRC/ATC/CANC" commands in the parsed output. }  puts {}  puts {    -Reply <yes/no>                  Optional, Default - no, Include "Cmd replay/Traffic captured" in the parsed output.}  puts {}  puts {===========================You can mail to yun.c.zhou@alcatel-sbell.com.cn for your idea===========================}}set lValidArgList {-LogPath -StcLog -PctaLog -Alarms -Mnemonic -RemoveShow -Reply}if { [expr $argc % 2] } {  #puts "Error:  You must supply an even number of arguments"  printUsage  exit 1}array set aArgs $argv# Mandatory arg checkset mandatoryArgList {-LogPath}foreach argName $mandatoryArgList {  if { ![info exists aArgs($argName)] } {    puts "Error: $argName is required"    printUsage    exit 1  }}# Invalid arg checkforeach sThisArg [array names aArgs] {  if {[lsearch -exact $lValidArgList $sThisArg] < 0} {    puts "Invalid argument: $sThisArg"    printUsage    exit 1  }}# Invalid value check set valuecheckArgList {-StcLog -PctaLog -Alarms -RemoveShow -Reply}foreach argName $valuecheckArgList {  if { [info exists aArgs($argName)] } {    if { [expr [string match -nocase $aArgs($argName) "NO"] * \                [string match -nocase $aArgs($argName) "YES"]] } {      puts "Error: Invalid value for $argName, should be yes (or) no "      printUsage      exit 1    }  }}# Mnemonicset iInputList 0if { [info exists aArgs(-Mnemonic)] } {  set linputmnemoniclist [split $aArgs(-Mnemonic) ","]  set iInputList 1}# RemoveShowset iRemoveShow 0if { [info exists aArgs(-RemoveShow)] } {  set iRemoveShow 1}set iReply 0if { [info exists aArgs(-Reply)] } {  set iReply 1}# Input/Output LogPathset sLogFilePath $aArgs(-LogPath)set sOutfilepath [regsub {[A-Za-z_\-0-9]*.[a-z0-9]*$} $aArgs(-LogPath) ""]if {![info exists aArgs(-RemoveShow)] ||  [string match -nocase $aArgs(-RemoveShow) "NO"] } {  set iRemoveShow 0  } else {  set iRemoveShow 1} if {![info exists aArgs(-StcLog)] ||  [string match -nocase $aArgs(-StcLog) "NO"] } {  set StcLog "NO"  } else {  set StcLog "YES"} if {![info exists aArgs(-PctaLog)] || [string match -nocase $aArgs(-PctaLog) "NO"]} {  set PctaLog "NO"  } else {  set PctaLog "YES"} if {![info exists aArgs(-Alarms)] || [string match -nocase  $aArgs(-Alarms) "NO"]} {  set Alarms "NO"  } else {  set Alarms "YES"} if {![info exists aArgs(-Reply)] || [string match -nocase  $aArgs(-Reply) "NO"]} {  set iReply 0  } else { set iReply 1 }set bLine falseset bLinePCTA falseset parse_time [clock format [clock seconds] -format %d%h%Y_%I%M%S%p]set outfilename "filter_$sLogFilePath.txt"set outfilenameExec "exec_filter_$sLogFilePath.txt"#set outfilename "Commands_Parsed_$parse_time.txt"#set outfilenameExec "Exec_Commands_Parsed_$parse_time.txt"catch { set hLogFile [ open $sLogFilePath r ] } err if { !([ string first "file" $err ] > -1) } {   puts " \n Unable to Open the Log File $sLogFilePath"   puts " \n Getting the Error : $err "   exit 1 }catch { set hOutputFile  [ open $sOutfilepath$outfilename w+] } err if { !([ string first "file" $err] > -1)} {  puts " \n Unable to Open the File $sOutfilepath$outfilename"   puts " \n Getting the Error : $err "   exit 1}catch { set hOutputFileExec  [ open $sOutfilepath$outfilenameExec w+] } err if { !([ string first "file" $err] > -1)} {  puts " \n Unable to Open the File $sOutfilepath$outfilenameExec"   puts " \n Getting the Error : $err "   exit 1}set module ""set tc ""set actualorder ""set cmdonly ""set skipline 0puts " \n Parsing..." puts " \n This may take a few minutes depending on the log size..."   puts $hOutputFile "\n************************* COMMAND PARSER OUTPUT *****************************\n"puts $hOutputFile "Input Log file                        : $sLogFilePath \n"puts $hOutputFile "Output file with parsed commands      : $sOutfilepath$outfilename\n"puts $hOutputFile "Output file with Exec parsed commands : $sOutfilepath$outfilenameExec\n" puts $hOutputFile "\n\n[string repeat "*" 80]"puts $hOutputFile "---------------------------- Actual Execution Order -------------------------"puts $hOutputFile "[string repeat "*" 80]\n"if {!$iInputList} {  puts $hOutputFileExec "\n\n[string repeat "*" 100]"  puts $hOutputFileExec  "---------------------TL1 AND CLI COMMAND LIST IN THE ORDER OF EXECUTION ---------------"  puts $hOutputFileExec "[string repeat "*" 100]\n"}while { [gets $hLogFile line] != -1 } {    # Module  if {!$iInputList} {    if {[regexp {TS_Module:(.*)} $line match module]} {      puts $hOutputFile "$module"    }  }  # Testcase   if {$skipline} {     if {![regexp {Starting (.*.ars)} $line match tc]} {       continue     }   }  if {[regexp {Starting (.*.ars)} $line match tc]} {    if {!$iInputList} {      puts $hOutputFile "\n----------"      puts $hOutputFile "Test Case: $tc"      puts $hOutputFile "----------\n"    }    if {$iInputList} {      regexp {([a-zA-Z0-9_-]+).ars} $line match sAtcMnemonic      foreach mnemonic $linputmnemoniclist {        if {[string match $mnemonic $sAtcMnemonic]} {          puts $hOutputFile "\n----------"          puts $hOutputFile "Test Case: $tc"          puts $hOutputFile "----------\n"          set skipline 0          set iMnemonicindex [lsearch $linputmnemoniclist $sAtcMnemonic]          lreplace $linputmnemoniclist $iMnemonicindex $iMnemonicindex           break        } else {            set skipline 1        }       }    }  }  if {$skipline} {continue;}  # Alarm  if {[string match $Alarms "YES"]} {    if {[regexp {:MN,|:MJ,|:CR,|:CL,} $line]} {      regexp {:    (.*)} $line match alarm      set alarm [string trim $alarm]       puts $hOutputFile "ALARM: $alarm"    }  }  #PCTA log  if {[string match $PctaLog "YES"]} {    if {[regexp {ITF_BEGIN:::llp_traffic_[A-Z]*_issue_cmd.*-command {(.*)}[^\}]*$} $line sMatch Traffic]} {        set Traffic [string trim $Traffic]         puts $hOutputFile "PCTA: $Traffic"     }  }  #INFO::PC_TA_ETH_IMPL:ta_stop_capt_ip_packet:ITF_END:-ip_packet_received_l  if {[string match $PctaLog "YES"] && ($iReply == "1")} {    if {[regexp {PC_TA_ETH_IMPL:ta_.*:ITF_END:.*_received_l} $line sMatch Traffic]} {     set bLinePCTA true    }    if {[regexp {ITF_END:::llp_traffic_[A-Z]*_issue_cmd} $line sMatch Traffic]} {      if {$bLinePCTA} { set bLinePCTA false}    }  }   #STC log  if {[string match $StcLog "YES"]} {    if {[regexp {ITF_BEGIN:::llp_traffic_STC_issue_cmd.*-cmd {(.*)}[^\}]*$} $line sMatch Traffic]} {        set Traffic [string trim $Traffic]         puts $hOutputFile "STC: $Traffic"     }  }  #TEST result commands#  if {[regexp {TEST_FAIL} $line]} {#    set test_fail [string trim $line] #    puts $hOutputFile "##TEST-FAIL## $test_fail" #  }#  if {[regexp {TEST_PASS} $line]} {#    set test_pass [string trim $line] #    puts $hOutputFile "##TEST-PASS## $test_pass"#  }#  if {[regexp {ars_report_msg:\ ERROR} $line]} {#    set error_msg [string trim $line] #    puts $hOutputFile "##ERROR## $error_msg" #  }  set step ""  if {[regexp {.*(Step.*[0-9]+ :.*)} $line match step]} {    puts $hOutputFile "$step"   }  if {$iReply} {    if {[regexp {(REPLY::COM_CLI:)} $line]} {      if {$iRemoveShow} {        if {![regexp {^$|show|info} $line]} {          set bLine false        }       } else {         set bLine true        }    }    #DEBUG ars_report_msg: DBG_ALL:TRANS:COM_CLI:com_get_cmd_response:    #ITF_END ars_report_msg: ITF_END::    #INFORMATIONAL ars_report_msg: INFO    if {[regexp {(COM_CLI:com_)} $line] || [regexp {(ITF_END ars_report_msg)} $line]\|| [regexp {(INFORMATIONAL ars_report_msg)} $line] } {      if {$bLine} {set bLine false}    }     if {[regexp {(INFORMATIONAL ars_report_msg: INFO::::The reply recovered)} $line]} {       if {$iRemoveShow} {        if {![regexp {^$|ACT|CAN|RTRV|REPT} $line]} {          set bLine false        }      } else {          set bLine true        }    }    #ITF_BEGIN::com_tl1_syntax:tl1ParseTL1    if {[regexp {(INFO from proc read_sock)} $line]} {      if {$bLine} {set bLine false}    }   }  if {$bLine || $bLinePCTA} {    switch -exact -regexp -- $line {     {REPLY::COM_CLI:} {       set clisp [split $line "#"]       set cmd [lindex [split [lindex $clisp 1] ">"] 1]       set cmd [string trim $cmd]       puts $hOutputFile $cmd     }     {INFORMATIONAL ars_report_msg: INFO::::The reply recovered}  {     }     {PC_TA_ETH_IMPL:ta_.*:ITF_END:.*_received_l} {       regexp {.*received_l(.*)} $line match cmd       puts $hOutputFile $cmd     }     default {       regexp {([0-9]+ [a-zA-Z0-9]+ [0-9]+:[0-9]+:[0-9]+.[0-9]+ [0-9.]+:)(.*)} $line match timestamp cmd       puts $hOutputFile $cmd     }  }}  #TL1 CLI commands  if {[regexp {(:COM_CLI:|:COM_TL1:)} $line]} {    if {[regexp {(<CMD#>)} $line] } {      set clisp [split $line "#"]      set cmd [lindex [split [lindex $clisp 1] ">"] 1]      set cmd [string trim $cmd]       if {$iRemoveShow} {        if {![regexp {^$|show|info} $cmd]} {          puts $hOutputFile $cmd        }      } else {        puts $hOutputFile $cmd      }            if {!$iInputList} {        if {![regexp {^$} $cmd]} {          puts $hOutputFileExec $cmd        }      }    } elseif {[regexp {:COM_TL1:com_send_cmd:(.*)} $line match cmd]} {      if {![regexp {\;$} $cmd]} {        set cmd [string trim $cmd]         append cmd ";"        if {$iRemoveShow} {          if {![regexp {^$|ACT|CAN|RTRV|REPT} $cmd]} {            puts $hOutputFile $cmd          }        } else {          puts $hOutputFile $cmd        }        if {!$iInputList} {          if {![regexp {^$|ACT|CAN} $cmd]} {            puts $hOutputFileExec $cmd          }        }      } else {        if {$iRemoveShow} {          if {![regexp {^$|ACT|CAN|RTRV|REPT} $cmd]} {            puts $hOutputFile $cmd          }        } else {          puts $hOutputFile $cmd        }        if {!$iInputList} {          if {![regexp {^$|ACT|CAN} $cmd]} {            puts $hOutputFileExec $cmd          }        }      }    }  }}puts "\n************************* COMMAND PARSER OUTPUT *****************************"puts "Input Log file                                    : $sLogFilePath "puts "Output file with parsed commands                  : $sOutfilepath$outfilename"puts "Output file with parsed commands in order of exec : $sOutfilepath$outfilenameExec" puts "[string repeat "*" 80]"puts " \n Parsing complete.\n" close $hLogFileclose $hOutputFileclose $hOutputFileExec