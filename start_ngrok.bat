@echo off
set "NGROK_PATH=c:\Users\user\Downloads\ngrok.exe"
set "DOMAIN=karry-unrueful-loutishly.ngrok-free.dev"
set "PORT=8080"

echo Starting ngrok for domain %DOMAIN% on port %PORT%...
"%NGROK_PATH%" http --domain=%DOMAIN% %PORT%
pause
