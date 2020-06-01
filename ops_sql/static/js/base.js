
// 按回车键时，等于按了按钮
function KeyDown()
{
  if (event.keyCode == 13)
  {
    event.returnValue=false;
    event.cancel = true;
    $('#seabtn').click();
  }
}

