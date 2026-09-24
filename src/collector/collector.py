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
from typing import Any

import pydantic

import yaml
from yaml.loader import SafeLoader

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("collector")


class Equipment(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(populate_by_name=True)

    antenna: str
    receiver_id: int = pydantic.Field(alias="receiverId")
    receiver_type: str = pydantic.Field(alias="receiverType")
    host_name: str = pydantic.Field(alias="hostName")
    host_type: str = pydantic.Field(alias="hostType")


class GeoLoc(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(populate_by_name=True)

    altitude: float
    latitude: float
    longitude: float
    site_name: str = pydantic.Field(alias="siteName")


class Job(pydantic.BaseModel):
    mode: str
    project: str
    task: str


class TimeStamp(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(populate_by_name=True)

    epoch_seconds: int = pydantic.Field(
        default_factory=lambda: int(time.time()), alias="epochSeconds"
    )
    iso8601: str = ""

    @pydantic.model_validator(mode="after")
    def sync_iso8601_from_epoch(self) -> "TimeStamp":
        self.iso8601 = datetime.datetime.fromtimestamp(
            self.epoch_seconds, tz=zoneinfo.ZoneInfo("UTC")
        ).isoformat()
        return self


class ManateeModel(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(populate_by_name=True)

    equipment: Equipment
    geo_loc: GeoLoc = pydantic.Field(alias="geoLoc")
    job: Job
    time_stamp: TimeStamp = pydantic.Field(alias="timeStamp")
    crate: str
    file_name: str = pydantic.Field(alias="fileName")
    source_file_name: str = pydantic.Field(alias="sourceFileName")
    version: int = 1
    observations: list[dict[str, Any]]


class Collector:
    def __init__(self, args: dict[str, Any]):
        self.crate_name = args["crateName"]
        self.fresh_dir = args["freshDir"]
        self.raw_dir = args["rawDir"]

        equipment_cfg = args["equipment"]
        receiver_cfg = args["receiver"]
        geo_loc_cfg = args["geoLoc"]

        self.equipment = Equipment(
            antenna=receiver_cfg["antenna"],
            receiver_id=receiver_cfg["receiverId"],
            receiver_type=receiver_cfg["type"],
            host_name=equipment_cfg["hostName"],
            host_type=equipment_cfg["hostType"],
        )
        self.geo_loc = GeoLoc(
            altitude=geo_loc_cfg["altitude"],
            latitude=geo_loc_cfg["latitude"],
            longitude=geo_loc_cfg["longitude"],
            site_name=geo_loc_cfg["siteName"],
        )
        self.job = Job(
            mode=receiver_cfg["mode"],
            project="manatee-v1",
            task=receiver_cfg["task"],
        )

    def write_manatee(
        self, observations: list[dict[str, Any]], source_file_name: str
    ) -> None:
        base_file_name = str(uuid.uuid4())
        outfile_json = f"{self.fresh_dir}/{base_file_name}.json"
        logger.info("writing manatee file: %s", outfile_json)

        manatee_model = ManateeModel(
            equipment=self.equipment,
            geo_loc=self.geo_loc,
            job=self.job,
            time_stamp=TimeStamp(),
            crate=self.crate_name,
            file_name=f"{base_file_name}.json",
            source_file_name=source_file_name,
            observations=observations,
        )

        with open(outfile_json, "w", encoding="utf-8") as out_file:
            out_file.write(manatee_model.model_dump_json(indent=4, by_alias=True))

    def base_file_name(self) -> str:
        datetime_str = datetime.datetime.now().strftime("%Y%m%d_%H")
        file_name = (
            f"{self.raw_dir}/manatee_{self.equipment.host_name}_{datetime_str}"
        )
        return file_name

    def read_observations(self, file_name: str) -> list[dict[str, Any]]:
        logger.info("reading observations from file: %s", file_name)

        observations: list[dict[str, Any]] = []

        with open(file_name, "r", encoding="utf-8") as decode_file:
            # must be read line by line because file is not valid json list
            try:
                buffer = decode_file.readlines()
                for raw_row in buffer:
                    json_row = json.loads(raw_row)
                    for json_element in json_row:
                        observations.append(json_element)
            except Exception as error:
                logger.exception("file read error: %s", error)

        return observations

    def execute(self) -> int:
        bfn = os.path.basename(self.base_file_name())

        os.chdir(self.raw_dir)
        targets = sorted(os.listdir("."))
        logger.info("%d files noted", len(targets))

        for target in targets:
            logger.info("checking %s", target)
            if target.startswith("manatee"):
                if target.startswith(bfn):
                    logger.info("skipping %s", target)
                else:
                    fresh_target = f"{self.fresh_dir}/{target}"

                    if target.endswith(".raw"):
                        pass
                    elif target.endswith(".json"):
                        obs = self.read_observations(target)
                        self.write_manatee(obs, target)

                    logger.info("moving %s to %s", target, fresh_target)
                    os.rename(target, fresh_target)

        return 0

#
# argv[1] = configuration filename
# nc -u -l 10110 for test
#
if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
    else:
        file_name = "config.yaml"

    with open(file_name, "r", encoding="utf-8") as in_file:
        try:
            configuration = yaml.load(in_file, Loader=SafeLoader)
            collector = Collector(configuration)
            exit(collector.execute())
        except yaml.YAMLError as error:
            logger.error("YAML parse error: %s", error)

    exit(1)

# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***
