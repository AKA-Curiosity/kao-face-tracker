#!/bin/bash

# Проверка доступа к интернету
check_internet() {
    echo "Проверка доступа к интернету..."
    if ping -c 1 google.com &>/dev/null; then
        echo "Доступ в интернет есть"
    else
        echo "Ошибка: нет доступа к интернету. Проверьте соединение."
        exit 1
    fi
}

check_requirements() {
    echo "Проверка технических требований..."
    command -v python3 &>/dev/null || { echo "Python3 не установлен. Установите Python3 и повторите попытку."; exit 1; }
    command -v pip3 &>/dev/null || { echo "pip не установлен. Установите pip и повторите попытку."; exit 1; }
    command -v git &>/dev/null || { echo "git не установлен. Установите git и повторите попытку."; exit 1; }
    echo "Все необходимые инструменты найдены :)"
}


setup_environment() {
    echo "Настройка виртуального окружения..."
    python3 -m venv venv
    source venv/bin/activate

    echo "Обновление pip..."
    pip install --upgrade pip

    echo "Установка зависимостей..."
    pip install opencv-python numpy pynput pyautogui screeninfo requests
}

# Развертывания проекта
deploy_project() {
    REPO_URL="https://github.com/AKA-Curiosity/kao-face-tracker.git"
    PROJECT_DIR="kao-face-tracker"

    if [ ! -d "$PROJECT_DIR" ]; then
        echo "Клонирование репозитория..."
        git clone $REPO_URL
    else
        echo "Репозиторий уже существует, обновляем..."
        cd $PROJECT_DIR || exit 1
        git pull
        cd ..
    fi
}