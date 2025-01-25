import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from src.entities import Base

db_url = os.getenv('DB_URL')
engine = create_engine(db_url, echo=False)

Base.metadata.create_all(engine)

def example_query():
    with engine.connect() as conn:
        conn.execute(text("CREATE TABLE IF NOT EXISTS some_table (x int, y int)"))
        conn.execute(
            text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
            [{"x": 1, "y": 1}, {"x": 2, "y": 4}],
        )
        result = conn.execute(text("SELECT x, y FROM some_table"))
        for row in result:
            print(f"x: {row.x}  y: {row.y}")

def execute_raw_query(query):
    with Session(engine) as session:
        result = session.execute(text(query))
        session.commit()
        return result
    