"""
analytics-worker: A worker service for handling analytics tasks.

This service is designed to be run as a separate process, handling analytics tasks
in the background to improve the responsiveness of the main application.

Requirements
------------

* Python 3.8+
* `aiohttp` for asynchronous HTTP requests
* `aioredis` for Redis interactions

Usage
-----

To run the worker, use the following command:
```bash
python -m analytics_worker
```
This will start the worker in the foreground. To run the worker in the background,
use the following command:
```bash
nohup python -m analytics_worker &
```
Configuration
-------------

The worker can be configured using environment variables. The following variables
are supported:

* `REDIS_URL`: The URL of the Redis instance to use. Defaults to `redis://localhost:6379/0`.
* `ANALYTICS_API_URL`: The URL of the analytics API to use. Defaults to `http://localhost:8000`.

"""

import asyncio
import logging
import os

from aiohttp import web
from aioredis import Redis

# Set up logging
logging.basicConfig(level=logging.INFO)

# Set up Redis client
redis = Redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379/0'))

# Set up analytics API URL
analytics_api_url = os.environ.get('ANALYTICS_API_URL', 'http://localhost:8000')

# Create the web application
app = web.Application()

# Define the route for handling analytics tasks
@app.route('/analytics', method=['POST'])
async def handle_analytics_task(request):
    # Get the task data from the request body
    task_data = await request.json()

    # Process the task data
    await process_task_data(task_data)

    # Return a success response
    return web.Response(text='Task processed successfully')

# Define the function to process task data
async def process_task_data(task_data):
    # Use the Redis client to store the task data
    await redis.set('task_data', task_data)

    # Use the analytics API to process the task data
    async with aiohttp.ClientSession() as session:
        async with session.post(analytics_api_url, json=task_data) as response:
            await response.json()

# Run the application
if __name__ == '__main__':
    web.run_app(app)