@echo off
REM === 進階版一鍵打包 launcher.py ===

REM 檢查 app.py 是否存在
if not exist "app.py" (
    powershell -Command "Add-Type -AssemblyName PresentationFramework; [System.Windows.MessageBox]::Show('app.py 不存在，請確認檔案位置','錯誤','OK','Error')"
    exit /b
)

REM 安裝 PyInstaller（如果尚未安裝）
python -m pip install --upgrade pyinstaller

REM 打包成單一 exe，不顯示命令列視窗
pyinstaller --onefile --noconsole launcher.py

REM 提示完成
echo.
echo ===== 打包完成 =====
echo 可執行檔位於 dist\launcher.exe
pause
