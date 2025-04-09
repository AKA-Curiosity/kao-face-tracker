#!/bin/bash

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

check_requirements() {
    echo "Проверка технических требований..."
    command -v python3 &> /dev/null || { echo "Python3 не установлен. Установите Python3 и повторите попытку."; exit 1; }
    command -v pip3 &> /dev/null || { echo "pip не установлен. Установите pip и повторите попытку."; exit 1; }
    command -v git &> /dev/null || { echo "git не установлен. Установите git и повторите попытку."; exit 1; }
    echo "Все необходимые инструменты найдены"
}

setup_environment() {
    echo "Настройка виртуального окружения..."
    python3 -m venv venv
    # (для Windows через Git Bash)
    source venv/bin/activate

    echo "Обновление pip..."
    pip install --upgrade pip

    echo "Установка зависимостей..."
    pip install opencv-python numpy pynput pyautogui screeninfo requests
}

# Развертывания проекта
deploy_project() {
    echo "Развёртывание проекта в текущую папку..."

    DEST_DIR="$(pwd)/kao-face-tracker"

    if [ -d "$DEST_DIR" ]; then
        echo "Проект уже развернут в $DEST_DIR"
    else
        echo "Создание директории $DEST_DIR..."
        mkdir -p "$DEST_DIR"

        echo "Копирование файлов проекта (кроме ненужных)..."
        rsync -av --exclude='.git' --exclude='setup.sh' --exclude='.gitignore' --exclude='LICENSE' ./ "$DEST_DIR"

        echo "Проект успешно развернут в $DEST_DIR"
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
s
    read -p "Нажмите Enter, чтобы выйти..."
}

main
