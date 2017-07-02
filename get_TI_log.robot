*** Settings ***
Suite Setup       init test env
Suite Teardown    clean test env
#Resource
#Variables
Library           SSHLibrary
Library           DebugLibrary
#force tags


*** Test Cases ***

download TI logs
    log to console    \nstart download log for version ${version} batch ${batch}
    get logs via SCP    ${version}/${batch}



*** Keywords ***

get logs via SCP
    [arguments]    ${rmt_path}
    open connection    ${server['ip']}
    login    ${server['username']}    ${server['passwd']}
    get file    ${rmt_path}/apelogs/TS_focus.log1.gz    ${local_path}/apelogs/TS_focus.log1.gz

    get file    ${rmt_path}/*.html    ${local_path}\\
    run keyword and ignore error    get file    ${rmt_path}/apelogs/Logs/*.html    ${local_path}\\apelogs\\Logs\\


init test env
    ${server}    create dictionary    ip=172.21.128.21    username=rmtlab    passwd=rmtlab
    ${local_path}    set variable    d:/TI_logs/${version}__${batch}
    set suite variable    ${server}
    set suite variable     ${local_path}


clean test env
    Close All Connections