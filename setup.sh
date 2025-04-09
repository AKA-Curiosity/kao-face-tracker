#!/bin/bash

# Функция проверки доступа к интернету
check_internet() {
    echo "Проверка доступа к интернету..."
    # Для Windows используем флаг -n
    if ping -n 1 google.com &> /dev/null; then
        echo "Доступ к интернету есть :)"
    else
        echo "Ошибка: нет доступа к интернету. Проверьте соединение."
        exit 1
    fi
}

# Функция проверки технических требований
check_requirements() {
    echo "Проверка технических требований..."
    command -v python3 &> /dev/null || { echo "Python3 не установлен. Установите Python3 и повторите попытку."; exit 1; }
    command -v pip3 &> /dev/null || { echo "pip не установлен. Установите pip и повторите попытку."; exit 1; }
    command -v git &> /dev/null || { echo "git не установлен. Установите git и повторите попытку."; exit 1; }
    echo "Все необходимые инструменты найдены :)"
}

# Функция настройки виртуального окружения и установки зависимостей
setup_environment() {
    echo "Настройка виртуального окружения..."
    python3 -m venv venv
    # Активация виртуального окружения в bash (для Windows через Git Bash)
    source venv/bin/activate

    echo "Обновление pip..."
    pip install --upgrade pip

    echo "Установка зависимостей..."
    pip install opencv-python numpy pynput pyautogui screeninfo requests
}

# Функция развертывания проекта
deploy_project() {
    REPO_URL="https://github.com/AKA-Curiosity/kao-face-tracker.git"
    PROJECT_DIR="kao-face-tracker"

    if [ ! -d "$PROJECT_DIR" ]; then
        echo "Клонирование репозитория..."
        git clone $REPO_URL
    else
        echo "Репозиторий уже существует, обновляем..."
        cd "$PROJECT_DIR" || exit 1
        git pull
        cd ..
    fi
}

# Основной блок
main() {
    check_internet
    check_requirements
    setup_environment
    deploy_project

    echo "======================================"
    echo "✅ Развертывание завершено!"
    echo "Папка проекта 'kao-face-tracker' готова для работы."
    echo "Далее запустите setup.py для дополнительной настройки:"
    echo "   cd kao-face-tracker && python3 setup.py"
    echo "======================================"

    # Задержка, чтобы окно не закрывалось сразу
    read -p "Нажмите Enter, чтобы выйти..."
}

main
