#!/bin/bash
chmod +x setup.sh
./setup.sh
source .triang_env/bin/activate
python -m gui.main