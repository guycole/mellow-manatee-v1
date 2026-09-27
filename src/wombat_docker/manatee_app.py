#
# Title: manatee_app.py
# Description: driver for manatee application
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#
import logging
import os
import sys
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from validator import ManateeValidator
from helper.postgres import PostGres

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("manatee")


class ManateeApp:
    def __init__(self, stunt_box: str):
        self.stunt_box = stunt_box

        self.db_conn = os.environ.get(
            "DB_CONN",
            "postgresql+psycopg2://manatee_client:batabat@localhost:5432/manatee",
        )

        connect_timeout = int(os.environ.get("PG_CONNECT_TIMEOUT", "5"))
        statement_timeout_ms = int(os.environ.get("PG_STATEMENT_TIMEOUT_MS", "5000"))

        db_engine = create_engine(
            self.db_conn,
            echo=False,
            pool_pre_ping=True,
            connect_args={
                "connect_timeout": connect_timeout,
                "options": f"-c statement_timeout={statement_timeout_ms}",
            },
        )
        self.postgres = PostGres(sessionmaker(bind=db_engine, expire_on_commit=False))

    def execute(self) -> int:
        logger.info("manatee execute: %s", self.stunt_box)

        if self.stunt_box == "validator":
            validator = ManateeValidator(logger, self.postgres)
            return validator.execute()

        logger.error("invalid stunt_box option: %s", self.stunt_box)
        return 1


if __name__ == "__main__":
    stunt_box = os.environ.get("stuntbox", "validator")

    app = ManateeApp(stunt_box)
    exit(app.execute())

# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***
