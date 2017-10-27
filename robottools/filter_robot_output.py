#!/usr/bin/env python
"""
    filter output.xml to get necessary test commands
    
    usage:
        filter_robot_output.py /tmp/RIDEIfzlnJ.d/output.xml
      
    return:
        a result file named output.xml.filter will be gotten
      
    History:
        Jan 9th 2014: designed by chunyagu

"""
import re

HIERARCHY_SYNTAX_MAP = {
    'SUITE_START': ['SUITE>> ',['id','name'],'<suite source=".*" id="(.*)" name="(.*)">'],
    'TEST_START' : ['TEST>> ',['id','name'],'<test id="(.*)" name="(.*)">'],
    'SETUP':       ['SETUP>> ',['name'],'<kw type="setup" name="(.*)">'],
    'TEARDOWN'  :  ['TEARDOWN>> ',['name'],'<kw type="teardown" name="(.*)">'],
    'SUITE_END' :  ['SUITE>> ',['status','info'],'<status status="(\w+)" [^>]*>(.*)</status>(\r|\n)+</suite>'],
    'TEST_END'  :  ['TEST>> ',['status','info'],'<status status="(\w+)".*">(.*)</status>.*</test>']
}

TYPE_SYNTAX_MAP = {
    'CLI' : ['  ','<msg[^>]+level="INFO">&lt;.*?&gt;CLI CMD &gt;&gt; *(.*?)&lt;/span&gt;'],
    'TL1' : ['  ','<msg[^>]+level="INFO">&lt;.*?&gt;TL1 CMD &gt;&gt; *(.*?)&lt;/span&gt;'],
    'PCTA': ['  ','<msg[^>]+level="INFO">&lt;.*?&gt;PCTA CMD &gt;&gt; *(.*?)&lt;/span&gt;'],
    'SNMP': ['  ','<msg[^>]+level="INFO">&lt;.*?&gt;SNMP REPLY&lt;&lt; *(.*?)&lt;/span&gt;']
}

PROCESS_STATUS = {
    'SUITE_LAYER': 0,
    'TEST_LAYER': 0,
    'SETUP_LAYER': 0,
    'TEARDOWN_LAYER': 0, 
    'KEYWORD_LAYER': 0      
}

CHECK_STATUS = False
STATUS_LINE = ""
LAST_COMMAND = ""
CURRENT_LINE = ""
CURRENT_COMMAND_TYPE = ""

def check_kw_layer (line):
    """
      check if current line is in setup or teardown for indent numbers
    """
    syntax_kw_start = '<kw type="(setup|kw|teardown){1}" name=".*">'
    syntax_kw_end = '</kw>'

    if re.search(syntax_kw_start,line) :  
        PROCESS_STATUS['KEYWORD_LAYER']+= 1
        if re.search('<kw type="setup" name=".*">',line) :
            PROCESS_STATUS['SETUP_LAYER'] = 1

        if re.search('<kw type="teardown" name=".*">',line) :
            PROCESS_STATUS['TEARDOWN_LAYER'] = 1 
         
                      
    elif re.search(syntax_kw_end,line) :
        PROCESS_STATUS['KEYWORD_LAYER']-= 1         
        if PROCESS_STATUS['KEYWORD_LAYER'] == 0 :
            PROCESS_STATUS['SETUP_LAYER'] = 0 
            PROCESS_STATUS['TEARDOWN_LAYER'] = 0 
        

    
def print_hierarchy_start_info (line,file_handler):
    """
    record SUITE and TEST info
    """
    info = re.search(HIERARCHY_SYNTAX_MAP['SUITE_START'][2] , line) 
    if info :
        layer_list = info.group(1).split("-")
        PROCESS_STATUS['SUITE_LAYER'] = len(layer_list)-1
        prefix = "  "*PROCESS_STATUS['SUITE_LAYER']+HIERARCHY_SYNTAX_MAP['SUITE_START'][0]
        file_handler.writelines(prefix+info.group(2)+"\n" )
        info = None
        return True

    info = re.search(HIERARCHY_SYNTAX_MAP['TEST_START'][2] , line)
    if info :
        layer_list = info.group(1).split("-")
        PROCESS_STATUS['TEST_LAYER'] = len(layer_list)-1
        prefix = "  "*PROCESS_STATUS['TEST_LAYER']+HIERARCHY_SYNTAX_MAP['TEST_START'][0]
        file_handler.writelines(prefix+info.group(2)+"\n" )
        info = None
        return  True
    info = re.search(HIERARCHY_SYNTAX_MAP['SETUP'][2] , line)    
    if info :
        if PROCESS_STATUS['TEST_LAYER'] != 0 :
            indent = PROCESS_STATUS['TEST_LAYER'] + 1
        elif  PROCESS_STATUS['SUITE_LAYER'] != 0 :
            indent =  PROCESS_STATUS['SUITE_LAYER'] + 1
        else :
            indent = 0
        prefix = "  "*indent+HIERARCHY_SYNTAX_MAP['SETUP'][0]
        file_handler.writelines(prefix+info.group(1)+"\n" )
        info = None
        return  True  
    info = re.search(HIERARCHY_SYNTAX_MAP['TEARDOWN'][2] , line)       
    if info :
        if PROCESS_STATUS['TEST_LAYER'] != 0 :
            indent = PROCESS_STATUS['TEST_LAYER'] + 1
        elif  PROCESS_STATUS['SUITE_LAYER'] != 0 :
            indent =  PROCESS_STATUS['SUITE_LAYER'] + 1
        else :
            indent = 0
        prefix = "  "*indent+HIERARCHY_SYNTAX_MAP['TEARDOWN'][0]
        file_handler.writelines(prefix+info.group(1)+"\n" )
        info = None
        return  True                         
    return False
    
def print_hierarchy_end_info (line,file_handler):
    """
    record SUITE and TEST status
    """
    global CHECK_STATUS, STATUS_LINE
    if re.search ('<status status="\w+" .*>.*',line) :
        STATUS_LINE = STATUS_LINE + line
        CHECK_STATUS = True
        return False
    if CHECK_STATUS and not re.search ('</(kw|test|suite)>',line) :
        STATUS_LINE = STATUS_LINE + line
        return False
    
    if CHECK_STATUS and re.search ('</(kw)>',line):
        STATUS_LINE = ""
        CHECK_STATUS = False
        return False
        
    if CHECK_STATUS and re.search ('</suite>',line): 
        CHECK_STATUS = False
        STATUS_LINE = STATUS_LINE + line
        info = re.search(HIERARCHY_SYNTAX_MAP['SUITE_END'][2], STATUS_LINE, re.S)
        if info :
            prefix = "  "*PROCESS_STATUS['SUITE_LAYER']+HIERARCHY_SYNTAX_MAP['SUITE_END'][0]
            file_handler.writelines(prefix+info.group(1)+"\n" )
            info = None
            PROCESS_STATUS['SUITE_LAYER']-= 1        
            return True                          
        
    if CHECK_STATUS and re.search ('</test>',line):
        CHECK_STATUS = False
        prefix = "  "*PROCESS_STATUS['TEST_LAYER']+HIERARCHY_SYNTAX_MAP['TEST_END'][0]
        PROCESS_STATUS['TEST_LAYER'] = 0
        STATUS_LINE = STATUS_LINE + line
        info = re.search(HIERARCHY_SYNTAX_MAP['TEST_END'][2], STATUS_LINE, re.S)     
        if info :
            file_handler.writelines(prefix+info.group(1)+"\n" )
            info = None
            return True    
    return False    
    
    
def print_test_info (line,file_handler,command_type) :
    """
    record test command executed
    """
    global LAST_COMMAND, CURRENT_LINE, CURRENT_COMMAND_TYPE
    if PROCESS_STATUS['TEST_LAYER'] != 0 :
        indent_num = PROCESS_STATUS['TEST_LAYER'] + 1
        if PROCESS_STATUS['SETUP_LAYER'] or PROCESS_STATUS['TEARDOWN_LAYER'] :
            indent_num+= 1
    elif  PROCESS_STATUS['SUITE_LAYER'] :
        indent_num = PROCESS_STATUS['SUITE_LAYER'] + 1
        if PROCESS_STATUS['SETUP_LAYER'] or PROCESS_STATUS['TEARDOWN_LAYER'] :
            indent_num+= 1  
    else :
        indent_num = 0 
        
    is_target_command = False    

    if CURRENT_LINE == "" :
        for item in command_type :
            prefix,syntax = TYPE_SYNTAX_MAP[item.upper()]
            matched = re.search(syntax,line)
            if matched :
                CURRENT_COMMAND_TYPE = item.upper()
                if not re.search("</msg>",line) :
                    CURRENT_LINE = CURRENT_LINE + line
                else :
                    is_target_command = True    
                break
            else :
                continue
    else :
        if not re.search("</msg>",line) :
            CURRENT_LINE = CURRENT_LINE + line
            return False 
        else :
            CURRENT_LINE = CURRENT_LINE + line
            prefix,syntax = TYPE_SYNTAX_MAP[CURRENT_COMMAND_TYPE]
            matched = re.search(syntax+"</msg>",CURRENT_LINE,re.S)
            CURRENT_COMMAND_TYPE = ""
            if not matched :
                print "target line can not be matched by: "
                print "'"+syntax+"</msg>'"
                print CURRENT_LINE
                print "\n"
                return False    
            else :
                is_target_command = True
          

    if is_target_command :                                         
        current_command = matched.group(1).replace(" \r","").replace(" \n","").replace("</msg>","")        
        if current_command != LAST_COMMAND :
            lines = current_command.split("\n")
            tidy_command = ""
            for current_line in lines :
                tidy_command = tidy_command + prefix*indent_num + current_line +"\n"
            file_handler.writelines( tidy_command)

        LAST_COMMAND = current_command
        CURRENT_LINE = ""
        return True
    else :
        return False
    
        
def filter_log (file_name,info_type) :
    """
    main function to check and record each line from input file
    """
    
    # if info_type was given, users only care about specific commands in it
    # or filter and write all commands defined in TYPE_SYNTAX_MAP to result file
    filter_dict = {}  
    if info_type != None :
        for type in info_type :
            if TYPE_SYNTAX_MAP.has_key(type) :
                filter_dict[type] = TYPE_SYNTAX_MAP[type]
    else :
        filter_dict = TYPE_SYNTAX_MAP
        
        
    with open(file_name,'r') as file_handler:
        data = file_handler.readlines() 

    file_handler_write = open(file_name+'.filter.txt','w')  
    for line in data :      
        print_hierarchy_end_info (line,file_handler_write)
        if not CHECK_STATUS :
            check_kw_layer (line)
            if print_test_info (line,file_handler_write,filter_dict.keys()):
                continue
            if print_hierarchy_start_info (line,file_handler_write):
                continue       
                    
    file_handler_write.close()        
     
                
if __name__ == '__main__' :

    import sys, time
    if "-h" in sys.argv or "--help" in sys.argv :
        print " filtering output.xml to get necessary test commands"
        print " supported commands: CLI/TL1/SNMP/PCTA"
        print ""
        print " calling example for filter all supported command:"
        print " $ROBOTREPO/LIBS/LOG/filter_robot_output.py /home/auto/output.xml"
        print ""
        print " calling example for filter cared command only:"   
        print " $ROBOTREPO/LIBS/LOG/filter_robot_output.py /home/auto/output.xml CLI"
        print " $ROBOTREPO/LIBS/LOG/filter_robot_output.py /home/auto/output.xml CLI PCTA"
        exit(0)

    if sys.argv[2:] :
        filter_type_list = sys.argv[2:]
    else :
        filter_type_list = None

    filter_log (sys.argv[1],filter_type_list)
    print "CLI filter File : " + sys.argv[1] + ".filter.txt"



