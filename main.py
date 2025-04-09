import cv2
import random
import pyautogui
import numpy as np
from pynput.mouse import Listener


# Функция определения лиц
def highlightFace(face_net, gender_net, frame, prediction, conf_threshold=0.7):
    frame_opencv_dnn = frame.copy()
    frame_height = frame_opencv_dnn.shape[0]
    frame_width = frame_opencv_dnn.shape[1]
    blob = cv2.dnn.blobFromImage(frame_opencv_dnn, 1.0, (300, 300), [104, 117, 123], True, False)
    face_net.setInput(blob)
    detections = face_net.forward()
    face_boxes = []
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > conf_threshold:
            x1 = int(detections[0, 0, i, 3] * frame_width)
            y1 = int(detections[0, 0, i, 4] * frame_height)
            x2 = int(detections[0, 0, i, 5] * frame_width)
            y2 = int(detections[0, 0, i, 6] * frame_height)

            # Проверка, чтобы координаты лица не выходили за границы изображения
            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(frame_width - 1, x2)
            y2 = min(frame_height - 1, y2)

            face_boxes.append([x1, y1, x2, y2])
            cv2.rectangle(frame_opencv_dnn, (x1, y1), (x2, y2), (0, 255, 0), int(round(frame_height / 150)), 6)

            # Вывод предсказания
            text_size = cv2.getTextSize(prediction, cv2.FONT_HERSHEY_COMPLEX, 0.5, 1)[0]
            text_x = int((frame_width - text_size[0]) / 2.5)
            text_y = int((frame_height + text_size[1]) / 1.1)
            text_x = max(0, min(text_x, frame_width - text_size[0]))
            text_y = max(0, min(text_y, frame_height - text_size[1]))

            cv2.putText(frame_opencv_dnn, prediction, (text_x, text_y), cv2.FONT_HERSHEY_COMPLEX, 0.6, (255, 255, 255),
                        1, cv2.LINE_AA)

    return frame_opencv_dnn, face_boxes

# Функция предсказания пола

def select_camera():
    internal_camera_index = 0
    external_camera_index = 1

    # Проверяем наличие встроенной камеры
    internal_camera = cv2.VideoCapture(internal_camera_index)
    if internal_camera.isOpened():
        internal_camera.release()
        return internal_camera_index
    else:
        print("Встроенная камера не найдена, переключение на внешнюю камеру.")
        return external_camera_index


# Загрузка моделей
face_proto = "opencv_face_detector.pbtxt"
face_model = "opencv_face_detector_uint8.pb"
gender_proto = "deploy_gender.prototxt"
gender_model = "gender_net.caffemodel"

face_net = cv2.dnn.readNet(face_model, face_proto)
gender_net = cv2.dnn.readNet(gender_model, gender_proto)

# Выбор камеры
camera_index = select_camera()
video = cv2.VideoCapture(camera_index)

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

# Авто определения ширина/высота монитора
screen_width, screen_height = pyautogui.size()


# Функция обработки нажатия левой кнопки мыши
def on_left_click(x, y, button, pressed):
    global prediction
    if pressed:
        prediction = random.choice(predictions)


# Функции обработки нажатия кнопок мыши
def on_left_click(x, y, button, pressed):
    global prediction
    if pressed:
        prediction = random.choice(predictions)

def on_right_click(x, y, button, pressed):
    if pressed:
        global prediction
        if pressed:
            prediction = random.choice(predictions)

# Слушатели событий мыши
left_listener = Listener(on_click=on_left_click)
right_listener = Listener(on_click=on_right_click)

# Запуск слушателей
left_listener.start()
right_listener.start()

prediction = random.choice(predictions)
while True:
    has_frame, frame = video.read()
    if not has_frame:
        print("Конец видео")
        break
    result_img, face_boxes = highlightFace(face_net, gender_net, frame, prediction)
    if not face_boxes:
        print("Лица не распознаны")
    # Создаем серый фон
    gray_frame = np.full((screen_height, screen_width, 3), 50, dtype=np.uint8)

    # Определяем размеры для вывода изображения
    resize_factor = 1  # Уменьшаем размер изображения на 30%
    output_size = int(min(screen_width, screen_height) * resize_factor)  # Выбираем минимальный размер

    # Определяем координаты для центрирования
    x_offset = (screen_width - output_size) // 2
    y_offset = (screen_height - output_size) // 2

    # Отображаем изображение в центре экрана
    gray_frame[y_offset:y_offset + output_size, x_offset:x_offset + output_size] = cv2.resize(result_img, (
    output_size, output_size))

    cv2.namedWindow("Face detection", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("Face detection", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow("Face detection", gray_frame)
    key = cv2.waitKey(1)
    if key == ord('q'):  # Q - завершаем программу
        break
    if key == 32:  # Пробел - меняем предсказание
        prediction = random.choice(predictions)

cv2.destroyAllWindows()