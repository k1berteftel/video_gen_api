import asyncio


class TaskWorker():
    def __init__(self):
        self._task_storage: dict[str, asyncio.Task] = {}
        self._task_storage.clear()

    async def add_task(self, task_id: str, func, args: list):
        task = asyncio.create_task(
            func(*args)
        )
        task.set_name(task_id)
        self._task_storage[task_id] = task

    async def get_task(self, task_id: str) -> dict:
        task = self._task_storage.get(task_id)
        if not task:
            raise KeyError('Такой задачи не существует')
        if task.done():
            exception = task.exception()
            if exception:
                result = {
                    'status': 'failed',
                    'message': str(exception)
                }
            else:
                result = {
                    'status': 'completed',
                    'result': task.result()
                }
                task.cancel()
                del self._task_storage[task_id]
        else:
            result = {
                'status': 'processing',
                'message': ''
            }
        return result
