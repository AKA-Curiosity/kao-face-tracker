import os
import sys
import cv2
import random
import pyautogui
import numpy as np
from pynput.mouse import Listener

# Для проверок подключения к интернету и обновлений
try:
    import requests
except ImportError:
    print("Библиотека 'requests' не установлена. Обновления через интернет будут недоступны!")
    requests = None

# Конфигурация обновлений
GITHUB_VERSION_URL = "https://raw.githubusercontent.com/AKA-Curiosity/kao-face-tracker/refs/heads/main/version.txt"
GITHUB_FILES_BASE_URL = "https://github.com/AKA-Curiosity/kao-face-tracker"

LOCAL_VERSION_FILE = "version.txt"


### Функция распознавания и отображения лиц (логика вынесена из main)
def run_face_detection():
    global prediction, predictions

    # Инициализация моделей
    face_proto = "models/opencv_face_detector.pbtxt"
    face_model = "models/opencv_face_detector_uint8.pb"
    gender_proto = "models/deploy_gender.prototxt"
    gender_model = "models/gender_net.caffemodel"

    try:
        face_net = cv2.dnn.readNet(face_model, face_proto)
        gender_net = cv2.dnn.readNet(gender_model, gender_proto)
    except Exception as e:
        print("Ошибка при загрузке моделей:", e)
        return

    # Выбор камеры
    camera_index = select_camera()
    video = cv2.VideoCapture(camera_index)
    if not video.isOpened():
        print("Не удалось открыть камеру.")
        return

    # Получаем разрешение экрана
    screen_width, screen_height = pyautogui.size()

    window_name = "Face detection"
    cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    prediction = random.choice(predictions)
    # Запускаем слушателя мыши
    listener = setup_listeners()

    while True:
        ret, frame = video.read()
        if not ret:
            print("Не удалось получить кадр с камеры")
            break

        processed_frame, _ = highlightFace(face_net, frame, prediction)
        full_screen_frame = cv2.resize(processed_frame, (screen_width, screen_height))
        cv2.imshow(window_name, full_screen_frame)

        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        elif key == 32:
            prediction = random.choice(predictions)

    video.release()
    cv2.destroyAllWindows()


### Функции, используемые в run_face_detection ###

def highlightFace(face_net, frame, prediction, conf_threshold=0.7):
    output_frame = frame.copy()
    frame_h, frame_w = output_frame.shape[:2]
    blob = cv2.dnn.blobFromImage(output_frame, 1.0, (300, 300), [104, 117, 123], True, False)
    face_net.setInput(blob)
    detections = face_net.forward()

    face_boxes = []
    rect_thickness = max(1, int(round(frame_h / 150)))
    font_scale = frame_h / 800

    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > conf_threshold:
            x1 = int(detections[0, 0, i, 3] * frame_w)
            y1 = int(detections[0, 0, i, 4] * frame_h)
            x2 = int(detections[0, 0, i, 5] * frame_w)
            y2 = int(detections[0, 0, i, 6] * frame_h)
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(frame_w - 1, x2), min(frame_h - 1, y2)
            face_boxes.append([x1, y1, x2, y2])
            cv2.rectangle(output_frame, (x1, y1), (x2, y2), (0, 255, 0), rect_thickness, lineType=cv2.LINE_AA)

            if prediction is not None:
                text_size, baseline = cv2.getTextSize(prediction, cv2.FONT_HERSHEY_COMPLEX, font_scale, 1)
                text_x = int((frame_w - text_size[0]) / 2)
                text_y = frame_h - int(frame_h * 0.05)
                text_x = max(0, min(text_x, frame_w - text_size[0]))
                text_y = max(text_size[1], min(text_y, frame_h - baseline))
                cv2.putText(output_frame, prediction, (text_x, text_y),
                            cv2.FONT_HERSHEY_COMPLEX, font_scale, (255, 255, 255), thickness=1, lineType=cv2.LINE_AA)
    return output_frame, face_boxes


def select_camera():
    for index in [0, 1]:
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            cap.release()
            return index
    raise RuntimeError("Не удалось открыть ни одну камеру.")


def on_click(x, y, button, pressed):
    global prediction
    if pressed:
        prediction = random.choice(predictions)


def setup_listeners():
    listener = Listener(on_click=on_click)
    listener.start()
    return listener


### Функции проверки окружения ###

def check_dependencies():
    """
    Проверяет наличие необходимых библиотек и выводит их версии.
    """
    print("Проверка зависимостей:")
    try:
        print("OpenCV:", cv2.__version__)
    except Exception as e:
        print("Ошибка с OpenCV:", e)
    try:
        import numpy
        print("NumPy:", numpy.__version__)
    except Exception as e:
        print("Ошибка с NumPy:", e)
    try:
        print("PyAutoGUI:", pyautogui.__version__)
    except Exception as e:
        print("Ошибка с PyAutoGUI:", e)
    try:
        import pynput
        print("pynput: OK")
    except Exception as e:
        print("Ошибка с pynput:", e)


def is_internet_available(url="http://www.google.com", timeout=5):
    """
    Простая проверка доступности интернета.
    """
    if requests is None:
        return False
    try:
        _ = requests.get(url, timeout=timeout)
        return True
    except Exception:
        return False


def read_local_version():
    """
    Читает локальную версию из файла version.txt.
    """
    if not os.path.exists(LOCAL_VERSION_FILE):
        print("Локальный файл версии не найден.")
        return None
    try:
        with open(LOCAL_VERSION_FILE, "r", encoding="utf-8") as f:
            version = f.read().strip()
            print("Локальная версия:", version)
            return version
    except Exception as e:
        print("Ошибка чтения файла версии:", e)
        return None


def fetch_remote_version():
    """
    Получает версию с GitHub.
    """
    if requests is None:
        return None
    try:
        response = requests.get(GITHUB_VERSION_URL, timeout=5)
        if response.status_code == 200:
            remote_version = response.text.strip()
            print("Удалённая версия:", remote_version)
            return remote_version
        else:
            print("Ошибка при получении версии с GitHub. Status code:", response.status_code)
            return None
    except Exception as e:
        print("Ошибка при подключении к GitHub:", e)
        return None


def update_files(remote_version):
    """
    Простейший механизм обновления файлов.
    Если обнаружена новая версия, обновляет локальные файлы.
    Здесь подразумевается, что обновляются только файлы из корня и папка models.
    Реальную логику можно расширить.
    """
    print("Начало обновления файлов до версии", remote_version)
    # Пример: список файлов, которые нужно обновить. Расширьте при необходимости.
    files_to_update = [
        "main.py",
        "models/opencv_face_detector.pbtxt",
        "models/opencv_face_detector_uint8.pb",
        "models/deploy_gender.prototxt",
        "models/gender_net.caffemodel",
        LOCAL_VERSION_FILE,
    ]
    for file in files_to_update:
        remote_url = GITHUB_FILES_BASE_URL + file
        try:
            response = requests.get(remote_url, timeout=5)
            if response.status_code == 200:
                os.makedirs(os.path.dirname(file), exist_ok=True)
                with open(file, "wb") as f:
                    f.write(response.content)
                print(f"Файл {file} обновлён.")
            else:
                print(f"Не удалось обновить файл {file}, статус {response.status_code}.")
        except Exception as e:
            print(f"Ошибка при обновлении {file}:", e)
    print("Обновление завершено.")


### Главная функция ###
def main():
    # Шаг 1. Проверка зависимостей
    check_dependencies()

    # Шаг 2. Проверка подключения к интернету
    if is_internet_available():
        print("Интернет-соединение установлено.")
        local_version = read_local_version()
        remote_version = fetch_remote_version()
        if remote_version is not None:
            if local_version != remote_version:
                print("Обнаружена новая версия!")
                update_files(remote_version)
            else:
                print("Локальная версия актуальна.")
    else:
        print("Интернет-соединение отсутствует. Запуск в оффлайн-режиме.")

    # Шаг 3. Запуск основной логики
    # Можно запустить другой функционал или основное приложение
    # В данном случае — запуск распознавания лиц
    global predictions, prediction
    predictions = [
        "Ты найдешь новых друзей!",
        "Ты обретешь внутренний покой!",
        "Ты освоишь новое увлечение!",
        "Ты преодолеешь страхи!",
        "Ты создашь что-то уникальное!",
        "Ты получишь новый опыт!",
        "Ты узнаешь что-то новое о себе!",
        "Ты подаришь кому-то радость!",
        "Ты улучшишь свои навыки!",
        "Ты найдешь свое призвание!",
        "Ты раскроешь свой потенциал!",
        "Ты почувствуешь себя увереннее!",
        "Ты найдешь новые возможности!",
        "Ты разбогатеешь духовно!",
        "Ты станешь центром внимания!",
        "Ты переживешь все испытания!",
        "Ты окажешь помощь нуждающимся!",
        "Ты найдешь ответ на важный вопрос!",
        "Ты обретешь уважение окружающих!",
        "Ты обнаружишь скрытые возможности!",
        "Ты найдешь вдохновение в природе!",
        "Ты станешь экспертом в своей области!",
        "Ты научишься ценить моменты счастья!",
        "Ты обретешь уверенность в себе!",
        "Ты привлечешь успех своим упорством!",
        "Ты станешь образцом для подражания!",
        "Ты будешь радоваться мелочам!",
        "Ты привлечешь удачу своим оптимизмом!",
        "Ты обретешь вдохновение в своих мечтах!",
        "Ты окружишь себя позитивными эмоциями!",
        "Ты найдешь утешение в трудные моменты!",
        "Ты обретешь веру в себя и свои силы!",
        "Ты найдешь свое место в этом мире!",
        "Ты станешь опорой для своих близких!",
        "Ты обретешь мудрость в опыте!",
        "Ты научишься ценить моменты счастья!",
        "Ты обретешь веру в себя и свои силы!",
        "Ты станешь магнитом для хороших событий!",
        "Ты сделаешь свой мир ярче и красочнее!",
        "Ты станешь мастером своей судьбы!",
        "Ты обретешь внутренний покой и гармонию!",
        "Ты привлечешь удачу во все дела!",
        "Ты сделаешь шаг к своей мечте каждый день!",
        "Ты обретешь веру в себя и свои силы!",
        "Ты обретешь внутреннюю гармонию и покой!",
        "Ты сделаешь свои мечты реальностью!",
        "Ты привлечешь в свою жизнь все самое лучшее!",
        "Ты обретешь внутренний покой и гармонию!",
    ]
    prediction = random.choice(predictions)
    run_face_detection()


if __name__ == '__main__':
    main()
