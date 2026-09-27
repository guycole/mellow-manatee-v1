#
# Title: postgres.py
# Description: postgresql support
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#
# import sqlalchemy
# from sqlalchemy import and_
# from sqlalchemy import select

import datetime

from typing import Any, List

import sqlalchemy
from sqlalchemy import and_
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy import desc

from .sql_table import (
    DailyScore,
    GeoLoc,
    LoadLog,
)

class PostGres:
    db_engine = None
    Session = None

    def __init__(self, session: sqlalchemy.orm.session.sessionmaker):
        self.Session = session

    def daily_score_insert_or_update(self, args: dict[str, Any]) -> DailyScore:
        candidate = DailyScore(args)

        try:
            with self.Session() as session:
                existing = session.scalars(
                    select(DailyScore).filter(
                        and_(
                            DailyScore.crate_name == candidate.crate_name,
                            DailyScore.host_name == candidate.host_name,
                            DailyScore.score_date == candidate.score_date,
                        )
                    )
                ).first()

                if existing is None:
                    session.add(candidate)
                else:
                    existing.file_quantity += candidate.file_quantity
                    existing.obs_quantity += candidate.obs_quantity

                session.commit()
        except Exception as error:
            print(error)

        return candidate

    def geo_loc_select_by_site(self, site_name: str) -> List[GeoLoc]:
        statement = (
            select(GeoLoc)
            .filter_by(site_name=site_name)
            .order_by(desc(GeoLoc.fix_time), desc(GeoLoc.id))
        )

        with self.Session() as session:
            return session.scalars(statement).all()

    @staticmethod
    def _normalize_load_log_args(args: dict[str, Any]) -> dict[str, Any]:
        key_map = {
            "crateName": "crate_name",
            "epochSeconds": "epoch_seconds",
            "fileName": "file_name",
            "geoLocId": "geo_loc_id",
            "hostName": "host_name",
            "loadTime": "load_time",
            "obsQuantity": "obs_quantity",
            "obsTime": "obs_time",
            "siteName": "site_name",
            "sourceFileName": "source_file_name",
            "taskName": "task",
        }

        normalized = {}
        for key, value in args.items():
            normalized[key_map.get(key, key)] = value

        return normalized

    def load_log_insert(self, args: dict[str, Any]) -> LoadLog:
        candidate = LoadLog(self._normalize_load_log_args(args))

        try:
            with self.Session() as session:
                session.add(candidate)
                session.commit()
        except Exception as error:
            print(error)

        return candidate

    def load_log_select_all(self) -> list[LoadLog]:
        with self.Session() as session:
            return session.scalars(
                select(LoadLog).order_by(desc(LoadLog.load_time), desc(LoadLog.id))
            ).all()

    def load_log_select_all_by_date(self, target: datetime.date) -> list[LoadLog]:
        with self.Session() as session:
            return session.scalars(
                select(LoadLog)
                .filter(func.date(LoadLog.load_time) == target)
                .order_by(desc(LoadLog.load_time), desc(LoadLog.id))
            ).all()

    def load_log_select_by_file_name(self, file_name: str) -> LoadLog:
        with self.Session() as session:
            return session.scalars(
                select(LoadLog).filter_by(file_name=file_name)
            ).first()

# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***
