import argparse
import asyncio
import concurrent.futures
import json
import logging
import time

from aiohttp import web


logger = logging.getLogger(__name__)


class App:
    def __init__(self, task):
        self.app = web.Application()
        self.app.add_routes([web.get('/health', self.health)])
        self.app.add_routes([web.get('/admin', self.admin)])
        self.status = {
            'status': 'up'
        }
        self.app.on_startup.append(self.run_task)
        self.app.on_shutdown.append(self.cleanup)
        self.task = task
        self.task_interval = 30 # seconds
        self.last_start = None
        self.last_end = None
        self.max_expected_task_duration = 5 # seconds
        self.errors = 0

    async def health(self, request):
        """Health check handler

        Works in tandem with the healthcheck.py script.
        """
        def send(status):
            return web.Response(json.dumps({
                'status': status
            }))
        
        if self.last_start is None:
            return send('down')
        
        if self.last_end is None:
            return send('down')
        
        if self.errors:
            return send('down')
        
        now = time.time()
        if (self.last_end < self.last_start and
                self.max_expected_task_duration < now - self.last_start):
            return send('down')
        return send('up')

    async def admin(self, request):
        """Admin request handler

        Useful to help determine how long tasks take to execute.
        """
        return web.Response(json.dumps({
            'last_start': self.last_start,
            'last_end': self.last_end,
            'errors': self.errors
        }))

    async def run_task(self, app):
        self.running = True
        executor = concurrent.futures.ProcessPoolExecutor(max_workers=1)
        while self.running:
            self.last_start = time.time()
            try:
                await app.loop.run_in_executor(executor, self.task)
                self.errors = 0
            except RuntimeError as e:
                logger.error(f'Task failed: {e}')
                self.errors += 1
                # we may also take some action here based on number of errors,
                # send an email/SMS
            self.last_end = time.time()
            if self.running:
                await asyncio.sleep(self.task_interval)

    async def cleanup(self, app):
        self.running = False

    def run(self):
        web.run_app(self.app)


def task():
    '''
    Our actual script, whatever we're trying to run periodically.

    Raising an exception will propagate to the caller.

    Logging will go to stderr. It is unlikely to be interleaved since we
    only run 1 process and don't log from main. Otherwise see solutions
    here: https://stackoverflow.com/q/641420/1698058

    If the operation takes too long Docker will kill the
    app since we report it as unhealthy. For longer-running tasks
    we may provide a callback parameter that allows updating the
    status, but that is more intrusive for simple cases.
    '''
    logger.info('task()')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Task runner')
    parser.add_argument(
        '--debug', action='store_true',
        help='whether to enable debug logging')
    args = parser.parse_args()

    if args.debug:
        level = logging.DEBUG
    else:
        level = logging.INFO
    format = '''#### %(asctime)s %(levelname)s %(filename)s:%(lineno)d
    %(message)s'''
    logging.basicConfig(level=level, format=format)

    App(task).run()