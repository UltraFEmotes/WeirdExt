"""Validated settings shared by the native panel and the polling loop."""
from dataclasses import asdict, dataclass, fields
import math

CHOICES = {"aim_method": ("mouse", "camera"), "aim_part": ("head", "torso", "closest"),
           "aim_priority": ("crosshair", "distance")}
RANGES = {"box_height": (1, 20), "box_ratio": (0.2, 2), "fps": (1, 60), "fov": (30, 120),
          "walk_speed": (0, 150), "jump_power": (0, 200), "aim_radius": (20, 400),
          "aim_smoothing": (1, 20), "fly_speed": (5, 300), "aim_health_value": (1, 1000),
          "silent_radius": (20, 600)}


@dataclass(frozen=True)
class Settings:
    esp_enabled: bool = True
    boxes: bool = True
    names: bool = True
    distances: bool = True
    center_marker: bool = True
    show_local: bool = False
    esp_skeleton: bool = False
    esp_tracers: bool = False
    esp_offscreen: bool = False
    esp_health: bool = True
    team_check: bool = False
    box_height: float = 5.4
    box_ratio: float = 0.6
    fps: float = 60.0
    fov_enabled: bool = False
    fov: float = 70.0
    walk_speed_enabled: bool = False
    walk_speed: float = 16.0
    jump_power_enabled: bool = False
    jump_power: float = 50.0
    aim_enabled: bool = False
    aim_radius: float = 140.0
    aim_smoothing: float = 6.0
    aim_method: str = "mouse"
    aim_part: str = "torso"
    aim_priority: str = "crosshair"
    aim_sticky: bool = True
    aim_health_check: bool = False
    aim_health_value: float = 50.0
    silent_aim: bool = False
    silent_radius: float = 160.0
    silent_show_fov: bool = True
    noclip: bool = False
    infinite_jump: bool = False
    fly: bool = False
    fly_speed: float = 50.0

    @classmethod
    def from_event(cls, event):
        if not isinstance(event, dict) or set(event) != {field.name for field in fields(cls)}:
            raise ValueError("settings must contain exactly the supported fields")
        defaults = cls()
        for name, value in event.items():
            if name in CHOICES:
                if type(value) is not str or value not in CHOICES[name]:
                    raise ValueError(f"{name} must be one of {', '.join(CHOICES[name])}")
            elif isinstance(getattr(defaults, name), bool):
                if type(value) is not bool:
                    raise ValueError(f"{name} must be boolean")
            elif (type(value) not in (int, float) or not math.isfinite(value)
                  or not RANGES[name][0] <= value <= RANGES[name][1]):
                raise ValueError(f"{name} outside supported range")
        return cls(**event)

    def event(self):
        return asdict(self)

    def overlay_options(self):
        return {"enabled": self.esp_enabled, "boxes": self.boxes, "names": self.names,
                "distances": self.distances, "center_marker": self.center_marker,
                "skeleton": self.esp_skeleton, "tracers": self.esp_tracers,
                "offscreen": self.esp_offscreen, "health": self.esp_health}
