#!/usr/bin/env bash

set -e

PYTHON_VERSION=3.9

install_debian() {
    sudo apt update
    sudo apt install -y python${PYTHON_VERSION} python${PYTHON_VERSION}-venv python3-pip
}

install_arch() {
    sudo pacman -Sy --noconfirm python39 python-pip
}

install_fedora() {
    sudo dnf install -y python${PYTHON_VERSION} python${PYTHON_VERSION}-pip
}

install_opensuse() {
    sudo zypper install -y python39 python39-pip
}

detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        case "$ID" in
            ubuntu|debian|linuxmint|pop)
                install_debian
                ;;
            arch|endeavouros|manjaro)
                install_arch
                ;;
            fedora)
                install_fedora
                ;;
            opensuse*|suse|sles)
                install_opensuse
                ;;
            *)
                echo "Unsupported distro: $ID"
                exit 1
                ;;
        esac
    else
        echo "Cannot detect distro"
        exit 1
    fi
}

setup_venv() {
    if command -v python${PYTHON_VERSION} >/dev/null 2>&1; then
        python${PYTHON_VERSION} -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
    else
        echo "Python ${PYTHON_VERSION} not found"
        exit 1
    fi
}

detect_distro
setup_venv

echo "Done."