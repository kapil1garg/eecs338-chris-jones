#!/bin/bash

grep -oEh '([A-Za-z\ /]+\ )*([A-Za-z]+):' -r ${1} | sort -u
