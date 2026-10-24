"""数据库连接与初始化。"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import settings

# SQLite 单文件数据库，check_same_thread=False 以支持多线程并发访问
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


def init_db() -> None:
    """建表并写入默认管理员账号（幂等，可重复执行）。"""
    from . import models  # noqa: F401 确保模型被注册
    from .security import hash_password

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        admin = (
            db.query(models.User)
            .filter(models.User.username == settings.admin_username)
            .first()
        )
        if admin is None:
            db.add(
                models.User(
                    username=settings.admin_username,
                    password_hash=hash_password(settings.admin_password),
                    role="admin",
                )
            )
            db.commit()
    finally:
        db.close()
