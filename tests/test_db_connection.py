from sqlalchemy import text


def test_database_connection(db_engine):
    """Verify that we can connect and ping MySQL."""
    with db_engine.connect() as conn:
        result = conn.execute(text("SELECT 1;")).scalar()
        assert result == 1
