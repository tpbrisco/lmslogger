
all:
	echo "Make install, make test"

PYTHON_VIRTUALENV = /etc/lmslogger
PYTHON_VIRTUALENV_PYTHON_COMMAND = /etc/lmslogger/venv/bin/python -m lmslogger

.ONESHELL:
install: lmslogger.service.template requirements.txt
	@bash installer.sh

uninstall:
	@rm -rf /etc/lmslogger /etc/systemd/system/lmslogger.service
