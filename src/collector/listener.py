#
# Title: listener.py
# Description: listen for AIS data on UDP port 10110 and write two files
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#

import json
import logging
import os
import socket
import sys
import time
import uuid
from typing import Any

import pydantic

from pyais import decode

import yaml
from yaml.loader import SafeLoader

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("listener")


class Observation(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(populate_by_name=True, extra="allow")

    epoch_seconds: int = pydantic.Field(alias="epochSeconds")
    message_uuid: str = pydantic.Field(alias="uuid")


class Listener:
    def __init__(self, args: dict[str, Any]):
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

    def base_file_name(self) -> str:
        import datetime

        datetime_str = datetime.datetime.now().strftime("%Y%m%d_%H")
        file_name = f"{self.dump_dir}/manatee_{self.host_name}_{datetime_str}"
        return file_name

    def write_raw_file(self, base_file_name: str, data: bytes) -> bool:
        raw_file_name = f"{base_file_name}.raw"

        if os.path.exists(raw_file_name):
            fresh_flag = False
            mode = "ab"
        else:
            fresh_flag = True
            mode = "wb"

        with open(raw_file_name, mode) as out_file:
            out_file.write(data)

        return fresh_flag

    def write_decode_file(self, base_file_name: str, data: bytes) -> bool:
        parts_buffer: dict[str, list[str]] = {}
        decoded_messages: list[dict[str, Any]] = []
        for sentence in data.decode("utf-8", errors="replace").splitlines():
            sentence = sentence.strip()
            if not sentence:
                continue

            try:
                fields = sentence.split(",")
                total_parts = int(fields[1])
                seq_id = fields[3]
                if total_parts == 1:
                    message = decode(sentence).asdict()
                    print(message, flush=True)
                    decoded_messages.append(message)
                else:
                    if seq_id not in parts_buffer:
                        parts_buffer[seq_id] = []
                    parts_buffer[seq_id].append(sentence)
                    if len(parts_buffer[seq_id]) == total_parts:
                        message = decode(*parts_buffer.pop(seq_id)).asdict()
                        print(message, flush=True)
                        decoded_messages.append(message)
            except Exception as error:
                logger.warning("decode error: %s", error)

        raw_file_name = f"{base_file_name}.json"
        if os.path.exists(raw_file_name):
            fresh_flag = False
            mode = "ab"
        else:
            fresh_flag = True
            mode = "wb"

        epoch_seconds = int(time.time())

        observations: list[dict[str, Any]] = []
        for message in decoded_messages:
            observation = Observation(
                **message,
                epoch_seconds=epoch_seconds,
                message_uuid=str(uuid.uuid4()),
            )
            observations.append(observation.model_dump(by_alias=True))

        with open(raw_file_name, mode) as out_file:
            out_file.write(json.dumps(observations, default=str).encode("utf-8"))
            out_file.write(b"\n")

        return fresh_flag

    def execute(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind(("127.0.0.1", 10110))
            logger.info("listening on UDP 127.0.0.1:10110")

            while True:
                data, _ = sock.recvfrom(4096)

                bfn = self.base_file_name()

                self.write_raw_file(bfn, data)
                self.write_decode_file(bfn, data)


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
            listener = Listener(configuration)
            listener.execute()
        except yaml.YAMLError as error:
            logger.error("YAML parse error: %s", error)

    exit(1)

# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***
