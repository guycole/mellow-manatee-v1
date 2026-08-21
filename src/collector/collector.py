#
# Title: collector.py
# Description:
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#

import datetime
import json
import logging
import sys
import time
import uuid
import zoneinfo

import socket

import yaml
from yaml.loader import SafeLoader

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("manatee")


class Collector:

    def __init__(self, args: dict[str, any]):
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

    def json_file_writer(self, file_name: str, json_data: dict[str, any]) -> None:
        try:
            with open(file_name, "w") as out_file:
                json.dump(json_data, out_file, indent=4)
        except Exception as error:
            print(error)

    def execute2(self) -> None:
        print(f"collector execute: {self.receiver_task}")

        base_file_name = str(uuid.uuid4())
        print(f"base filename: {base_file_name}")

        epoch_seconds = int(time.time())
        dt_object_utc = datetime.datetime.fromtimestamp(
            epoch_seconds, tz=zoneinfo.ZoneInfo("UTC")
        )

        outfile_json = f"{self.fresh_dir}/{base_file_name}.json"

        observations = []

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
            "version": 1,
            "observations": observations,
        }

        self.json_file_writer(outfile_json, results)


    def execute(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind(("127.0.0.1", 10110))
            logger.info("listening on UDP 127.0.0.1:10110")
            while True:
                data, _ = sock.recvfrom(4096)
                print(data.decode("utf-8", errors="replace"), end="", flush=True)

#
# argv[1] = configuration filename
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
