from passlib.context import CryptContext
from passlib.exc import UnknownHashError
from typing import Tuple
from core.config import settings

class PasswordHasher:
    def __init__(self, rounds: int = 12):
        self.pwd_context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto",
            bcrypt__rounds=rounds,
        )

    def hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify(self, password: str, hashed_password: str) -> bool:
        try:
            return self.pwd_context.verify(password, hashed_password)
        except UnknownHashError:
            return False

    def needs_refresh(self, hash_password: str) -> bool:
        return self.pwd_context.needs_update(hash_password)

    @classmethod
    def validate_strength(cls, password: str) -> Tuple[bool, str]:
        if len(password) < settings.PASSWORD_MIN_LENGTH:
            return False, f'Минимум {settings.PASSWORD_MIN_LENGTH} символов'

        checks = [
            (any(c.isupper() for c in password), "Заглавная буква"),
            (any(c.islower() for c in password), "Строчная буква"),
            (any(c.isdigit() for c in password), "Цифра"),
            (any(not c.isalnum() for c in password), "Специальный символ"),
        ]

        for passed, requirements in checks:
            if not passed:
                return False, f"Пароль должен содержать: {requirements}"

        return True, "Пароль надежный"

password_hasher = PasswordHasher()
