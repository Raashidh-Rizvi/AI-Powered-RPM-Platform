import sys
import os

from sqlalchemy import create_engine
from shared.database import engine, Base
from shared import models

print("Dropping all tables...")
Base.metadata.drop_all(bind=engine)
print("Done.")
