#
# Title: sql_table.py
# Description: database table definitions
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#
from datetime import datetime
from typing import Any

from sqlalchemy import Column
from sqlalchemy import BigInteger, Date, DateTime, Float, ForeignKey, Integer, SmallInteger, String

from sqlalchemy.orm import registry
from sqlalchemy.orm import DeclarativeBase

mapper_registry = registry()

class Base(DeclarativeBase):
    pass


class DailyScore(Base):
    __tablename__ = "manatee_daily_score"

    id = Column(BigInteger, primary_key=True)
    crate_name = Column(String(32), nullable=False)
    file_quantity = Column(Integer, nullable=False)
    host_name = Column(String(16), nullable=False)
    obs_quantity = Column(Integer, nullable=False)
    score_date = Column(Date, nullable=False)

    def __init__(self, args: dict[str, Any]):
        self.crate_name = args["crate_name"]
        self.file_quantity = args["file_quantity"]
        self.host_name = args["host_name"]
        self.obs_quantity = args["obs_quantity"]
        self.score_date = args["score_date"]

    def __repr__(self):
        return f"daily_score({self.score_date} {self.host_name})"


class GeoLoc(Base):
    __tablename__ = "manatee_geo_loc"

    id = Column(BigInteger, primary_key=True)
    altitude = Column(Float, nullable=False)
    course = Column(Float, nullable=False)
    fix_time = Column(DateTime, nullable=False, default=datetime.now)
    host_name = Column(String(16), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    site_name = Column(String(48), nullable=False)
    speed = Column(Float, nullable=False)

    def __init__(self, args: dict[str, Any]):
        self.altitude = args["altitude"]
        self.course = args["course"]
        self.fix_time = args.get("fix_time", datetime.now())
        self.host_name = args["host_name"]
        self.latitude = args["latitude"]
        self.longitude = args["longitude"]
        self.site_name = args["site_name"]
        self.speed = args["speed"]

    def __repr__(self):
        return f"geo_loc({self.site_name} {self.host_name})"


class LoadLog(Base):
    __tablename__ = "manatee_load_log"

    id = Column(BigInteger, primary_key=True)
    crate_name = Column(String(32), nullable=False)
    epoch_seconds = Column(BigInteger, nullable=False)
    file_name = Column(String(48), unique=True, nullable=False)
    geo_loc_id = Column(BigInteger, ForeignKey("manatee_geo_loc.id"), nullable=False)
    host_name = Column(String(32), nullable=False)
    load_time = Column(DateTime, nullable=False, default=datetime.now)
    obs_quantity = Column(SmallInteger, nullable=False)
    obs_time = Column(DateTime, nullable=False)
    site_name = Column(String(32), nullable=False)
    source_file_name = Column(String(48), unique=True, nullable=False)
    task = Column(String(32), nullable=False)

    def __init__(self, args: dict[str, Any]):
        self.crate_name = args["crate_name"]
        self.epoch_seconds = args["epoch_seconds"]
        self.file_name = args["file_name"]
        self.geo_loc_id = args["geo_loc_id"]
        self.host_name = args["host_name"]
        self.load_time = args.get("load_time", datetime.now())
        self.obs_quantity = args["obs_quantity"]
        self.obs_time = args["obs_time"]
        self.site_name = args["site_name"]
        self.source_file_name = args["source_file_name"]
        self.task = args["task"]

    def __repr__(self):
        return f"load_log({self.file_name} {self.obs_time} {self.task} {self.host_name})"

# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***
