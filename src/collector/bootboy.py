#
# Title: bootboy.py
# Description: generate configuration file
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#
import json
import socket
import sys
from json import JSONDecodeError
from typing import Any

import yaml


class BootBoy:
    def run_systemctl(self, action: str, service_name: str) -> tuple[int, str]:
        import subprocess

        # Use --no-block for start so systemd queues the job and returns
        # immediately, preventing a deadlock when bootboy itself runs under
        # systemd.
        if action == "start":
            cmd = ["systemctl", "--no-block", action, service_name]
        else:
            cmd = ["systemctl", action, service_name]

        proc = subprocess.run(cmd, capture_output=True, check=False, text=True)
        stderr = proc.stderr.strip()
        return proc.returncode, stderr

    def verify_service_active(self, service_name: str) -> None:
        import time

        # --no-block returns immediately; give systemd a moment to actually
        # start (or fail to start) the service before checking.
        time.sleep(2)
        returncode, _ = self.run_systemctl("is-active", service_name)
        if returncode == 0:
            print(f"{service_name} is active.")
        else:
            print(
                f"{service_name} is NOT active after start; "
                f"check: journalctl -u {service_name}"
            )

    def configuration(self, target: str) -> dict[str, Any]:
        print(f"BootBoy: configuring {target}")

        # Build the path to the admin JSON file
        admin_json_path = f"/var/wombat/admin/{target}.json"

        try:
            with open(admin_json_path, "r", encoding="utf-8") as in_file:
                config_data = json.load(in_file)
        except (JSONDecodeError, OSError) as error:
            print(f"Error reading {admin_json_path}: {error}")
            sys.exit(1)

        # Compose new config dict for YAML output
        receiver = config_data.get("receiver", {})
        geo_loc = config_data.get("geoLoc", {})
        crate_name = config_data.get("crateName", "xxx")
        host_name = config_data.get("hostName", target)
        host_type = config_data.get("type", "xxx")

        yaml_config = {
            "crateName": crate_name,
            "rawDir": "/tmp",
            "equipment": {
                "hostName": host_name,
                "hostType": host_type,
            },
            "receiver": {
                "antenna": receiver.get("antenna", "xxx"),
                "mode": "rtl_ais",
                "receiverId": receiver.get("id", "xxx"),
                "task": receiver.get("task", "xxx"),
                "type": receiver.get("type", "xxx"),
            },
            "freshDir": "/var/wombat/fresh/manatee",
            "geoLoc": geo_loc,
        }

        # Write to config.yaml in the current directory
        try:
            with open("config.yaml", "w", encoding="utf-8") as out_file:
                yaml.dump(yaml_config, out_file, default_flow_style=False)
            print("config.yaml generated successfully.")
        except (OSError, TypeError, yaml.YAMLError) as error:
            print(f"Error writing config.yaml: {error}")
            sys.exit(1)

        return {
            "receiver_task": receiver.get("task", "xxx"),
        }

    def manage_rtl_ais(self) -> None:
        # Only start; never enable. rtl_ais must not auto-start at boot;
        # bootboy.py is the sole entry point that starts this service.
        print("starting rtl_ais service")
        returncode, stderr = self.run_systemctl("start", "rtl_ais.service")
        if returncode == 0:
            print("rtl_ais.service start queued.")
            self.verify_service_active("rtl_ais.service")
        else:
            print(f"failed to start rtl_ais.service: {stderr}")

    def manage_rtl_ais_listener(self) -> None:
        # Only start; never enable. rtl_ais_listener must not auto-start at
        # boot;
        # bootboy.py is the sole entry point that starts this service.
        print("starting rtl_ais_listener service")
        returncode, stderr = self.run_systemctl(
            "start", "rtl_ais_listener.service"
        )
        if returncode == 0:
            print("rtl_ais_listener.service start queued.")
            self.verify_service_active("rtl_ais_listener.service")
        else:
            print(f"failed to start rtl_ais_listener.service: {stderr}")

    def crontab(self) -> None:
        import subprocess

        crontab_entry = (
            "07 13 * * * $HOME/github/mellow-manatee-v1/bin/collector.sh "
            "> /dev/null 2>&1"
        )

        # Always overwrite: collector is dedicated to this workload and must
        # have
        # exactly one cron entry.
        new_crontab = crontab_entry + "\n"
        try:
            proc = subprocess.run(
                ["crontab", "-u", "wombat", "-"],
                check=False,
                input=new_crontab,
                text=True,
            )
            if proc.returncode == 0:
                print("crontab updated for wombat.")
            else:
                print("failed to update wombat's crontab.")
        except OSError as error:
            print(f"error updating wombat's crontab: {error}")

    def execute(self, target: str) -> None:
        self.configuration(target)

        self.crontab()
        self.manage_rtl_ais()
        self.manage_rtl_ais_listener()


if __name__ == "__main__":
    target = socket.gethostname()
    # target = "pi4k"

    bb = BootBoy()
    bb.execute(target)

# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***
