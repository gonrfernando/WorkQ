# init_test_db.py
from sqlalchemy import create_engine
from worq.models.models import Base

engine = create_engine("postgresql://test_user:test_Workq_360@localhost/test_db_worq")
Base.metadata.create_all(bind=engine)
print("Base de datos inicializada correctamente.")
