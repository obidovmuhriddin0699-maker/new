"""Transaction boundary helper.

Service methods wrap their work in ``atomic(session)``. The outermost block
commits on success and rolls back on any exception; nested blocks join the
outer transaction, so a service calling another service stays atomic.
"""

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy.orm import Session

_DEPTH_KEY = "atomic_depth"


@contextmanager
def atomic(session: Session) -> Iterator[Session]:
    depth = session.info.get(_DEPTH_KEY, 0)
    session.info[_DEPTH_KEY] = depth + 1
    try:
        yield session
        if depth == 0:
            session.commit()
    except BaseException:
        if depth == 0:
            session.rollback()
        raise
    finally:
        session.info[_DEPTH_KEY] = depth
