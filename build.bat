@echo off

pyinstaller -D -w -i ..\chrom_helper3.ico --workpath .\build\build --distpath .\build\dist --specpath .\build --name ChromHelper3 .\main.py
