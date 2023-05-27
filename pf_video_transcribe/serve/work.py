from __future__ import annotations

import datetime
import email.utils
import functools
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler
from http.server import ThreadingHTTPServer
import logging
import os.path
import re
from typing import BinaryIO
from typing import Union

from termcolor import colored

_logger = logging.getLogger(__name__.replace(".work", ""))
_dbg = functools.partial(_logger.log, logging.DEBUG)
_inf = functools.partial(_logger.log, logging.INFO)
_wrn = functools.partial(_logger.log, logging.WARN)

_range_re = re.compile(
    r"bytes=(?P<start>\d+)-",
)


class RequestHandler(SimpleHTTPRequestHandler):
    # Just SimpleHTTPRequestHandler handling "Range" requests,
    # required by video seek, returning Content-Range
    #
    # Also generates pretty "/"" (main index), only for .html files
    directory: str

    def log_error(self, fmt: str, *args: object) -> None:
        message = fmt % args
        _wrn(colored(self.address_string(), "blue") + " " + colored(message, "red"))

    def log_request(
        self,
        code: Union[str, int, HTTPStatus] = "-",
        size: Union[str, int] = "-",
    ) -> None:
        if isinstance(code, HTTPStatus):
            code = code.value

        code_str = str(code)
        code_color = "green"
        if code_str[0] in ("4", "5"):
            code_color = "red"

        _inf(
            colored(self.address_string(), "blue")
            + " "
            + colored(self.requestline, "cyan")
            + " "
            + colored(code_str, code_color)
            + " "
            + colored(str(size), "cyan")
        )

    def log_message(self, fmt: str, *args: object) -> None:
        message = fmt % args
        _dbg(colored(self.address_string(), "blue") + " " + colored(message, "cyan"))

    def do_GET(self) -> None:
        r = self.headers.get("Range")
        if r:
            m = _range_re.match(r)
            path = self.translate_path(self.path)
            if m and os.path.isfile(path):
                start = int(m.group("start"))
                try:
                    with open(path, "rb") as f:
                        self._do_GET_range(f, path, start)
                        return
                except Exception:
                    pass

        super().do_GET()

    def _do_GET_range(self, f: BinaryIO, path: str, start: int) -> None:
        # most of this code is similar to send_headers() handling files:
        fs = os.fstat(f.fileno())

        total_size = fs[6]
        size = total_size - start
        if size < 0:
            self.send_response(HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE)
            self.end_headers()
            return

        # Use browser cache if possible
        if "If-Modified-Since" in self.headers and "If-None-Match" not in self.headers:
            # compare If-Modified-Since and time of last file modification
            try:
                ims = email.utils.parsedate_to_datetime(
                    self.headers["If-Modified-Since"]
                )
            except (TypeError, IndexError, OverflowError, ValueError):
                # ignore ill-formed values
                pass
            else:
                if ims and ims.tzinfo is None:
                    # obsolete format with no timezone, cf.
                    # https://tools.ietf.org/html/rfc7231#section-7.1.1.1
                    ims = ims.replace(tzinfo=datetime.timezone.utc)
                if ims and ims.tzinfo is datetime.timezone.utc:
                    # compare to UTC datetime of last modification
                    last_modif = datetime.datetime.fromtimestamp(
                        fs.st_mtime, datetime.timezone.utc
                    )
                    # remove microseconds, like in If-Modified-Since
                    last_modif = last_modif.replace(microsecond=0)

                    if last_modif <= ims:
                        self.send_response(HTTPStatus.NOT_MODIFIED)
                        self.end_headers()
                        return

        f.seek(start)
        end = start + size - 1
        ctype = self.guess_type(path)

        self.send_response(HTTPStatus.PARTIAL_CONTENT)
        self.send_header("Content-type", ctype)
        self.send_header("Content-Length", str(size))
        self.send_header("Content-Range", f"bytes {start}-{end}/{total_size}")
        self.send_header("Last-Modified", self.date_time_string(int(fs.st_mtime)))
        self.end_headers()
        try:
            self.copyfile(f, self.wfile)  # type: ignore
        except BrokenPipeError:
            self.log_error("Broken pipe, likely client closed the connection")


class Server(ThreadingHTTPServer):
    directory: str

    def __init__(self, directory: str, port: int) -> None:
        self.directory = directory
        super().__init__(("", port), RequestHandler)

    def finish_request(self, request: object, client_address: object) -> None:
        self.RequestHandlerClass(
            request, client_address, self, directory=self.directory  # type: ignore
        )


def serve(port: int, directory: str) -> None:
    with Server(directory, port) as server:
        host, port = server.socket.getsockname()[:2]
        url_host = f"[{host}]" if ":" in host else host
        _inf(
            "Serving "
            + colored(directory, "cyan")
            + " at: "
            + colored(f"http://{url_host}:{port}/", "cyan")
        )
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            _dbg("Keyboard interrupt received, exiting.")
