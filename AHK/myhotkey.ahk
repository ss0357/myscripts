;replace CapsLock to LeftEnter; CapsLock = Alt CapsLock
$CapsLock::Enter

LAlt & Capslock::SetCapsLockState, % GetKeyState("CapsLock", "T") ? "Off" : "On"
~LWin Up:: return

; # 号代表 Win 键；
; ! 号代表 Alt 键；
; ^ 号代表 Ctrl 键；
; + 号代表 shift 键；
; :: 号(两个英文冒号)起分隔作用；
; run，非常常用 的 AHK 命令之一;
; ; 号代表 注释后面一行内容；

; 温馨提示： 以下几个系统默认的 Win 快捷键：
; Win + E：打开资源管理器；
; Win + D：显示桌面；
; Win + F：打开查找对话框；
; Win + R：打开运行对话框；
; Win + L：锁定电脑；
; Win + PauseBreak：打开系统属性对话框;
; Win + Q: 本地文件/网页等搜索;
; Win + U: 打开控制面板－轻松使用设置中心;

#q::Run https://www.baidu.com/s?wd=%Clipboard%


; Set this path to your tools directory
tools := "D:\mytools"

; Set screen resolutions
#^1::  Run "D:\mytools\displaychange2\dc2.exe" -primary
#^2::  Run "D:\mytools\displaychange2\dc2.exe" -secondary
#^0::  Run "D:\mytools\displaychange2\dc2.exe" -extend

#^d::  Run "D:\mytools\myscripts\change_wallpaper.bat"


Activate(t)
{
  IfWinActive,%t%
  {
    WinMinimize
    return 1
  }

  IfWinExist,%t%
  {
    WinActivate
    return 1
  }
  return 0
}


ActivateAndOpen(t,p)
{
  if Activate(t)==0
  {
    Run %p%
    WinActivate
    return
  }
}

!x::ActivateAndOpen("ahk_class Xshell::MainFrame_0","C:\Program Files (x86)\NetSarang\Xshell 5\Xshell.exe")
!s::ActivateAndOpen("ahk_exe sublime_text.exe","D:\mytools\Sublime Text Build 3126\sublime_text.exe")
!c::ActivateAndOpen("ahk_class Chrome_WidgetWin_1","C:\Users\songsonl\AppData\Local\Google\Chrome\Application\chrome.exe")
!m::ActivateAndOpen("ahk_class TFoxMainFrm.UnicodeClass","D:\Program Files\Foxmail 7.2\Foxmail.exe")
!r::ActivateAndOpen("ahk_class VirtualConsoleClass","D:\mytools\cmder\Cmder.exe")
!e::ActivateAndOpen("ahk_class TTOTAL_CMD","C:\totalcmd\TOTALCMD64.EXE")


#W::
  OutputVar := StrReplace(Clipboard, "/home/songsonl/tmp", "D:/tmp3")
  Run %OutputVar%
  return





;------------------------------------------------------------ 
; For ererything
;------------------------------------------------------------ 

EverythingExe := "D:\mytools\Everything\Everything.exe"

!t::    ; 打开/最小化/激活 Everything
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



Loop
{
    ifWinExist, This is an unregistered copy
    {
      WinClose
    }
    sleep, 250
}


