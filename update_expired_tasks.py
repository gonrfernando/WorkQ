from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from worq.models.models import Tasks  # Asegúrate de que el path sea correcto
import os

DATABASE_URL = os.getenv("DATABASE_URL")

# Configurar sesión
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

def update_expired():
    today = date.today()
    expired_tasks = session.query(Tasks).filter(
        Tasks.finished_date < today,
        Tasks.priority_id != 4,
        Tasks.status_id != 5
    ).all()

    for task in expired_tasks:
        print(f"Task ID {task.id} has expired!. Changing his status to Expired.")
        task.priority_id = 4
        task.status_id = 5

    session.commit()
    print(f"{len(expired_tasks)} Tasks updated.")

if __name__ == "__main__":
    update_expired()
