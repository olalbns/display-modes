# Publication sur GitHub et dans l’AUR

Le dépôt de code visé est : <https://github.com/olalbns/display-modes>.

## 1. Publier l’application sur GitHub

Depuis la racine de ce projet :

```bash
git init
git branch -M main
git add .
git commit -m 'Initial release of Display Modes'
git remote add origin https://github.com/olalbns/display-modes.git
git push -u origin main
```

## 2. Créer et publier le dépôt AUR

L’AUR héberge seulement les fichiers d’empaquetage, pas le code complet. Il
faut avoir un compte AUR et une clé SSH enregistrée sur aur.archlinux.org.

```bash
# À exécuter depuis la racine du projet display-modes.
project_dir="$PWD"
git clone ssh://aur@aur.archlinux.org/display-modes-git.git /tmp/display-modes-git-aur
cp "$project_dir/aur/display-modes-git/PKGBUILD" /tmp/display-modes-git-aur/
cd /tmp/display-modes-git-aur
makepkg --printsrcinfo > .SRCINFO
git add PKGBUILD .SRCINFO
git commit -m 'Initial AUR package'
git push
```

> **Avant le premier envoi :** remplacez `YOUR_EMAIL@example.com` dans le
> champ Maintainer du `PKGBUILD` par votre e-mail de mainteneur, si vous
> souhaitez l’afficher publiquement. La valeur n’est pas utilisée à
> l’installation.

## 3. Installation par yay

Après l’indexation de l’AUR (quelques minutes) :

```bash
yay -S display-modes-git
```

`yay` installera automatiquement les dépendances obligatoires : `python`,
`python-gobject` et `gtk4`. Pour la gestion des écrans selon la session,
installez aussi l’option adaptée :

```bash
# Hyprland
yay -S hyprland
# Session X11
yay -S xorg-xrandr
```

Ces deux paquets sont volontairement des dépendances optionnelles : installer
Hyprland dans une session X11, ou un serveur X11 dans une installation Wayland,
n’est ni nécessaire ni souhaitable.
