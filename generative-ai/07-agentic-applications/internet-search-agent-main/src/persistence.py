from contextlib import AbstractAsyncContextManager

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from src import config


def get_sqlite_saver() -> AbstractAsyncContextManager[AsyncSqliteSaver]:
    """Initialize and return a SQLite saver instance."""
    return AsyncSqliteSaver.from_conn_string(config.SQLITE_DB_LOCAL_PATH)


def get_checkpointer():
    if config._USE_POSTGRES_CHECKPOINTER:  # production / Homebrew-Postgres
        # TODO: implement Postgres checkpointer
        raise NotImplementedError("Postgres checkpointer is not implemented yet.")
    if config._USE_SQLITE_CHECKPOINTER:  # local dev / SQLite
        return get_sqlite_saver()
    # for the case of using langgraph studio
    return None
