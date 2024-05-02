#!/bin/bash

set -e

[ -n "$1" -a "$1" = "clean" ] && rm -rf .venv

python -m venv .venv
source .venv/bin/activate

if [ -z "$LOCAL_INSTALL" -o "$LOCAL_INSTALL" = "0" ]; then
    pip3 install ${PIP_OPTIONS} --upgrade pip wheel setuptools
fi

#export PIP_INDEX_URL="http://pypi.privateserver.one/simple"
#export PIP_TRUSTED_HOST="pypi.privateserver.one"
pip3 install ${PIP_OPTIONS} .
pip3 install ${PIP_OPTIONS} -r requirements.txt
