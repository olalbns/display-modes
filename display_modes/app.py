from __future__ import annotations
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib
from .backends import DisplayError, Mode, detect_backend

APP_ID = "io.github.displaymodes"

class Window(Gtk.ApplicationWindow):
    def __init__(self, app: Gtk.Application):
        super().__init__(application=app, title="Modes d’affichage")
        self.set_default_size(480, 360)
        self.set_resizable(False)
        self.backend = detect_backend()
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14,
                       margin_top=22, margin_bottom=22, margin_start=22, margin_end=22)
        self.set_child(root)
        title = Gtk.Label(label="Modes d’affichage", xalign=0)
        title.add_css_class("title-2"); root.append(title)
        self.subtitle = Gtk.Label(label=f"Backend : {self.backend.name}", xalign=0, wrap=True)
        self.subtitle.add_css_class("dim-label"); root.append(self.subtitle)
        grid = Gtk.Grid(column_spacing=10, row_spacing=10, column_homogeneous=True, row_homogeneous=True)
        root.append(grid)
        entries = [("⧉  Dupliquer", Mode.MIRROR), ("→  Étendre à droite", Mode.EXTEND_RIGHT),
                   ("←  Étendre à gauche", Mode.EXTEND_LEFT), ("↑  Étendre en haut", Mode.EXTEND_ABOVE),
                   ("↓  Étendre en bas", Mode.EXTEND_BELOW), ("▣  Écran interne uniquement", Mode.INTERNAL_ONLY),
                   ("▤  Écran externe uniquement", Mode.EXTERNAL_ONLY)]
        for i, (label, mode) in enumerate(entries):
            button = Gtk.Button(label=label)
            button.set_hexpand(True); button.set_vexpand(True)
            button.connect("clicked", self.on_mode, mode)
            grid.attach(button, i % 2, i // 2, 1, 1)
        self.status = Gtk.Label(label="Prêt.", xalign=0, wrap=True, margin_top=6)
        root.append(self.status)

    def on_mode(self, _button: Gtk.Button, mode: Mode) -> None:
        self.status.set_text("Application de la configuration…")
        while GLib.MainContext.default().iteration(False): pass
        try:
            self.status.set_text(self.backend.apply(mode))
        except DisplayError as error:
            self.status.set_text(f"Erreur : {error}")

class App(Gtk.Application):
    def __init__(self): super().__init__(application_id=APP_ID)
    def do_activate(self):
        window = self.props.active_window or Window(self)
        window.present()

def main() -> None:
    App().run(None)

if __name__ == "__main__":
    main()
