import uvicorn
from threading import Thread


class UvicornServer:
    def __init__(self, app, host="127.0.0.1", port=8000):
        self.server_config = uvicorn.Config(app, host=host, port=port, lifespan="on")
        self.server = uvicorn.Server(self.server_config)
        self.thread = None

    def start(self):
        """Запуск сервера в отдельном потоке"""
        print("🚀 Сервер запущен")
        self.server.run()

    async def stop(self):
        """Остановка сервера"""
        print("🛑 Останавливаю сервер...")
        self.server.should_exit = True
        await self.server.shutdown()
        print("👋 Сервер остановлен")