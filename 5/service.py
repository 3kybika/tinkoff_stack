import argparse
from enum import Enum
from flask import Flask, request
import asyncio
import json

app = Flask(__name__)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

object_dict = {}

@app.before_first_request
async def load_dict_from_file():
    global object_dict
    with open(app.config.get('data_path'), 'r') as file:
        object_dict = json.load(file)


class Response(Enum):
    Success = 1
    RetryAfter = 2
    Failure = 3

async def check_object_in_dict(object_id):
    # TODO механизм Success, Failure
    await asyncio.sleep(1)  # Имитация длительного выполнения операции
    stat = object_dict.get(object_id)
    if stat:
        if stat["retries"] == 0:
            return (
                Response.Success.name 
                if stat["status"] == Response.Success.name
                else Response.Failure.name 
            )
        else:
            stat["retries"] -= 1
            object_dict[object_id] = stat
            return Response.RetryAfter.name
    else:
        return Response.RetryAfter.name

@app.route('/check_object', methods=['GET'])
def check_object():
    object_id = request.args.get('object_id')
    
    async def async_check():
        return await check_object_in_dict(object_id)

    fut = loop.create_task(async_check())

    try:
        result = loop.run_until_complete(fut)
        return result
    except asyncio.CancelledError:
        return Response.RetryAfter.name

# python3 service.py --file_path path_to_your_file.json --port=80
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Test service')
    parser.add_argument('--port', type=str, help='Server port', default='0.0.0.0')
    parser.add_argument('--host', type=str, help='Server host', default='5001')
    parser.add_argument('--file_path', type=str, help='Path to test data file')
    args = parser.parse_args()

    app.config['data_path'] = args.file_path

    app.run(host=args.host, port=args.port)

    app.run()