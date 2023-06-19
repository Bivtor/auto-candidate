@echo off


start cmd.exe /k "cd N:\Desktop\projects\auto-candidate\source && python -m uvicorn server:app"
start cmd.exe /k "cd N:\Desktop\projects\auto-candidate\source && ngrok http --subdomain=autocandidate localhost:8000"