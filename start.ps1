# Starts FAST python server
# Starts ngrok tunnel (forwards ngrok line to local)
# Starts RabbitMQ Broker
# Starts Celery Task Executor with concurrency=1 and pool=solo

# Change directory to the source folder
# Set-Location -Path 'N:\Desktop\projects\auto-candidate\source' -PassThru

# pause

# Start-Process -FilePath "notepad" -Wait -WindowStyle Maximized

# Start-Process "cmd.exe" -ArgumentList "/k cd 'N:\Desktop\projects\auto-candidate\source' && python -m uvicorn server:app" -NoNewWindow

# Start-Process "cmd.exe" -ArgumentList "/k cd 'N:\Desktop\projects\auto-candidate\source' && ngrok http --subdomain=autocandidate localhost:8000" -NoNewWindow

# Start-Process "cmd.exe" -ArgumentList "/k cd 'N:\Program Files\RabbitMQ Server\rabbitmq_server-3.12.2\sbin' && .\rabbitmq-server.bat" -NoNewWindow

# Start-Process "cmd.exe" -ArgumentList "/k cd 'N:\Desktop\projects\auto-candidate\source' && celery -A worker worker --loglevel=INFO --concurrency=1 --pool=solo" -NoNewWindow
