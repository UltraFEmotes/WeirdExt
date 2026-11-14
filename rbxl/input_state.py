"""Physical input relayed by the unprivileged helper; receiver-clock freshness."""
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class InputState:
    focused: bool = False
    aim_held: bool = False
    space_presses: int = 0
    received: float | None = None
    available: bool = True

    @classmethod
    def from_event(cls, event, received):
        if (type(event.get("focused")) is not bool or type(event.get("aim_held")) is not bool
                or type(event.get("space_presses")) is not int
                or not 0 <= event["space_presses"] < 2 ** 53 or not math.isfinite(received)
                or type(event.get("available", True)) is not bool):
            raise ValueError("invalid native input state")
        return cls(event["focused"], event["aim_held"], event["space_presses"], received,
                   event.get("available", True))

    def fresh(self, now):
        return self.received is not None and math.isfinite(now) and 0 <= now - self.received < 0.1
