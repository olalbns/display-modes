# Modes d’affichage

Petite application GTK4 pour basculer rapidement entre **dupliquer**, **étendre** (droite, gauche, haut, bas), **écran interne uniquement** et **écran externe uniquement**.

## Backends inclus

| Session | État | Mécanisme |
|---|---|---|
| Hyprland / Wayland | pris en charge | `hyprctl monitors -j`, `hyprctl keyword monitor` |
| Toute session X11 | pris en charge | `xrandr` |
| GNOME/KDE/Autres Wayland | message explicite | pas d’API standard inter-compositeurs |

Wayland ne fournit volontairement pas une API universelle permettant à une application de modifier la topologie des sorties. Une app réellement portable doit donc comporter un backend par compositeur. L’interface est portable ; cette version est immédiatement utilisable sous Hyprland et X11.

## Dépendances d’exécution

- Python 3.10+
- GTK 4 et PyGObject (`python-gobject` ou équivalent)
- **Hyprland :** `hyprctl` (fourni par Hyprland)
- **X11 :** `xrandr` (paquet `xorg-xrandr` sur Arch)

### Arch Linux
```bash
sudo pacman -S python python-gobject gtk4 xorg-xrandr
cd display-modes
python -m pip install --user .
```

### Fedora
```bash
sudo dnf install python3-gobject gtk4 xrandr
python3 -m pip install --user .
```

### Debian / Ubuntu
```bash
sudo apt install python3-gi gir1.2-gtk-4.0 x11-xserver-utils
python3 -m pip install --user .
```

Lancez `display-modes`, ou utilisez **Modes d’affichage** dans le menu d’applications.

## Notes de sécurité et comportement

- L’app ne requiert pas `sudo` et ne modifie que la session graphique courante.
- Avec *Dupliquer*, les écrans doivent avoir un mode de résolution/fréquence compatible. Sinon, l’outil affiche l’erreur retournée par le système.
- Pour Hyprland, les réglages appliqués sont dynamiques. Ajoutez vos règles `monitor = …` à `hyprland.conf` si vous souhaitez les rendre permanents après redémarrage.


## Langue de l’interface

L’interface suit automatiquement la langue de la session définie par
`LC_MESSAGES` puis `LANG`. Les traductions livrées sont le français et
l’anglais (langue de repli). Par exemple :

```bash
LANG=fr_FR.UTF-8 display-modes # français
LANG=en_US.UTF-8 display-modes # anglais
```

Les catalogues gettext sont dans `po/`. Pour ajouter une langue, créez un
fichier `po/<code-langue>.po`, compilez-le avec `msgfmt`, puis installez le
fichier produit dans `usr/share/locale/<code-langue>/LC_MESSAGES/display-modes.mo`.
