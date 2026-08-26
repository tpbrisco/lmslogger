# LMS Logger Daemon

A Python system daemon that connects to a remote host on port 9090, sends a "listen 1" command, and receives/decodes status information.

Configure what you would like to see through LMS -> Settings -> Advanced -> Logging.  What is enabled there winds up on the output of the lmslogger.

## Configuration

The daemon can be configured via environment variables:

- `LMS_HOST`: Remote host (default: localhost)
- `LMS_PORT`: Port number (default: 9090)
- `LMS_COMMAND`: Command to send (default: "listen 1")
- `LMS_POLL_INTERVAL`: Time in seconds to wait between alive polls (default: 60)
- `LMS_ALIVE_MESSAGES`: Whether to print alive messages when no data is received (default: true)

You can set these in a `.env` file or export them in your environment.

Command-line flags can override both the `.env` file and environment variables:

- `--env-file <path>`: Path to the `.env` file to load (default: `.env`)
- `--host <host>`: LMS host to connect to
- `--port <port>`: LMS port to connect to
- `--command <command>`: Command to send to LMS after connecting
- `--poll-interval <seconds>`: Seconds to wait between heartbeat polls
- `--alive-messages`: Print alive messages when no data is received
- `--no-alive-messages`: Disable alive messages

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
3. Install runtime dependencies: `pip install -r requirements.txt`
   - To install developer/testing tools (pytest, coverage, mypy), run either:

     - From `requirements-dev.txt`:

       ```bash
       pip install -r requirements-dev.txt
       ```

     - Or using PEP-621 extras (preferred if you installed the package editable):

       ```bash
       # install project and dev extras
       python -m pip install -e .[dev]
       ```
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

## Testing

Run the test suite locally either by installing the package into a virtual environment or by setting `PYTHONPATH` to `src` (the CI uses this pattern).

Recommended (virtualenv + editable install):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
pytest -q
```

Run without installing (export `PYTHONPATH`):

```bash
export PYTHONPATH=src
python3 -m pytest -q
```

If you need to test with environment-based configuration, set `LMS_` variables (or use a `.env` file):

```bash
export LMS_HOST=example.com
export LMS_PORT=1234
export LMS_COMMAND="status"
```

The GitHub Action workflow `/.github/workflows/test-manual.yml` sets `PYTHONPATH=src` before running pytest and mypy.

### Type checking (mypy)

You can run `mypy` to perform static type checking. If you installed the package in a virtual environment (recommended), run:

```bash
python -m mypy src
```

Or run without installing by exporting `PYTHONPATH` (same pattern as the CI):

```bash
export PYTHONPATH=src
python3 -m mypy src
```

Install `mypy` into your environment with `pip install mypy` or via `requirements.txt` if it is included there.
