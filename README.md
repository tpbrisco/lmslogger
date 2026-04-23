# LMS Logger Daemon

A Python system daemon that connects to a remote host on port 9090, sends a "listen 1" command, and receives/decodes status information.

Configure what you would like to see through LMS -> Settings -> Advanced -> Logging.  What is enabled there winds up on the output of the lmslogger.

## Configuration

The daemon can be configured via environment variables:

- `LMS_HOST`: Remote host (default: localhost)
- `LMS_PORT`: Port number (default: 9090)
- `LMS_COMMAND`: Command to send (default: "listen 1")

You can set these in a `.env` file or export them in your environment.

While the instruction below indicate installing it as a system
service, no privileges are necessary, and this can run and operate as
a user systemd service.

The lmslogger.service has a few items to be filled in:
- YOURUSERNAME - the username under which the service should run
- YOUR\_LMS\_HOST - the LMS server
- PYTHON\_VIRTUALENV - full path to the virtualenv python -
  e.g. /home/me/lmslogger/.venv/
- PYTHON\_VIRTUALENV\_PYTHON_COMMAND - the virtualenv path to python -
  e.g. /home/me/lmslogger/.venv/bin/python -m lmslogger.daemon

## Setup

1. Create virtual environment: `python3 -m venv dev`
2. Activate: `source dev/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Run type check: `mypy src/`
5. Run tests: `pytest`
6. Configuration service: `cp lmslogger.service.temple lmslogger.service`
7. Install service: `cp lmslogger.service ~/.config/systemd/user/`
8. Enable: `systemctl --user enable lmslogger`
9. Start: `systemctl --user start lmslogger`
10. Check logs: `journalctl --user -u lmslogger -f`

## SDLC

See docs/SDLC.md for the software development life cycle.

## ADDITIONAL REFERENCES
See [LMS Command Line Interface](https://lyrion.org/reference/cli/introduction/)
