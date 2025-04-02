from .base import UserRepositoryBase
from .postgres import UserRepositoryPostgres


__all__ = [
    "UserRepositoryBase",
    "UserRepositoryPostgres",
]
