@echo off
echo ========================================================
echo   GENERATING PUBLIC LINK (NO ACCOUNT NEEDED)
echo ========================================================
echo.
echo NOTE: You might be asked to input a password on the website.
echo The password is the IP Address shown below.
echo.
curl -s https://loca.lt/mytunnelpassword
echo.
echo.
echo ========================================================
echo   YOUR PUBLIC LINK IS BELOW (Copy and Paste in Chrome)
echo ========================================================
echo.
lt --port 5000
pause
