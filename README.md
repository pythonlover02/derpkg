# derpkg
My custom generic package manager wrapper, created because I usually use a bunch of different distros both on virtual machines and real hardware, just trying to make updating/installing packages easier by just remembering some generic commands.

### Prerequisites

- Python 3.8 or higher
- Pip
- Sudo privileges (for installation)

## Installation

- Download the files
- run `./build.sh`
- run `sudo ./install.sh`
- now you can run `derpkg -h` and see what you can do with it.

## Supported Package Managers

- Pacman (Arch Linux and derivatives)
- Apt (Debian, Ubuntu, and derivatives)
- Zypper (openSUSE)
- Flatpak (cross-distribution)
- Yay (AUR helper for Arch Linux)
