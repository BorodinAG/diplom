import cv2
import numpy as np
import streamlit as st
import os
import tempfile
import threading
from streamlit.runtime.scriptrunner import add_script_run_ctx
from ultralytics import YOLO
import json
import datetime
import pandas as pd

# model = YOLO('main_diplom/files/model/yolo11_sym_plate.pt')
model = YOLO('main_diplom/files/model/yolo11_sym_plate_new.pt')

# model_car = YOLO('main_diplom/files/model/yolo11cars.pt')
model_car = YOLO('main_diplom/files/model/yolo11cars_new.pt')


# Функция отрисовки зоны интереса
def zone_intersest_plot(results, x, y, yz, xz, colors):
    
    frame_res = results[0].orig_img.copy()
    for box in results[0].boxes:
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(np.int32)
        conf = round(box.conf[0].item(), 2)
        cls = int(box.cls[0].item())
        cv2.rectangle(frame_res, (x1, y1), (x2, y2), colors, 2)
        cv2.putText(frame_res, f'{cls} {conf}', (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    # Создаем копию кадра перед рисованием    
    frame_res = frame_res.copy()
                    
    try:
        # Рисуем зоны интереса
        # Рисуем верхнюю границу зоны интереса
        cv2.line(frame_res, (0, y), (frame_res.shape[1], y), (255, 0, 0), 2)
        # Рисуем нижнюю границу зоны интереса
        cv2.line(frame_res, (0, yz), (frame_res.shape[1], yz), (255, 255, 0), 2)
        # Рисуем правую границу зоны интереса
        cv2.line(frame_res, (x, 0), (x, frame_res.shape[0]), (0, 0, 255), 2)
        # Рисуем левую границу зоны интереса
        cv2.line(frame_res, (xz, 0), (xz, frame_res.shape[0]), (0, 255, 255), 2)
    except:
        pass
    
    # Конвертируем BGR в RGB для streamlit
    frame_res = cv2.cvtColor(frame_res, cv2.COLOR_BGR2RGB) 
    return frame_res

# Функция для обработки изображения
def image_processing(image):
    results = model(image)[0]
    cropped_image = None

    # Получаем список результатов
    for box in results.boxes:
        if box.cls[0].item() == 22:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(np.int32)
            cropped_image = image[y1:y2, x1:x2]
            break    
    
    if cropped_image is None:
        return image
   
    # # Генерируем уникальное имя файла на основе текущего времени
    # timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    # filename = f'users/detected_plates/plate_{timestamp}.jpg'
    
    # # Сохраняем изображение
    # cv2.imwrite(filename, cropped_image)
    
    return cropped_image

# Функция для обработки номера
def number_processing(image):
    
    results = model(image)[0]
    auto_number = ''

    try:
        # Получаем минимальный y2 и максимальный y1
        min_y2 = min(box.xyxy[0][3].item() for box in results.boxes if box.cls[0].item() <= 21)
        max_y1 = max(box.xyxy[0][1].item() for box in results.boxes if box.cls[0].item() <= 21)
 
        # Если min_y2 < max_y1, сортируем все символы по x слева направо
        if min_y2 > max_y1:
            sorted_boxes = sorted(results.boxes, key=lambda box: box.xyxy[0][0].item())
            get_val = lambda box: str(int(box.cls[0].item())) if box.cls[0].item() < 10 else results.names[int(box.cls[0])]
            auto_number = ''.join(map(get_val, [box for box in sorted_boxes if box.cls[0].item() <= 21]))            
                
        else:
            # получаем среднее значение y координаты для всех объектов
            try:
                avg_y = sum(box.xyxy[0][1].item() for box in results.boxes if box.cls[0].item() <= 21)/len(
                    [box for box in results.boxes if box.cls[0].item() <= 21])
            except:
                avg_y = 0
        
            upper = []
            lower = []
            
            for box in results.boxes:
                if box.cls[0].item() <= 21:
                    y = box.xyxy[0][1].item()
                    data = (
                        box.xyxy[0][0].item(),
                        y,
                        box.xyxy[0][2].item(),
                        box.xyxy[0][3].item(),
                        box.cls[0].item(),
                        results.names[int(box.cls[0])]
                    )
                    (upper if y < avg_y else lower).append(data)
            
            upper.sort(key=lambda x: x[0])
            lower.sort(key=lambda x: x[0])

            # Функция для получения значения символа:
            # Если класс < 10 (цифра), возвращаем строковое представление класса
            # Иначе возвращаем букву из имени класса
            get_val = lambda x: str(int(x[4])) if x[4] < 10 else x[5]    
            auto_number = ''.join(map(get_val, upper)) + ''.join(map(get_val, lower))   

        # Сохраняем номер в txt файл
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%Hh-%Mm")
        data = datetime.datetime.now().strftime("%Y-%m-%d")
        os.makedirs(fr'users/detected_numbers/{data}', exist_ok=True)                        
        save_path = fr"users/detected_numbers/{data}/number_auto_{data}.txt"
        with open(save_path, 'a') as f:
            f.write(f"Auto number: {auto_number}, Data: {timestamp}, Coordinates: {min_y2} {max_y1}\n")    
    
    except:
        pass
    
    return auto_number

# Функция для пропуска или отказа
def comparison_number(auto_number):
    try:
        # db = pd.read_excel('users/admin/data/the_base_of_admission.xlsx')['Номер авто']
        db = pd.read_csv('users/admin/data/the_base_of_admission.csv')['Номер авто']
    except:
        db = []
    
    bool = False
    # Проверяем совпадение номеров
    # Если совпадает, то возвращаем True
    for auto_number_db in db:
        auto_number_db = str(auto_number_db).replace(r'[^\w\s]', '').strip()
        
        if auto_number == auto_number_db:
            bool = True
            break
    return bool

def miss_stop(frame_res,colors, bool):
    
    height, width = frame_res.shape[:2]
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = min(width, height) * 0.003
    thickness = 10
                        
    text = "MISS" if bool else "STOP"
    color = colors['green'] if bool else colors['red']
                        
    # Получаем размер текста и позицию
    (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, thickness)
    text_x = (width - text_width) // 2
    text_y = (height + text_height) // 2
                        
    # Рисуем текст
    cv2.putText(frame_res, text, (text_x, text_y), font, font_scale, color, thickness)
    
    return frame_res

def save_cropped_image(cropped_image, auto_number):
    # Сохраняем изображение
    # timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    timestamp = datetime.datetime.now().strftime("%Hh-%Mm")
    data = datetime.datetime.now().strftime("%Y-%m-%d")
    user = st.session_state.username
    os.makedirs(fr'users/detected_cars/{data}', exist_ok=True)                        
    save_path = fr"users/detected_cars/{data}/{user}_{timestamp}_{auto_number}.jpg"
    cv2.imwrite(save_path, cropped_image)

def play_video(filename, position, len_video, model, intersections):
    colors = {
        'white': (255, 255, 255),
        'green': (0, 255, 0),
        'red': (255, 0, 0)
    }
    
    try:
        if st.session_state.stop_processing:
            return
            
        cap = cv2.VideoCapture(filename)
        if not cap.isOpened():
            st.error(f"Не удалось открыть видео: {filename}")
            return

        # Создаем пустые плейсхолдеры для видео
        if 'video_placeholders' not in st.session_state:
            st.session_state.video_placeholders = []
            cols = st.columns(3)
            for i in range(len_video):
                if i<3:
                    st.session_state.video_placeholders.append(cols[i].empty())
                else:
                    st.session_state.video_placeholders.append(cols[i-3].empty())
        
        while cap.isOpened() and not st.session_state.stop_processing:
            ret, frame = cap.read()
            if not ret:
                break
            
            results = model_car(frame)
            # Координаты зоны интереса
            x, y, yz, xz = intersections[position]
            
            # Получаем кадр с результатами и зоной интереса
            frame_res = zone_intersest_plot(results, x, y, yz, xz, colors['white'])
            
            # Обновляем соответствующий плейсхолдер
            st.session_state.video_placeholders[position].image(frame_res)
            
            # Получаем координаты распознанных объектов
            bounding_box = results[0].boxes.xyxy.cpu().numpy().astype(np.int32)  # координаты объектов
            class_id = results[0].boxes.cls.cpu().numpy().astype(np.int32)  # классы объектов            
            
            for i, class_id_i in enumerate(class_id):
                # if class_id_i in [22, 24, 26]:  # если это машина, скорая или пожарная
                if class_id_i in [0, 1]:  # если это машина или экстренная служба              
                    x1, y1, x2, y2 = bounding_box[i]  # координаты объекта
                    if y < y2 < yz and x2 <= x and x1 >= xz:  # проверка на вхождение в зону интереса
                        
                        cropped_image = frame[y1:y2, x1:x2].copy()  # вырезаем кадр

                        plate = image_processing(cropped_image)
                        
                        auto_number = number_processing(plate)
                        
                        # if class_id_i == 22:
                        if class_id_i == 0:
                            bool = comparison_number(auto_number)
                        else:
                            bool = True
                            auto_number = ''
                        
                        frame_res = miss_stop(frame_res, colors, bool)

                        st.session_state.video_placeholders[position].image(frame_res)      
                        
                        save_cropped_image(cropped_image, auto_number)                  
                        
    except Exception as e:                  
        st.error(f"Ошибка при воспроизведении видео: {str(e)}")
    finally:
        if 'cap' in locals():
            cap.release()


def play_multiple_videos(video_files, intersections):
    
    # Удаляем плейсхолдеры, если они уже есть
    if 'video_placeholders' in st.session_state:
        del st.session_state.video_placeholders
    
    # Определяем количество видео
    len_video = len(video_files)    
    
    if len(video_files) > 6:
        st.warning("Можно загрузить максимум 6 видео одновременно")
        video_files = video_files[:6]

    threads = []
    for i, video in enumerate(video_files):
        thread = threading.Thread(target=play_video, args=(video, i, len_video, model, intersections))        
        add_script_run_ctx(thread)
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()

def main():
    st.header(":violet[_Обработка видео_]", divider='rainbow')
    
    if 'stop_processing' not in st.session_state:
        st.session_state.stop_processing = False
    
    try:
        st.sidebar.header(":violet[Загрузите видео файлы]", divider='rainbow')

        uploaded_files = st.sidebar.file_uploader("Выберите видео файлы", type=['mp4', 'avi', 'mov'], accept_multiple_files=True)
        
        # Создаём временные файлы для каждого загруженного видео
        if uploaded_files:
            temp_files = []
            try:
                for file in uploaded_files:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                        tmp_file.write(file.read())
                        temp_files.append(tmp_file.name)
                
                # Получаем список имен загруженных файлов
                file_names = [os.path.splitext(file.name)[0] for file in uploaded_files]                
                
                intersections = []
                for file in file_names:
                    try:
                        with open(f'users/coordinates/{file}.json', 'r') as json_file:
                            data = json.load(json_file)
                            intersections.append(data.get('intersection'))
                    except:
                        intersections.append([0,0])
                        st.write(f'Зона интереса неопределена для: {file}')               

                # st.write(intersections)
                col1, col2 = st.sidebar.columns(2)
                
                if col1.button("Обработать видео"):
                    st.session_state.stop_processing = False
                    play_multiple_videos(temp_files, intersections)
                
                if col2.button("Остановить обработку"):
                    st.session_state.stop_processing = True
                    if 'video_placeholders' in st.session_state:
                        del st.session_state.video_placeholders
                
            finally:
                # Чистим временные файлы
                for temp_file in temp_files:
                    try:
                        os.unlink(temp_file)
                    except Exception:
                        pass
                        
    except Exception as e:
        st.error(f"Произошла ошибка: {str(e)}")

if __name__ == '__main__':
    main()

# def main():
#     """
#     Главная функция приложения для обработки видео.
    
#     Функционал:
#     1. Загрузка видео файлов различных форматов (MP4, AVI, MOV)
#     2. Автоматическое определение зон интереса на видео
#     3. Визуализация определяемых объектов и зон интереса
#     4. Визуальный показ разрешения на проезд
#     3. Параллельная обработка нескольких видео потоков
#     4. Интуитивно понятный пользовательский интерфейс
    
#     Особенности:
#     - Поддержка множественной загрузки файлов
#     - Автоматическое создание временных файлов для безопасной обработки
#     - Система координат для определения зон интереса
#     - Возможность остановки обработки в любой момент
#     - Автоматическая очистка временных файлов
#     """
#     try:
#         st.title("Система анализа видеопотоков")
#         st.sidebar.header("Панель управления")
        
#         # Добавляем описание функционала
#         st.markdown("""
#         ### Возможности системы:
#         - 📹 Загрузка нескольких видео одновременно
#         - 🎯 Автоматическое определение зон интереса
#         - ⚡ Быстрая обработка видеопотоков
#         - 🔄 Возможность остановки и возобновления обработки
        
#         ### Как использовать:
#         1. Загрузите видео файлы через панель слева
#         2. Дождитесь определения зон интереса
#         3. Нажмите кнопку "Обработать видео"
#         4. Наблюдайте за результатами в реальном времени
#         """)
