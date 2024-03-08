#!/bin/bash

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title endfinder
# @raycast.mode compact

# Optional parameters:
# @raycast.icon 🤖

# Documentation:
# @raycast.description Close all finder window
# @raycast.author Darren Victoriano

osascript -e 'tell application "Finder" to close windows'
