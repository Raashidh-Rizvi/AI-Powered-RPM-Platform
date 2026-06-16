import sys
import os

from sqlalchemy import create_engine
from database import engine, Base
import models

print("Dropping all tables...")
Base.metadata.drop_all(bind=engine)
print("Done.")
