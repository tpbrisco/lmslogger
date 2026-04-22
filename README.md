# LMS Logger Daemon

A Python system daemon that connects to a remote host on port 9090, sends a "listen 1" command, and receives/decodes status information.

## Configuration

The daemon can be configured via environment variables:

- `LMS_HOST`: Remote host (default: localhost)
- `LMS_PORT`: Port number (default: 9090)
- `LMS_COMMAND`: Command to send (default: "listen 1")

You can set these in a `.env` file or export them in your environment.

## Setup

1. Create virtual environment: `python3 -m venv dev`
2. Activate: `source dev/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Run type check: `mypy src/`
5. Run tests: `pytest`
6. Install service: `sudo cp lmslogger.service /etc/systemd/system/`
7. Enable: `sudo systemctl enable lmslogger`
8. Start: `sudo systemctl start lmslogger`
9. Check logs: `journalctl -u lmslogger -f`

## SDLC

See docs/SDLC.md for the software development life cycle.

## ADDITIONAL REFERENCES
See [LMS Command Line Interface](https://lyrion.org/reference/cli/introduction/)