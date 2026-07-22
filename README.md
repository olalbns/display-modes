# Modes d’affichage

Petite application GTK4 pour basculer rapidement entre les modes d’affichage
sous Hyprland et les sessions X11.

## Fonctions

- Dupliquer les écrans ;
- étendre l’affichage à droite, à gauche, en haut ou en bas ;
- utiliser uniquement l’écran interne ou l’écran externe ;
- détection automatique du backend Hyprland ou X11 ;
- interface en français ou en anglais selon la langue de la session.

## Installation sur Arch Linux

```bash
yay -S display-modes-git
```

Pour Hyprland, `hyprctl` est fourni avec Hyprland. Pour les sessions X11,
installez aussi :

```bash
sudo pacman -S xorg-xrandr
```

## Utilisation

Lancez l’application depuis le menu, ou avec :

```bash
display-modes
```

Choisissez ensuite le mode souhaité. Les changements sont appliqués à la
session graphique en cours et ne demandent pas de mot de passe.

> Sous Hyprland, les changements sont dynamiques. Ajoutez vos règles `monitor`
> à `hyprland.conf` si vous souhaitez les conserver après un redémarrage.
