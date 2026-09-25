#
# Title: validator.py
# Description: ensure valid manatee files
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#
import datetime
import logging
import os
import sys
from pathlib import Path

from abc import ABC, abstractmethod

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from helper.postgres import PostGres
from helper.json_helper import JsonHelper


class Validator(ABC):
    @abstractmethod
    def file_processor(self, file_name: str) -> bool:
        pass

    @abstractmethod
    def execute(self) -> int:
        pass

    @abstractmethod
    def file_failure(self, file_name: str) -> None:
        pass

    @abstractmethod
    def file_success(self, file_name: str) -> None:
        pass

    @abstractmethod
    def load_log_test(self, test_file_name: str) -> bool:
        pass


class ManateeValidator(Validator):
    def __init__(self, logger: logging.Logger, postgres: PostGres):
        self.logger = logger
        self.postgres = postgres
        self.json_helper = JsonHelper()

        self.failure_dir = os.environ.get("FAILURE_DIR", "/var/wombat/failure")
        self.fresh_dir = os.environ.get("FRESH_DIR", "/var/wombat/fresh/manatee")
        self.success_dir = os.environ.get("SUCCESS_DIR", "/var/wombat/manatee/success")

        self.failure: int = 0
        self.success: int = 0

    def file_failure(self, file_name: str) -> None:
        self.logger.info("file failure: %s", file_name)

        self.failure += 1

        failure_target = os.path.join(self.failure_dir, file_name)
        try:
            os.rename(file_name, failure_target)
        except Exception as error:
            self.logger.error(
                "file move failure for %s -> %s: %s",
                file_name,
                failure_target,
                error,
            )

    def file_success(self, file_name: str) -> None:
        self.logger.info("file success: %s", file_name)

        self.success += 1
        success_target = os.path.join(self.success_dir, file_name)

        try:
            os.rename(file_name, success_target)
        except Exception as error:
            self.logger.error(
                "file move failure for %s -> %s: %s",
                file_name,
                success_target,
                error,
            )

    def load_log_test(self, test_file_name: str) -> bool:
        self.logger.info("checking load log: %s", test_file_name)

        try:
            raw_buffer = self.json_helper.raw_json

            candidate = self.postgres.load_log_select_by_file_name(test_file_name)
            if candidate is not None:
                self.logger.info("skipping already processed: %s", test_file_name)
                return False

            site_name = raw_buffer["geoLoc"]["siteName"]
            geo_locs = self.postgres.geo_loc_select_by_site(site_name)
            if len(geo_locs) == 0:
                self.logger.error("missing geo_loc for site: %s", site_name)
                return False

            load_log = {
                "crate_name": raw_buffer["crate"],
                "epoch_seconds": raw_buffer["timeStamp"]["epochSeconds"],
                "file_name": test_file_name,
                "geo_loc_id": geo_locs[0].id,
                "host_name": raw_buffer["equipment"]["hostName"],
                "load_time": datetime.datetime.now(),
                "mode": raw_buffer["job"]["mode"],
                "obs_time": raw_buffer["timeStamp"]["iso8601"],
                "peaker_quantity": len(raw_buffer["observations"]),
                "site_name": site_name,
                "task": raw_buffer["job"]["task"],
            }

            self.postgres.load_log_insert(load_log)
            self.logger.info("load log insert complete: %s", test_file_name)

            return True
        except Exception as error:
            self.logger.error(
                "postgres insert failed for %s: %s", test_file_name, error
            )

        return False

    def file_processor(self, file_name: str) -> bool:
        self.logger.info("processing file: %s", file_name)

        if not os.path.isfile(file_name):
            self.logger.warning("skipping non-file: %s", file_name)
            self.file_failure(file_name)
            return False

        if os.path.getsize(file_name) < 1:
            self.logger.warning("skipping empty file: %s", file_name)
            self.file_failure(file_name)
            return False

        if not self.json_helper.json_file_reader(file_name, True):
            self.logger.warning("file read failed for %s", file_name)
            self.file_failure(file_name)
            return False

        model_file_name = self.json_helper.raw_json["fileName"]
        if model_file_name != file_name:
            self.logger.warning(
                "mismatched file name: %s vs %s",
                model_file_name,
                file_name,
            )
            self.file_failure(file_name)
            return False

        if (
            self.json_helper.raw_json["version"] != 1
            or self.json_helper.raw_json["job"]["project"] != "manatee-v1"
        ):
            self.logger.warning("invalid version or project for %s", file_name)
            self.file_failure(file_name)
            return False

        if self.load_log_test(file_name):
            self.file_success(file_name)
            return True

        self.file_failure(file_name)
        return False

    def execute(self) -> int:
        self.logger.info("validator fresh dir: %s", self.fresh_dir)

        os.chdir(self.fresh_dir)
        targets = sorted(os.listdir("."))
        self.logger.info("%d files noted", len(targets))

        for target in targets:
            if target.endswith(".raw"):
                self.logger.info("skipping raw: %s", target)
                self.file_success(target)
                continue

            self.file_processor(target)

        self.logger.info(
            "validator success: %d failure: %d", self.success, self.failure
        )

        return 0


# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***
