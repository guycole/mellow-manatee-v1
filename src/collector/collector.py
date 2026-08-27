#
# Title: collector.py
# Description: discover completed observation files and write collection report
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#

import datetime
import json
import logging
import os
import sys
import time
import uuid
import zoneinfo

from helper.json_helper import JsonHelper

import yaml
from yaml.loader import SafeLoader

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("collector")

class Collector:

    def __init__(self, args: dict[str, any]):
        self.dump_dir = args["dumpDir"]
        self.crate_name = args["crateName"]
        self.fresh_dir = args["freshDir"]

        self.host_name = args["equipment"]["hostName"]
        self.host_type = args["equipment"]["hostType"]

        self.altitude = args["geoLoc"]["altitude"]
        self.latitude = args["geoLoc"]["latitude"]
        self.longitude = args["geoLoc"]["longitude"]
        self.site_name = args["geoLoc"]["siteName"]

        self.antenna = args["receiver"]["antenna"]
        self.receiver_id = args["receiver"]["receiverId"]
        self.receiver_mode = args["receiver"]["mode"]
        self.receiver_task = args["receiver"]["task"]
        self.receiver_type = args["receiver"]["type"]

    def write_manatee(self, observations: list[dict[str, any]], source_file_name: str) -> None:
        epoch_seconds = int(time.time())
        dt_object_utc = datetime.datetime.fromtimestamp(
            epoch_seconds, tz=zoneinfo.ZoneInfo("UTC")
        )

        base_file_name = str(uuid.uuid4())
        outfile_json = f"{self.fresh_dir}/{base_file_name}.json"

        results = {
            "equipment": {
                "antenna": self.antenna,
                "receiverId": self.receiver_id,
                "receiverType": self.receiver_type,
                "hostName": self.host_name,
                "hostType": self.host_type,
            },
            "geoLoc": {
                "altitude": self.altitude,
                "latitude": self.latitude,
                "longitude": self.longitude,
                "siteName": self.site_name,
            },
            "timeStamp": {
                "epochSeconds": epoch_seconds,
                "iso8601": dt_object_utc.isoformat(),
            },
            "crate": self.crate_name,
            "fileName": f"{base_file_name}.json",
            "mode": self.receiver_mode,
            "project": self.receiver_task,
            "sourceFileName": source_file_name,
            "version": 1,
            "observations": observations,
        }

        JsonHelper().json_file_writer(outfile_json, results)

    def base_file_name(self) -> str:
        datetime_str = datetime.datetime.now().strftime("%Y%m%d_%H")
        file_name = f"{self.dump_dir}/manatee_{self.host_name}_{datetime_str}"
        return file_name

    def read_observations(self, file_name: str) -> list[dict[str, any]]:
        observations = []

        with open(file_name, "r") as decode_file:
            # must be read line by line because file is not valid json list
            try:
                buffer = decode_file.readlines()
                for raw_row in buffer:
                    json_row = json.loads(raw_row)
                    for json_element in json_row:
                        if "uuid" not in json_element:
                            json_element["uuid"] = str(uuid.uuid4())
                        observations.append(json_element)            
            except Exception as error:
                logger.exception("file read error: %s", error)

        return observations

    def execute(self) -> None:
        bfn = os.path.basename(self.base_file_name())

        os.chdir(self.dump_dir)
        targets = sorted(os.listdir("."))
        logger.info(f"{len(targets)} files noted")

        for target in targets:
            logger.info(f"checking {target}")
            if target.startswith("manatee"):
                if target.startswith(bfn):
                    logger.info(f"skipping {target}")
                else:
                    if target.endswith(".raw"):
                        fresh_target = f"{self.fresh_dir}/{target}"
                        logger.info(f"moving {target} to {fresh_target}")
                        os.rename(target, fresh_target)
                    elif target.endswith(".json"):
                        obs = self.read_observations(target)
                        self.write_manatee(obs, target)                      
#                        fresh_target = f"{self.fresh_dir}/{target}"
#                        logger.info(f"moving {target} to {fresh_target}")
#                        os.rename(target, fresh_target)

#
# argv[1] = configuration filename
# nc -u -l 10110 for test
#
if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
    else:
        file_name = "config.yaml"

    with open(file_name, "r") as in_file:
        try:
            configuration = yaml.load(in_file, Loader=SafeLoader)
            collector = Collector(configuration)
            collector.execute()
        except yaml.YAMLError as error:
            print(error)

# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***
