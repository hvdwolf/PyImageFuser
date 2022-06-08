@echo off

set VERSION=%1
REM @echo VERSION %VERSION%

IF "%VERSION%" == "" (
  @echo.
  @echo You need to provide the version
  @echo.
  exit /b
) ELSE (
  set VERSION=%1
)
set WWD=%cd%
echo %WWD%

cd ..\..

set RWD=%cd%
echo %RWD%

echo "Removing the previous build data"
REM del /s /q dist/*
REM del /s /q build/*
del *.spec
rmdir /s /q dist
rmdir /s /s build

echo "Creating the pyinstaller exe"
pyinstaller --onefile --noconsole PyImageFuser.py

@echo Copy docs, images, licenses and enfuse_ais
xcopy docs dist\docs\ /E /S
xcopy images dist\images\ /E /S
xcopy enfuse_ais dist\enfuse_ais\ /E /S
copy GPLv* dist

@echo Now create the zip file
cd dist
zip -r ..\PyImageFuser-%VERSION%-win-x86_64.zip *
cd ..
move PyImageFuser-%VERSION%-win-x86_64.zip %WWD%
cd %WWD%



