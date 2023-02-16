import typing
from hashlib import sha256
from typing import Optional

from app.base.base_accessor import BaseAccessor
from app.admin.models import Admin

if typing.TYPE_CHECKING:
    from app.web.app import Application


class AdminAccessor(BaseAccessor):
    @staticmethod
    async def get_password_hash(password: str) -> str:
        password_hash = sha256()
        password_hash.update(password.encode())
        return password_hash.hexdigest()

    async def connect(self, app: "Application"):
        # TODO: создать админа по данным в config.yml здесь
        email = self.app.config.admin.email
        password = await self.get_password_hash(self.app.config.admin.password)
        await self.create_admin(email=email, password=password)

    async def get_by_email(self, email: str) -> Optional[Admin]:
        admin = None
        for item in self.app.database.admins:
            if item.email == email:
                admin = item
                break
        return admin

    async def create_admin(self, email: str, password: str) -> Admin:
        admin = await self.get_by_email(email)
        if not admin:
            id_ = len(self.app.database.admins) + 1
            admin = Admin(
                id=id_,
                email=email,
                password=password,
            )
            self.app.database.admins.append(admin)
        return admin

    async def login(self, email: str, password: str) -> Optional[Admin]:
        is_auth = await self.authenticate(email, password)
        if is_auth:
            return await self.get_by_email(email)
        return None

    async def authenticate(self, email: str, password: str) -> bool:
        admin = await self.get_by_email(email)
        if not admin:
            return False
        password_hash = await self.get_password_hash(password)
        if password_hash == admin.password:
            return True
        return False
