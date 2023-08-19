@echo off
@REM Starts FAST python server
@REM Starts ngrok tunnel (forwards ngrok line to local)
@REM Starts RabbitMQ Broker
@REM Starts Celery Task Executor with concurrency=1 and pool=solo

@REM start cmd.exe /k "cd N:\Desktop\projects\auto-candidate\source && python -m uvicorn server:app"

@REM start cmd.exe /k "cd N:\Desktop\projects\auto-candidate\source && ngrok http --subdomain=autocandidate localhost:8000"

start cmd.exe /k "cd N:\Program Files\RabbitMQ Server\rabbitmq_server-3.12.2\sbin && timeout 5 && .\rabbitmq-server.bat"

@REM start cmd.exe /k "cd N:\Desktop\projects\auto-candidate\source && celery -A worker worker --loglevel=INFO --concurrency=1 --pool=solo"
