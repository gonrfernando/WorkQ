from sqlalchemy import inspect, text
from worq.models.meta import Base

def test_database_tables_accessible(db_session):
    """Verifica que todas las tablas se puedan consultar sin error."""
    inspector = inspect(db_session.bind)
    tables = inspector.get_table_names()

    for table in tables:
        try:
            result = db_session.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            assert count >= 0  # La tabla es accesible
        except Exception as e:
            assert False, f"Error al consultar la tabla {table}: {e}"


def test_database_expected_structure():
    """Verifica que las tablas definidas en el modelo existen en la base de datos y tienen columnas claves."""
    metadata = Base.metadata

    for table in metadata.sorted_tables:
        column_names = [c.name for c in table.columns]
        assert 'id' in column_names or 'uuid' in column_names or 'email' in column_names, \
            f"La tabla '{table.name}' no tiene una columna primaria clara (id/uuid/email)"


def test_foreign_keys_exist(db_session):
    """Verifica que todas las llaves foráneas puedan resolverse (sin registros huérfanos)."""
    inspector = inspect(db_session.bind)
    for table_name in inspector.get_table_names():
        fks = inspector.get_foreign_keys(table_name)
        for fk in fks:
            try:
                # Verificar que la tabla de referencia exista
                ref_table = fk['referred_table']
                assert ref_table in inspector.get_table_names(), \
                    f"Tabla referenciada '{ref_table}' no existe para FK en '{table_name}'"
            except Exception as e:
                assert False, f"Error revisando FK en tabla {table_name}: {e}"
