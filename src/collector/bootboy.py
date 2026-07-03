#
# Title: bootboy.py
# Description: generate configuration file
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#
import json
import socket
import sys

import yaml
from yaml.loader import SafeLoader

class BootBoy:

    def configuration(self, target: str) -> dict[str, any]:
        print(f"BootBoy: configuring {target}")

        # Build the path to the admin JSON file
        admin_json_path = f"/var/wombat/admin/{target}.json"

        try:
            with open(admin_json_path, "r") as f:
                config_data = json.load(f)
        except Exception as e:
            print(f"Error reading {admin_json_path}: {e}")
            sys.exit(1)

        # Compose new config dict for YAML output
        receiver = config_data.get("receiver", {})
        geo_loc = config_data.get("geoLoc", {})
        crate_name = config_data.get("crateName", "xxx")
        host_name = config_data.get("hostName", target)
        host_type = config_data.get("type", "xxx")

        yaml_config = {
            "crateName": crate_name,
            "equipment": {
                "hostName": host_name,
                "hostType": host_type,
            },
            "receiver": {
                "antenna": receiver.get("antenna", "xxx"),
                "mode": "default",
                "receiverId": receiver.get("id", "xxx"),
                "task": receiver.get("task", "xxx"),
                "type": receiver.get("type", "xxx"),
            },
            "freshDir": "/var/wombat/fresh/manatee",
            "geoLoc": geo_loc,
        }

        # Write to config.yaml in the current directory
        try:
            with open("config.yaml", "w") as f:
                yaml.dump(yaml_config, f, default_flow_style=False)
            print("config.yaml generated successfully.")
        except Exception as e:
            print(f"Error writing config.yaml: {e}")
            sys.exit(1)

        return {
            "receiver_task": receiver.get("task", "xxx"),
        }

    def crontab(self) -> None:
        import subprocess

        crontab_entry = (
            "*/10 * * * * $HOME/github/mellow-manatee-v1/bin/collector.sh > /dev/null 2>&1"
        )

        # Always overwrite — collector is dedicated to this workload and must have
        # exactly one cron entry.
        new_crontab = crontab_entry + "\n"
        try:
            proc = subprocess.run(
                ["crontab", "-u", "wombat", "-"], input=new_crontab, text=True
            )
            if proc.returncode == 0:
                print("Crontab updated for wombat.")
            else:
                print("Failed to update wombat's crontab.")
        except Exception as e:
            print(f"Error updating wombat's crontab: {e}")

    def execute(self, target: str) -> None:
        config = self.configuration(target)
        self.crontab()


#
#
#
if __name__ == "__main__":
    target = socket.gethostname()
    # target = "pi4k"

    bb = BootBoy()
    bb.execute(target)

# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***
