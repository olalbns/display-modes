from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

from .i18n import _


class Mode(str, Enum):
    MIRROR = "mirror"
    EXTEND_RIGHT = "right"
    EXTEND_LEFT = "left"
    EXTEND_ABOVE = "above"
    EXTEND_BELOW = "below"
    INTERNAL_ONLY = "internal"
    EXTERNAL_ONLY = "external"


@dataclass(frozen=True)
class Output:
    name: str
    internal: bool
    primary: bool = False
    width: int = 1920
    height: int = 1080
    enabled: bool = True


class DisplayError(RuntimeError):
    pass


class Backend(ABC):
    name: str

    @abstractmethod
    def outputs(self) -> list[Output]: ...

    @abstractmethod
    def apply(self, mode: Mode) -> str: ...


def run(*args: str) -> str:
    try:
        result = subprocess.run(args, text=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, check=True)
        return result.stdout
    except FileNotFoundError:
        raise DisplayError(_("The command “{}” is not installed.").format(args[0]))
    except subprocess.CalledProcessError as exc:
        details = exc.stderr.strip() or exc.stdout.strip() or _("unknown error")
        raise DisplayError(details)


def internal_name(name: str) -> bool:
    """Best-effort identification, used only to choose sensible defaults."""
    name = name.upper()
    return name.startswith(("EDP", "LVDS", "DSI"))


class HyprlandBackend(Backend):
    name = "Hyprland (Wayland)"

    def outputs(self) -> list[Output]:
        # Sans « all », Hyprland peut omettre une sortie connectée mais
        # désactivée. Cela faisait croire à l’interface qu’un seul écran
        # existait, alors que la sortie pouvait être réactivée par une action.
        raw = run("hyprctl", "monitors", "all", "-j")
        monitors = json.loads(raw)
        return [Output(m["name"], internal_name(m["name"]), m.get("focused", False),
                       int(m.get("width", 1920)), int(m.get("height", 1080)),
                       not m.get("disabled", False))
                for m in monitors]

    @staticmethod
    def _set(spec: str) -> None:
        run("hyprctl", "keyword", "monitor", spec)

    def apply(self, mode: Mode) -> str:
        outputs = self.outputs()
        if len(outputs) < 2:
            raise DisplayError(_("At least two connected displays are required."))
        primary = next((o for o in outputs if o.internal), outputs[0])
        others = [o for o in outputs if o.name != primary.name]

        if mode == Mode.INTERNAL_ONLY:
            for output in others: self._set(f"{output.name},disable")
        elif mode == Mode.EXTERNAL_ONLY:
            for output in outputs:
                if output.internal: self._set(f"{output.name},disable")
            for output in others: self._set(f"{output.name},preferred,auto,1")
        elif mode == Mode.MIRROR:
            self._set(f"{primary.name},preferred,0x0,1")
            for output in others:
                self._set(f"{output.name},preferred,auto,1,mirror,{primary.name}")
        else:
            # Make each output independent and place external screens relative to primary.
            self._set(f"{primary.name},preferred,0x0,1")
            cursor_x, cursor_y = 0, 0
            for index, output in enumerate(others):
                if mode == Mode.EXTEND_RIGHT:
                    pos = f"{primary.width + cursor_x}x0"; cursor_x += output.width
                elif mode == Mode.EXTEND_LEFT:
                    cursor_x -= output.width; pos = f"{cursor_x}x0"
                elif mode == Mode.EXTEND_ABOVE:
                    cursor_y -= output.height; pos = f"0x{cursor_y}"
                else:
                    pos = f"0x{primary.height + cursor_y}"; cursor_y += output.height
                self._set(f"{output.name},preferred,{pos},1")
        return _("Configuration applied with Hyprland.")


class XrandrBackend(Backend):
    name = "X11 (xrandr)"
    _connected = re.compile(r"^(\S+) connected(?: primary)?(?: (\d+)x(\d+)\+[-\d]+\+[-\d]+)?")

    def outputs(self) -> list[Output]:
        result: list[Output] = []
        for line in run("xrandr", "--query").splitlines():
            match = self._connected.match(line)
            if match:
                name, width, height = match.groups()
                result.append(Output(name, internal_name(name), " connected primary" in line,
                                     int(width or 1920), int(height or 1080), width is not None))
        return result

    def apply(self, mode: Mode) -> str:
        outputs = self.outputs()
        if len(outputs) < 2:
            raise DisplayError(_("At least two connected displays are required."))
        primary = next((o for o in outputs if o.internal), next((o for o in outputs if o.primary), outputs[0]))
        others = [o for o in outputs if o.name != primary.name]
        if mode == Mode.INTERNAL_ONLY:
            for o in others: run("xrandr", "--output", o.name, "--off")
        elif mode == Mode.EXTERNAL_ONLY:
            run("xrandr", "--output", primary.name, "--off")
            for o in others: run("xrandr", "--output", o.name, "--auto")
        elif mode == Mode.MIRROR:
            run("xrandr", "--output", primary.name, "--auto")
            for o in others: run("xrandr", "--output", o.name, "--auto", "--same-as", primary.name)
        else:
            relation = {Mode.EXTEND_RIGHT: "--right-of", Mode.EXTEND_LEFT: "--left-of",
                        Mode.EXTEND_ABOVE: "--above", Mode.EXTEND_BELOW: "--below"}[mode]
            run("xrandr", "--output", primary.name, "--auto")
            anchor = primary.name
            for o in others:
                run("xrandr", "--output", o.name, "--auto", relation, anchor)
                anchor = o.name
        return _("Configuration applied with xrandr.")


class UnsupportedWaylandBackend(Backend):
    name = "Unsupported Wayland"
    def outputs(self) -> list[Output]: return []
    def apply(self, mode: Mode) -> str:
        raise DisplayError(_("This Wayland compositor does not provide a universal display-management API. This first version supports Hyprland natively."))


def detect_backend() -> Backend:
    if os.environ.get("HYPRLAND_INSTANCE_SIGNATURE") and shutil.which("hyprctl"):
        return HyprlandBackend()
    if os.environ.get("DISPLAY") and shutil.which("xrandr"):
        return XrandrBackend()
    return UnsupportedWaylandBackend()
