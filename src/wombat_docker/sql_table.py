#
# Title: sql_table.py
# Description: database table definitions
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#
from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import BigInteger, Boolean, Date, DateTime, Float, Integer, String

from sqlalchemy.orm import registry
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.declarative import declared_attr

mapper_registry = registry()


class Base(DeclarativeBase):
    pass

class LoadLog(Base):
    """load_log table definition"""

    __tablename__ = "manatee_load_log"

    id = Column(Integer, primary_key=True)
    epoch_seconds = Column(BigInteger)
    file_name = Column(String)
    file_time = Column(DateTime)
    file_type = Column(String)
    host_name = Column(String)
    load_time = Column(DateTime)
    obs_quantity = Column(Integer)
   

    def __init__(self, args: dict[str, any]):
        self.epoch_seconds = args["epoch_seconds"]
        self.file_name = args["file_name"]
        self.file_time = args["file_time"]
        self.file_type = args["file_type"]
        self.host_name = args["host_name"]
        self.load_time = args.get("load_time", datetime.now())
        self.obs_quantity = args["obs_quantity"]
       

    def __repr__(self):
        return f"load_log({self.file_name} {self.file_time} {self.file_type} {self.host_name})"

# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***
