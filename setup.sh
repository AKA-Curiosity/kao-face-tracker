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
    echo "Развёртывание проекта из репозитория GitHub..."

    REPO_URL="https://github.com/AKA-Curiosity/kao-face-tracker.git"
    DEST_DIR="$(pwd)/kao-face-tracker"

    # Проверяем, если проект уже клонирован
    if [ -d "$DEST_DIR" ]; then
        echo "Проект уже развернут в $DEST_DIR"
    else
        # Клонируем репозиторий
        git clone "$REPO_URL" "$DEST_DIR"
        echo "Проект успешно клонирован в $DEST_DIR"

        # Удаляем ненужные файлы
        echo "Удаляем ненужные файлы..."
        rm -f "$DEST_DIR/setup.sh"
        rm -f "$DEST_DIR/LICENSE"
        rm -f "$DEST_DIR/.gitignore"
        rm -rf "$DEST_DIR/.git"

        echo "Ненужные файлы удалены"
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
