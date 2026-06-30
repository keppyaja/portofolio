@echo off

echo ========================================
echo Updating CyLab Stats...
echo ========================================

cd /d C:\Users\sukep\Documents\portofolio

C:\Users\sukep\AppData\Local\Python\pythoncore-3.14-64\python.exe scripts\update_stats.py

echo.
echo Finished at %date% %time%