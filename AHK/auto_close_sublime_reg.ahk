SetTitleMatchMode, 2

Loop
{
    ifWinExist, This is an unregistered copy ahk_class #32770
    {
      WinClose
    }
    ifWinExist, Sublime Text ahk_class #32770, Buy Now
    {
      WinClose
    }
    sleep, 250
}




