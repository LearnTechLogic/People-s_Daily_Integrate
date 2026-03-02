@echo off
echo 正在打包人民日报爬取工具...
echo.

REM 使用 PyInstaller 打包 gui.py
pyinstaller --onefile --windowed --name "人民日报爬取工具" --icon=NONE gui.py

echo.
echo 打包完成！可执行文件位于 dist 目录下
pause
