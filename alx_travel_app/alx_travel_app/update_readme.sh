#!/bin/bash

# Script to update root README.md with content from alx_travel_app/README.md

echo "Updating root README.md with content from alx_travel_app/README.md..."

# Run the Python script
python3 update_readme.py

# Check if the update was successful
if [ $? -eq 0 ]; then
    echo "README update completed successfully!"
else
    echo "README update failed!"
    exit 1
fi 