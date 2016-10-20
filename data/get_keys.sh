#!/bin/bash

grep -oEh '([A-Za-z\ /]+\ )*([A-Za-z]+):' -r . | sort -u
