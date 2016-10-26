#!/bin/bash

grep -oEh '[A-Z][a-z/]+:?\ ?([A-Za-z/]+\ )?([A-Za-z]+):' -r ${1} | sort -u
