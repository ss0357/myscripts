
EverythingExe := "D:\mytools\Everything\Everything.exe"

F1::    ; 打开/最小化/激活 Everything
IfWinActive, ahk_class EVERYTHING ; 窗口当前活跃，关闭（隐藏到后台了）。
{
    WinClose
    return
}
DetectHiddenWindows, On
IfWinNotExist, ahk_class EVERYTHING_TASKBAR_NOTIFICATION ; 未启动。
{
    Run, %EverythingExe%,, Max
    WinWait, ahk_class EVERYTHING_TASKBAR_NOTIFICATION,, 2
    if (ErrorLevel = 1)
    {
        MsgBox, 4112, 错误, Everything启动失败。
        return
    }
}
IfWinNotExist, ahk_class EVERYTHING ; 已启动但不存在窗口，说明在后台。
{
    PostMessage, 0x312, 0, 0x700000,, ahk_class EVERYTHING_TASKBAR_NOTIFICATION
    WinWait, ahk_class EVERYTHING,, 1
}
IfWinNotActive, ahk_class EVERYTHING ; 窗口不活跃，激活。
    WinActivate
return