
# Automated Router Config Backup ⚙️

A Python Network Automation utility designed for Network Operations Center (NOC) engineers to securely extract and archive running configurations from Cisco IOS devices.

**Features:**
* Utilizes the `netmiko` library for programmatic SSH connections to routing and switching hardware.
* Automatically executes `show running-config` and archives the output to a timestamped `.cfg` text file.
* Handles standard network timeouts and authentication failures gracefully without freezing the UI via Python `threading`.
* Includes an Offline Simulation Mode to demonstrate operational logic without requiring active physical hardware.

*Built as Day 9 of a 30-Day Network Engineering & Security portfolio streak.*
