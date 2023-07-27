from partial_add_seq import *
from paths import *
from celery import Celery
import asyncio

app = Celery('worker', broker='amqp://guest:guest@127.0.0.1:5672')
app.conf.result_backend = 'rpc://'
# celery -A worker worker --loglevel=INFO


@app.task()
def open_link_task(data: dict):
    # OPEN chrome
    cmd = 'open -a "Google Chrome"  \"{}\"'.format(data.get("link"))
    if os.system(cmd) == 0:
        logger.info(f"Successfully Opened Link: {data.get('link')}")
    else:
        logger.info(f"Failed to open link: {data.get('link')}")


@app.task()
def process_candidate_part1(data: dict):

    # De-serialize Pydantic Model
    model_CD = candidateData(**data)

    # Await half add method

    loop = asyncio.get_event_loop()
    loop.run_until_complete(beginHalfAdd(model_CD))

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
