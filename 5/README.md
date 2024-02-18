# All to Scala, проверка стека
# 5 задание
Python

# Решение и описание лежит в result.ipynb

Цель задачи

Реализовать асинхронные методы для получения статуса заявок от двух сервисов. Операция `perform_operation` должна асинхронно выполнять параллельные запросы к сервисам `get_application_status1` и `get_application_status2`, а также обрабатывать их ответы в соответствии с предоставленными правилами.



Используемые технологии

1. Язык программирования: Python 3.7 или более поздняя версия.

2. Библиотеки: asyncio для асинхронного выполнения задач, ThreadPoolExecutor для запуска блокирующих функций в отдельных потоках.

3. Стандартные библиотеки: enum для определения перечислений, dataclasses для создания данных,   datetime для работы с временем.



Описание методов

1. `get_application_status1(identifier: str) -> Response`

  1. Описание: Асинхронный метод для получения статуса заявки от сервиса 1.

   * Входные параметры:

     1. `identifier (строка)`: Идентификатор заявки.

   * Возвращаемое значение:

     1. `Response`: Одно из значений перечисления `Response (Success, RetryAfter, Failure)`.

2. `get_application_status2(identifier: str) -> Response`

  1. Описание: Асинхронный метод для получения статуса заявки от сервиса 2.

    * Входные параметры:

     1. `identifier (строка)`: Идентификатор заявки.

    * Возвращаемое значение:

     1. `Response`: Одно из значений перечисления `Response (Success, RetryAfter, Failure)`.

3. `perform_operation() -> ApplicationResponse`

  1. Описание: Асинхронный метод, выполняющий параллельные запросы к сервисам `get_application_status1` и `get_application_status2`, и обрабатывающий их ответы.

    * Возвращаемое значение:

     1. ApplicationResponse: Объект, содержащий информацию о результате операции.

  2. Поля объекта:

    * `application_id (строка)`: Идентификатор заявки.

    * `status (ApplicationStatusResponse)`: Одно из значений перечисления `ApplicationStatusResponse (Success, Failure)`.

    * `description (строка)`: Описание статуса заявки.

    * `last_request_time (datetime)`: Время последнего запроса (в случае успеха или неудачи).

    * `retriesCount (int или None)`: Количество повторных запросов (в случае неудачи).



Технические особенности

1. Асинхронное выполнение: Использование `asyncio` для асинхронного выполнения запросов и обработки ответов.

2. Параллельные запросы: Использование `ThreadPoolExecutor` для параллельного выполнения блокирующих функций.

3. Обработка таймаута: Проверка времени выполнения операции и возврат `ApplicationResponse.Failure` при достижении таймаута.

4. Ожидание перед повторной попыткой: Использование `asyncio.sleep` для ожидания перед повторной попыткой в случае `Response.RetryAfter`.



Пример использования

```python
import asyncio

# Инициализация asyncio loop
loop = asyncio.get_event_loop()

# Запуск асинхронной операции
result = loop.run_until_complete(perform_operation())
print(result)

```


Замечания

1. Можно дополнительно использовать библиотеки для выполнения HTTP-запросов (например, aiohttp), если это требуется для ваших сервисов.

2. Рекомендуется обеспечить обработку ошибок и исключений при выполнении запросов.



```python
from enum import Enum
from typing import Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

timeout_seconds = timedelta(seconds=15).total_seconds()

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

async def get_application_status1(identifier: str) -> Response:
  # Метод, возвращающий статус заявки
  pass

async def get_application_status2(identifier: str) -> Response:
  # Метод, возвращающий статус заявки
  pass

async def perform_operation(identifier: str) -> ApplicationResponse:
  # TODO дополнить реализацию
  pass


```