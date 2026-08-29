#
# Title: validator.py
# Description: ensure valid manatee files
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#
import logging
import datetime
import json
import os

from helper.json_helper import JsonHelper, schema

from helper.postgres import PostGres

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("manatee")

class Validator:

    def __init__(self, postgres: PostGres):
        self.postgres = postgres

        self.failure_dir = os.environ.get("FAILURE_DIR", "/var/wombat/failure")
        self.fresh_dir = os.environ.get("FRESH_DIR", "/var/wombat/fresh/manatee")
        self.success_dir = os.environ.get("SUCCESS_DIR", "/var/wombat/manatee/success")
      
        self.failure = 0
        self.success = 0

        self.jh = JsonHelper()

    def file_failure(self, file_name: str):
        logger.info(f"file failure:{file_name}")

        self.failure += 1
#        os.rename(file_name, self.failure_dir + file_name)

    def file_success(self, file_name: str):
        #logger.info(f"file success:{file_name}")

        self.success += 1
#        os.rename(file_name, self.success_dir + "/" + file_name)

    def file_reader(self, file_name: str) -> bool:
        try:
            with open(file_name, "r", encoding="utf-8") as in_file:
                self.raw_buffer = json.load(in_file)
        except Exception as error:
            logger.error(f"file read failed for {file_name}: {error}")
            return False

        return True

    def load_log_test(self, test_file_name: str) -> bool:

        logger.info(f"load_log_test for file: {test_file_name}")

        try:
            candidate = self.postgres.load_log_select_by_file_name(test_file_name)
            if candidate is None:
                logger.info(f"processing new file:{test_file_name}")

                geo_loc = self.postgres.geo_loc_select_by_site(self.jh.raw_json["geoLoc"]["siteName"])
                if len(geo_loc) == 0:
                    print("must insert geo_loc for site:", self.jh.raw_json["geoLoc"]["siteName"])
                    return False

                load_log = {
                    "crate_name": self.jh.raw_json["crateName"],
                    "epoch_seconds": self.jh.raw_json["timeStamp"]["epochSeconds"],
                    "file_name": test_file_name,
                    "geo_loc_id": geo_loc[0].id,
                    "host_name": self.jh.raw_json["equipment"]["hostName"],
                    "load_time": datetime.datetime.now(),
                    "mode": self.jh.raw_json["job"]["mode"],
                    "obs_time": self.jh.raw_json["timeStamp"]["iso8601"],
                    "peaker_quantity": len(self.jh.raw_json["peakers"]),
                    "site_name": self.jh.raw_json["geoLoc"]["siteName"],
                    "task": self.jh.raw_json["job"]["task"],
                }
                
                self.postgres.load_log_insert(load_log)

                return True
            else:
                logger.info(f"skippping already processed:{test_file_name}")
                return False               
        except Exception as error:
            logger.error(f"postgres insert failed for {test_file_name}: {error}")        

        return False

    def file_processor(self, file_name1: str, file_name2: str) -> None:
        logger.info(f"processing files: {file_name1} {file_name2}")

        if os.path.isfile(file_name1) is False:
            logger.warning(f"skipping non-file:{file_name1}")
            self.file_failure2(file_name1, file_name2)
            return

        if os.path.isfile(file_name2) is False:
            logger.warning(f"skipping non-file:{file_name2}")
            self.file_failure2(file_name1, file_name2)
            return

        if os.path.getsize(file_name1) < 1 or os.path.getsize(file_name2) < 1:
            logger.warning(f"skipping empty file(s):{file_name1} {file_name2}")
            self.file_failure2(file_name1, file_name2)
            return

        test_file_name = file_name1 if file_name1.endswith(".json") else file_name2
        if not self.jh.json_file_reader(test_file_name, True):
            logger.warning(f"file read failed for {test_file_name}")
            self.file_failure2(file_name1, file_name2)
            return

        if self.jh.raw_json["fileName"] != test_file_name:
            logger.warning(f"mismatched file name: {self.jh.raw_json['fileName']} vs {test_file_name}")
            self.file_failure2(file_name1, file_name2)
            return

        if self.jh.raw_json["version"] == 1 and self.jh.raw_json["job"]["project"].startswith("manatee-v1"):
            pass
        else:
            logger.warning(f"invalid version or project for {test_file_name} {self.jh.raw_json['job']['project']}")
            self.file_failure2(file_name1, file_name2)
            return

        if self.load_log_test(test_file_name):
            self.file_success2(file_name1, file_name2)
        else:
            self.file_failure2(file_name1, file_name2)

    def execute(self) -> None:
        logger.info(f"validator fresh dir:{self.fresh_dir}")

        os.chdir(self.fresh_dir)
        targets = sorted(os.listdir("."))
        logger.info(f"{len(targets)} files noted")

        ndx1 = 0
        while ndx1 < len(targets)-1:
            # valid files will arrive in pairs
            target1 = targets[ndx1]
            target2 = targets[ndx1+1]

            temp = target1.split(".")
            if target2.startswith(temp[0]):
                self.file_processor(target1, target2)
                ndx1 += 1
            else:
                logger.info(f"skipping fail name match {target1} {target2}")

            ndx1 += 1

# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***
