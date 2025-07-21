@echo on
setlocal EnableDelayedExpansion
set PYTHONUNBUFFERED=1

:: Copy activate and deactivate scripts (both .bat and .sh)
for %%F in (activate deactivate) DO (
    if not exist %PREFIX%\etc\conda\%%F.d mkdir %PREFIX%\etc\conda\%%F.d
    copy %RECIPE_DIR%\%%F.bat %PREFIX%\etc\conda\%%F.d\%PKG_NAME%_%%F.bat
    copy %RECIPE_DIR%\%%F.sh  %PREFIX%\etc\conda\%%F.d\%PKG_NAME%_%%F.sh
)

:: Install the Python package
%PYTHON% -m pip install . --no-deps -vv
if errorlevel 1 exit 1