from __future__ import annotations
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib
from .backends import DisplayError, Mode, detect_backend
from .i18n import _, setup_i18n

APP_ID = "io.github.displaymodes"

class Window(Gtk.ApplicationWindow):
    def __init__(self, app: Gtk.Application):
        super().__init__(application=app, title=_("Display Modes"))
        self.set_default_size(480, 360)
        self.set_resizable(False)
        self.backend = detect_backend()
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14,
                       margin_top=22, margin_bottom=22, margin_start=22, margin_end=22)
        self.set_child(root)
        title = Gtk.Label(label=_("Display Modes"), xalign=0)
        title.add_css_class("title-2"); root.append(title)
        self.subtitle = Gtk.Label(label=_("Backend: {}").format(_(self.backend.name)), xalign=0, wrap=True)
        self.subtitle.add_css_class("dim-label"); root.append(self.subtitle)
        grid = Gtk.Grid(column_spacing=10, row_spacing=10, column_homogeneous=True, row_homogeneous=True)
        root.append(grid)
        entries = [(_("⧉  Mirror"), Mode.MIRROR), (_("→  Extend right"), Mode.EXTEND_RIGHT),
                   (_("←  Extend left"), Mode.EXTEND_LEFT), (_("↑  Extend above"), Mode.EXTEND_ABOVE),
                   (_("↓  Extend below"), Mode.EXTEND_BELOW), (_("▣  Internal display only"), Mode.INTERNAL_ONLY),
                   (_("▤  External display only"), Mode.EXTERNAL_ONLY)]
        for i, (label, mode) in enumerate(entries):
            button = Gtk.Button(label=label)
            button.set_hexpand(True); button.set_vexpand(True)
            button.connect("clicked", self.on_mode, mode)
            grid.attach(button, i % 2, i // 2, 1, 1)
        self.status = Gtk.Label(label=_("Ready."), xalign=0, wrap=True, margin_top=6)
        root.append(self.status)

    def on_mode(self, _button: Gtk.Button, mode: Mode) -> None:
        self.status.set_text(_("Applying configuration…"))
        while GLib.MainContext.default().iteration(False): pass
        try:
            self.status.set_text(self.backend.apply(mode))
        except DisplayError as error:
            self.status.set_text(_("Error: {}").format(error))

class App(Gtk.Application):
    def __init__(self): super().__init__(application_id=APP_ID)
    def do_activate(self):
        window = self.props.active_window or Window(self)
        window.present()

def main() -> None:
    setup_i18n()
    App().run(None)

if __name__ == "__main__":
    main()
