#! /bin/bash
sudo sh -c 'XDG_RUNTIME_DIR=/tmp/runtime-root; python rpi.py 2> /dev/null'
# sudo sh -c 'XDG_RUNTIME_DIR=/tmp/runtime-root; python rpi.py'

# must run as sudo for neopixel library to work

# sudo usually only allows running one command, but we need multiple. 
#   change command to 'sh' (shell)
#   -c switch means "run these commands"
#   we've bundled 2 commands into one with sh, which is run as su
# set XDG_RUNTIME_DIR manually to avoid a warning and error message. Using su temporarily unsets this value so we manually set it again.

# python rpi.py is our script

# 2> /dev/null redirects stderr to /dev/null, this hides the camera setup info. If we want to view /dev/null, comment line 2 and uncomment line 3
