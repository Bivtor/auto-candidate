from partial_add_seq import *
from paths import *
from masstext import *
from celery import Celery
import asyncio

app = Celery('worker', broker='amqp://guest:guest@127.0.0.1:5672')
app.conf.result_backend = 'rpc://'

# System Startup:

# python -m celery -A worker worker --loglevel=INFO --concurrency=1 --pool=solo
# sudo rabbitmq-server
# sudo rabbitmqctl status
# sudo rabbitmqctl stop
# uvicorn server:app --reload
# python -m uvicorn server:app --reload
# ngrok http --subdomain=autocandidate localhost:8000


@app.task()
def open_link_task(data: dict):
    # OPEN chrome
    cmd = OPEN_CMD_LINK.format(data["link"])
    if os.system(cmd) == 0:
        logger.info(f"Successfully Opened Link: {data.get('link')}")
    else:
        logger.info(f"Failed to open link: {data.get('link')}")


@app.task()
def process_candidate_part1(data: dict):

    # Turn back into Pydantic Model
    model_CD = candidateData(**data)

    # Await half add method
    loop = asyncio.get_event_loop()
    new_item_id = loop.run_until_complete(beginHalfAdd(model_CD))

    # If we have their monday ID then do part 2
    if new_item_id != None:
        # Log
        logger.info(
            f"{model_CD.name} - Submitting Resume add part 2 at: {new_item_id}")

        # Add Item ID to object
        model_CD.monday_id = new_item_id

        # Submit Finish Add Task
        result = process_candidate_part2.apply_async(
            args=(model_CD.dict(),), priority=2)

        # Await Task Submission Confirmation
        # result_output = result.wait(timeout=None, interval=0.5)

    # Log
    logger.info(f"{model_CD.name} - Add 1/2 Completed")

    return


@app.task()
def process_candidate_part2(data: dict):

    # De-serialize Pydantic Model
    model_CD = candidateData(**data)

    # Finish Half-Add Process
    loop = asyncio.get_event_loop()
    loop.run_until_complete(finishHalfAdd(model_CD))

    # Log
    logger.info(f"{model_CD.name} - Add 2/2 Completed")

    return


@app.task()
def test_mailtext(incoming_data: dict):

    # De-serialize Pydantic Model
    model_CD = Data(**incoming_data)

    # Send Test Mail/Text
    send_test_mailtext(model_CD)

    # Log
    logger.info(f"Finished Test Mail/Text Task")

    return


@app.task()
def send_group_mailtext(incoming_data: dict):

    # De-serialize Pydantic Model
    model_CD = Data(**incoming_data)

    # Send Test Mail/Text
    send_group_mail_function(model_CD)

    # Log
    logger.info(f"Finished Full Mail/Text Task")

    return
