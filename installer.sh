#!/bin/bash

LMSDIR=${LMSDIR:-"/etc/lmslogger"}
PYTHON_COMMAND=${PYTHON_COMMAND:-"${LMSDIR}/venv/bin/python"}

if [[ ! -d "${LMSDIR}"  ]]; then
    mkdir "${LMSDIR}"
fi
cp lmslogger.service.template requirements.txt "${LMSDIR}/"
mkdir -p "${LMSDIR}/src/lmslogger"
cp -rp src/lmslogger/{config,daemon,network}.py  "${LMSDIR}/src/lmslogger"

# shellcheck disable=SC2164
cd "${LMSDIR}"
python -m virtualenv venv
"${PYTHON_COMMAND}" -m pip install -r requirements.txt

# set environment variables, when known (dont overwrite if someone already updated it)
if [[ ! -f lmslogger.env ]]; then
    cat <<EOF > lmslogger.env
LMS_HOST=YOURLMSHOST
# LMS_PORT defaults to 9090
# LMS_COMMAND defaults to 'listen 1', not recommended to change
# LMS_POLL_INTERVAL defaults to 60, not recommended to change"
# LMS_ALIVE_MESSAGE default to true, remove if output is too cluttered
EOF
fi


#
export RUNDIR="${LMSDIR}"
export EXECCMD="${PYTHON_COMMAND}"

# shellcheck disable=SC2016
envsubst '$RUNDIR $EXECCMD' < lmslogger.service.template > lmslogger.service

# shellcheck disable=SC2164
cd /etc/systemd/system
ln -s "${LMSDIR}/lmslogger.service" lmslogger.service
