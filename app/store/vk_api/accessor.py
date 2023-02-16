import typing
import random
from typing import Optional

from aiohttp.client import ClientSession

from app.base.base_accessor import BaseAccessor
from app.store.vk_api.dataclasses import Message, Update, UpdateObject, UpdateMessage
from app.store.vk_api.poller import Poller

if typing.TYPE_CHECKING:
    from app.web.app import Application


class VkApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.session: Optional[ClientSession] = None
        self.key: Optional[str] = None
        self.server: Optional[str] = None
        self.poller: Optional[Poller] = None
        self.ts: Optional[int] = None
        self.group_id: Optional[int] = None
        self.access_token: Optional[str] = None

    async def connect(self, app: "Application"):
        # TODO: добавить создание aiohttp ClientSession,
        #  получить данные о long poll сервере с помощью метода groups.getLongPollServer
        #  вызвать метод start у Poller
        self.access_token = app.config.bot.token
        self.group_id = app.config.bot.group_id
        params = {"group_id": self.group_id,
                  "access_token": self.access_token}
        url = self._build_query("https://api.vk.com/", "method/groups.getLongPollServer", params)
        client_session = ClientSession()
        response = await client_session.get(url)
        if response.ok:
            data = await response.json()
            data_response = data.get("response")
            self.session = client_session
            self.key = data_response.get("key")
            self.server = data_response.get("server")
            self.ts = data_response.get("ts")
            self.poller = Poller(app.store)
            await self.poller.start()

    async def disconnect(self, app: "Application"):
        # TODO: закрыть сессию и завершить поллер
        if not self.session.closed:
            await self.session.close()
        await self.poller.stop()

    @staticmethod
    def _build_query(host: str, method: str, params: dict) -> str:
        url = host + method + "?"
        if "v" not in params:
            params["v"] = "5.131"
        url += "&".join([f"{k}={v}" for k, v in params.items()])
        return url

    async def _get_long_poll_service(self):
        raise NotImplementedError

    async def poll(self):
        if not self.session.closed:
            params = {"act": "a_check",
                      "key": self.key,
                      "ts": self.ts,
                      "wait": 1}
            url = self._build_query(self.server, "", params)
            response = await self.session.get(url)
            if response.ok:
                data = await response.json()
                self.ts = data.get("ts")
                updates = []
                updates_data = data.get("updates")
                for update_data in updates_data:
                    message_data = update_data["object"]["message"]
                    update_type = update_data["type"]
                    id_ = message_data["id"]
                    from_id = message_data["from_id"]
                    text = message_data["text"]
                    message = UpdateMessage(from_id, text, id_)
                    update_object = UpdateObject(message)
                    update = Update(update_type, update_object)
                    updates.append(update)
                await self.app.store.bots_manager.handle_updates(updates)

    async def send_message(self, message: Message) -> None:
        params = {
            "access_token": self.access_token,
            "random_id": random.randint(1, 1000000),
            "message": message.text,
            "chat_id": 3,
        }
        url = self._build_query("https://api.vk.com/", "method/messages.send", params)
        await self.session.get(url)
