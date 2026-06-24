import datetime
from typing import List, TYPE_CHECKING

from sqlalchemy import String, Integer, ForeignKey, DateTime, Boolean, event

from core.config import settings
from models.base import AbstractImageModel, Base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from utils.password import password_hasher

if TYPE_CHECKING:
    from models.post import PostModel
    from models.comment import CommentModel


class User(Base):
    __tablename__ = 'user'
    __abstract__ = False

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    password: Mapped[str] = mapped_column(
        String,
        nullable=False
    )
    last_login: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.datetime.now(datetime.timezone.utc),
        onupdate=datetime.datetime.now(datetime.timezone.utc),
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    username: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
    )
    last_name: Mapped[str] = mapped_column(
        String,
        nullable=True,
    )
    email: Mapped[str] = mapped_column(
        String,
        nullable=False,
        unique=True,
        index=True,
    )
    is_staff: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )
    date_joined: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.datetime.now(datetime.timezone.utc)
    )
    first_name: Mapped[str] = mapped_column(
        String,
        nullable=True,
    )
    profile: Mapped["Profile"] = relationship(
        "Profile",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    posts: Mapped[List["PostModel"]] = relationship(
        back_populates="user",
    )
    comments: Mapped[List["CommentModel"]] = relationship(
        back_populates="user",
    )

    def set_password(self, password: str) -> None:
        self.password = password_hasher.hash(password)

    def verify_password(self, password: str) -> bool:
        return password_hasher.verify(password, self.password)

    def check_password_needs_rehash(self, password: str) -> bool:
        return password_hasher.needs_refresh(self.password)

    @property
    def is_authenticated(self) -> bool:
        return self.is_active

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip() or self.username

    def __repr__(self):
        return f"User(id={self.id}, email={self.email})"


class Profile(AbstractImageModel):
    __tablename__ = 'profile'
    __abstract__ = False

    IMAGE_SUBFOLDER = 'users'
    THUMBNAIL_SIZE = settings.THUMBNAIL_SIZES["small"]

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    birthday: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    attempts_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    block_date: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            'user.id',
            ondelete='CASCADE',
            onupdate='CASCADE',
        ),
        nullable=False,
        index=True,
    )
    user: Mapped["User"] = relationship(
        "User",
        back_populates="profile",
    )

    def increase_attempts_count(self):
        self.attempts_count += 1
        if self.attempts_count >= settings.MAX_ATTEMPTS:
            self.block_date = datetime.datetime.now(datetime.timezone.utc)

    @property
    def is_blocked(self) -> bool:
        if self.block_date is None:
            return False
        return datetime.datetime.now(datetime.timezone.utc) < self.block_date + datetime.timedelta(days=1)

    def reset_attempts_count(self) -> None:
        self.attempts_count = 0
        self.block_date = None


@event.listens_for(User, 'before_insert')
def hash_password_before_insert(mapper, connection, target):
    if target.password and not target.password.startswith('$2b$'):
        target.set_password(target.password)


@event.listens_for(User, 'before_update')
def hash_password_before_update(mapper, connection, target):
    if target.password and not target.password.startswith('$2b$'):
        target.set_password(target.password)
