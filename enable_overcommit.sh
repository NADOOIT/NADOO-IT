#!/bin/bash

# Add 'vm.overcommit_memory = 1' to /etc/sysctl.conf if it's not already present
if ! grep -q "vm.overcommit_memory = 1" /etc/sysctl.conf; then
  echo "vm.overcommit_memory = 1" | sudo tee -a /etc/sysctl.conf
fi

# Apply the changes without rebooting
sudo sysctl -p