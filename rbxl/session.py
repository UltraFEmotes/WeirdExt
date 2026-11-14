"""Roster diffing, incomplete-session health and nonblocking rediscovery."""
from __future__ import annotations

import threading
import time


class SessionHealth:
    """Retry discovery after sustained incomplete reads, not only exceptions."""

    def __init__(self, grace=3.0):
        self.grace = grace
        self.incomplete_since = None

    def observe(self, frame, now):
        if frame.complete and frame.fov is not None:
            self.incomplete_since = None
            return True
        if self.incomplete_since is None:
            self.incomplete_since = now
        return now - self.incomplete_since < self.grace


class SessionRecovery:
    """One read-only discovery worker; the UI thread never waits for a sweep.

    poll() transfers ownership of a successful (pid, reader) to the caller.
    Failed attempts retry indefinitely, spaced from completion rather than
    launch. close() disposes late results without joining a slow heap sweep.
    """

    def __init__(self, attach, find_pid, retry_interval=2.0, launch=None):
        self.attach, self.find_pid = attach, find_pid
        self.retry_interval = retry_interval
        self.launch = launch or self._launch
        self.lock = threading.Lock()
        self.pending = False
        self.closed = False
        self.result = None
        self.next_attempt = 0.0
        self.attempts = 0
        self.error = None

    @staticmethod
    def _launch(job):
        threading.Thread(target=job, name="session-discovery", daemon=True).start()

    @staticmethod
    def _dispose(reader):
        if reader is not None:
            try:
                reader.close()
            except Exception as exc:
                print(f"[session] reader cleanup failed: {exc}", flush=True)

    def _work(self):
        with self.lock:
            if self.closed:
                return
        reader = None
        try:
            pid = self.find_pid()
            if pid is None:
                raise RuntimeError("Roblox is not running")
            reader = self.attach(pid)
            if self.find_pid() != pid:
                raise RuntimeError("Roblox process changed during discovery")
            result = (pid, reader, None)
        except Exception as exc:
            self._dispose(reader)
            result = (None, None, str(exc))
        with self.lock:
            if not self.closed:
                self.result = result
                return
        self._dispose(result[1])

    def poll(self, now):
        with self.lock:
            if self.closed:
                return None
            if self.result is not None:
                pid, reader, self.error = self.result
                self.result = None
                self.pending = False
                self.next_attempt = now + self.retry_interval
                if reader is not None:
                    return pid, reader
            if self.pending or now < self.next_attempt:
                return None
            self.pending = True
            self.attempts += 1
        try:
            self.launch(self._work)
        except Exception as exc:
            with self.lock:
                self.pending = False
                self.error = str(exc)
                self.next_attempt = now + self.retry_interval
        return None

    def close(self):
        with self.lock:
            self.closed = True
            result, self.result = self.result, None
        if result is not None:
            self._dispose(result[1])


class SessionWatcher:
    """Diffs the Players roster between frames; bounded toast feed."""

    def __init__(self, keep: float = 4.0):
        self.keep = keep
        self.known: set[int] = set()
        self.names: dict[int, str] = {}
        self.toasts: list[tuple[float, str]] = []
        self.events: list[str] = []

    def observe(self, roster_ids, names, now=None):
        now = time.monotonic() if now is None else now
        current = set(roster_ids)
        for player in sorted(current - self.known):
            text = f"{names.get(player, '?')} joined"
            self.toasts.append((now, text))
            self.events.append(text)
        for player in sorted(self.known - current):
            text = f"{self.names.get(player, '?')} left"
            self.toasts.append((now, text))
            self.events.append(text)
        self.known = current
        self.names = {player: names.get(player, self.names.get(player, "?"))
                      for player in current}
        while len(self.toasts) > 6:
            self.toasts.pop(0)
        return list(self.toasts)

    def feed(self, now=None):
        """Toasts younger than `keep` seconds, oldest first."""
        now = time.monotonic() if now is None else now
        self.toasts = [(stamp, text) for stamp, text in self.toasts if now - stamp < self.keep]
        return [{"text": text, "age": now - stamp} for stamp, text in self.toasts]

    def observe_rejoin(self, now=None):
        now = time.monotonic() if now is None else now
        self.known.clear()
        self.names.clear()
        self.toasts.append((now, "You reconnected to the game"))
        self.events.append("Reconnected — game loaded; updates resumed")
        return list(self.toasts)
