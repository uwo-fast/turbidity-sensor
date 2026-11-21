#!/usr/bin/env python3
"""Show the rig's summary.csv on a read-only page, served to this computer only.

Every --interval seconds this reads summary.csv into memory, and serves that copy, replaced
whole, so the page never sees a half-read file. It only reads the original and writes no files,
and shares nothing else with rig.py: it cannot reach the motor or the Nano, and rig.py runs the
same with or without it. The address is fixed to 127.0.0.1 and only the named files below can
be fetched. Standard library only.
"""
import argparse
import errno
import http.server
import pathlib
import signal
import sys
import threading
import time
import tomllib

ADDRESS = "127.0.0.1"
HERE = pathlib.Path(__file__).resolve().parent
PAGE_DIR = HERE / "view"
COPY_NAME = "summary.csv"
# The page may load only its own files and talk only to this server.
POLICY = "default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; base-uri 'none'; form-action 'none'"
PAGES = {
    "/": (PAGE_DIR / "index.html", "text/html; charset=utf-8"),
    "/view.css": (PAGE_DIR / "view.css", "text/css; charset=utf-8"),
    "/view.js": (PAGE_DIR / "view.js", "text/javascript; charset=utf-8"),
}


class Latest:
    """The last good read of the summary. Replacing content is one step, so a request gets all of one read."""

    content = None


def copy_once(source, latest):
    with open(source, "rb") as original:
        latest.content = original.read()


def keep_copying(source, latest, interval_s):
    problem = None
    while True:
        try:
            copy_once(source, latest)
            problem = None
        except OSError as error:
            # Keep serving the last good copy. Say so once, not every interval.
            if str(error) != problem:
                problem = str(error)
                print(f"cannot read {source}: {error}", file=sys.stderr, flush=True)
        time.sleep(interval_s)


def make_handler(latest):
    class Handler(http.server.BaseHTTPRequestHandler):
        # With no do_POST, do_PUT or the like, anything but GET is refused with 501.
        def do_GET(self):
            path = self.path.split("?", 1)[0]
            if path == "/" + COPY_NAME:
                body, kind = latest.content, "text/csv; charset=utf-8"
            elif path in PAGES:
                body, kind = PAGES[path][0].read_bytes(), PAGES[path][1]
            else:
                body, kind = None, None
            if body is None:  # not a named file, or nothing read yet
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", kind)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", POLICY)
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format, *args):  # noqa: A002
            pass  # a page refreshing every 30 s would fill the journal

    return Handler


def interrupt(_signal, _frame):
    raise SystemExit(0)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", default=str(HERE / "rig.toml"), help="rig.toml, for its data_dir")
    parser.add_argument("--source", help="the summary.csv to show; default: the one in data_dir")
    parser.add_argument("--port", type=int, default=8080, help="0 picks a free port")
    parser.add_argument("--interval", type=float, default=30.0, help="seconds between copies")
    args = parser.parse_args(argv)

    if args.source:
        source = pathlib.Path(args.source).expanduser()
    else:
        with open(args.config, "rb") as config_file:
            source = pathlib.Path(tomllib.load(config_file)["data_dir"]).expanduser() / COPY_NAME

    signal.signal(signal.SIGTERM, interrupt)
    signal.signal(signal.SIGHUP, interrupt)
    latest = Latest()
    try:
        server = http.server.ThreadingHTTPServer((ADDRESS, args.port), make_handler(latest))
    except OSError as error:
        if error.errno != errno.EADDRINUSE:
            raise
        print(
            f"port {args.port} is already in use, probably by another view_server.py: check with pgrep -af view_server",
            file=sys.stderr,
        )
        return 1
    threading.Thread(target=keep_copying, args=(source, latest, args.interval), daemon=True).start()
    print(f"showing {source} at http://{ADDRESS}:{server.server_address[1]}/", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
