
import aiohttp
import logging
import asyncio
from enum import Enum
from typing import Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

# TODO config file
URL_SERVICE_1 = "http://127.0.0.1:5001/check_object?object_id={}"
URL_SERVICE_2 = "http://127.0.0.1:5002/check_object?object_id={}"

TOTAL_RETRIES = 3
RETRY_TIMEOUT = timedelta(seconds=1).total_seconds()
TOTAL_TIMEOUT = timedelta(seconds=15).total_seconds() # это timeout_seconds

logger = logging.getLogger("task_1")
logger.setLevel(logging.INFO)


class Response(Enum):
    Success = 1
    RetryAfter = 2
    Failure = 3


class ApplicationStatusResponse(Enum):
    Success = 1
    Failure = 2


@dataclass
class ApplicationResponse:
    application_id: str
    status: ApplicationStatusResponse
    description: str
    last_request_time: datetime
    retriesCount: Optional[int] 


async def get_application_status(service_url: str, identifier: str) -> Response:
    # Метод, возвращающий статус заявки
    url = service_url.format(identifier)

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    response_text = await response.text()
                    return Response[response_text]
                else:
                    logger.debug(f'Request failed with status code: {response.status}')
                    return Response.Failure
        except aiohttp.ClientError as e:
            logger.debug(f'An error occurred during request: {e}')
            return Response.Failure


async def get_application_status1(identifier: str) -> Response:
    # Метод, возвращающий статус заявки
    return await get_application_status(URL_SERVICE_1, identifier)


async def get_application_status2(identifier: str) -> Response:
    # Метод, возвращающий статус заявки
    return await get_application_status(URL_SERVICE_2, identifier)

async def retry_request(
    app_status_getter,
    getter_description: str,
    identifier: str,
    total_retries: int,
     # Не самое красивое решение, стоило бы это делать иначе, но времени уже мало
    status: dict
) -> ApplicationResponse:

    status["retries"] = 0

    while status["retries"] < total_retries:
        status["last_request_time"] = datetime.now()
        response = await app_status_getter(identifier)

        if response == Response.Success or response == Response.Failure:
            return ApplicationResponse(
                application_id=identifier,
                status=response,
                description=getter_description, # TODO get_application_status поменять
                last_request_time=status["last_request_time"],
                retriesCount=status["retries"] if status["retries"] != 0 else None
            )

        else:
            logger.debug(f'Received retry response: retrying...')
            status["retries"]+= 1

    logger.debug('Failed after maximum retries')
    # TODO проверить, что у нас ретраи вообще были
    return ApplicationResponse(
        application_id=identifier,
        status=ApplicationStatusResponse.Failure,
        description=getter_description, # TODO get_application_status поменять
        last_request_time=status["last_request_time"],
        retriesCount=status["retries"]
    )

async def perform_operation(identifier: str) -> ApplicationResponse:
    # TODO дополнить реализацию

    total_retries = TOTAL_RETRIES # TODO Общий счетчик?
    task1_status = {}
    task2_status = {}

    # TODO понимаю, что этот момент несколько кривоват, ибо логичнее было 
    # передавать не функции а url-ы, однако не могу понять
    # почему у нас именно такой интерфейс...
    # Это же зачем-то надо? Но я его не буду менять, раз в задании так
    task1 = retry_request(
        app_status_getter=get_application_status1,
        getter_description="Description for get_application_status1",
        identifier=identifier,
        total_retries=total_retries,
        status=task1_status
    )
    task2 = retry_request(
        app_status_getter=get_application_status2,
        getter_description="Description for get_application_status1",
        identifier=identifier,
        total_retries=total_retries,
        status=task2_status
    )
    
    try:
        done, pending = await asyncio.wait(
            [task1, task2],
            return_when=asyncio.FIRST_COMPLETED,
            timeout=TOTAL_TIMEOUT
        )

    except asyncio.TimeoutError:
        print(f'Timeout occurred after {TOTAL_TIMEOUT} seconds')
        # Завершаем pending tasks
        for task in pending:
            task.cancel()

    # Check if any task completed successfully
    for task in done:
        if task.exception() is None:
            response = task.result()
            print('Task has completed successfully')
            # TODO: а надо ли тут собирать стату общую?
            return response

    # Собираем стату
    last_request_time = task1_status.get("last_request_time")
    last_request_time_task2 = task2_status.get("last_request_time")
    if (
        last_request_time_task2 is not None and (
            last_request_time is None or
            last_request_time < last_request_time_task2
        )
    ):
        last_request_time = last_request_time_task2

    retries_count = task1_status.get("retries", 0) + task2_status.get("retries", 0)

    return ApplicationResponse(
        application_id=identifier,
        status=ApplicationStatusResponse.Failure,
        description="str", # ToDo get_application_status поменять
        last_request_time=last_request_time,
        retriesCount=retries_count
    )

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(perform_operation(2))
    loop.close()
