#!/bin/bash

# Change to the scripts directory
cd "$(dirname "$0")"

# Run the Python command from the scripts directory
python -m src.audio_yaml_generator.cli -m ../samples