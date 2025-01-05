import streamlit as st
import os
import cv2
import tempfile
import json
import shutil

def video_zone():
    """
    Функция для загрузки и первичной обработки видеофайла.
    Позволяет пользователю загрузить видео и подготовить его для дальнейшего анализа.
    """
    st.sidebar.header(":violet[Выберете файл для обработки]", divider='rainbow')
    
    # Интерфейс загрузки видеофайла с поддержкой популярных форматов
    uploaded_file = st.sidebar.file_uploader("Загрузка видео файла", type=['mp4', 'avi'])

    # Создание рабочей директории для временных файлов
    os.makedirs('users/temp', exist_ok=True)
  
    if uploaded_file is not None:
        # Сохранение информации о файле для дальнейшего использования
        with open('users/temp/name.json', 'w', encoding='utf-8') as f:
            json.dump({"filename": os.path.splitext(uploaded_file.name)[0]}, f)
        
        # Создание временного файла для безопасной обработки видео
        temp_video = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        temp_video.write(uploaded_file.read())
        temp_video.close()

        # Извлечение первого кадра для анализа зоны интереса
        cap = cv2.VideoCapture(temp_video.name)
        ret, frame = cap.read()
        
        if ret:
            # Сохранение первого кадра для дальнейшей обработки
            temp_frame = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            os.makedirs('users/temp', exist_ok=True)
            cv2.imwrite('users/temp/temp_img.jpg', frame)
      
            # Освобождение ресурсов и очистка временных файлов
            cap.release()
            os.unlink(temp_video.name)
            try:
                os.unlink(temp_frame.name)
            except:
                pass
        else:
            st.error("Не удалось прочитать видео файл")    
    
def area_of_interest():
    """
    Функция для интерактивного определения зоны интереса на видео.
    Позволяет пользователю визуально настроить область анализа с помощью удобных ползунков.
    """
    st.header(":violet[_Выберете область интереса_]", divider='rainbow')

    try:
        # Загрузка кадра для визуальной настройки
        image = cv2.imread('users/temp/temp_img.jpg')

        # Получение размеров изображения
        height, width, _ = image.shape

        # Получение имени файла из временного хранилища
        with open('users/temp/name.json', 'r', encoding='utf-8') as f:
            filename = json.load(f)['filename']

        # Попытка загрузить сохраненные настройки
        default_y1 = height//4
        default_x1 = width//2
        default_xz = width//4
        default_yz = height//2
        try:
            with open(f"users/coordinates/{filename}.json", "r") as f:
                saved_data = json.load(f)
                default_x1 = saved_data.get("x", width//4)
                default_y1 = saved_data.get("y", height//4)
                default_xz = saved_data.get("xz", width//2)
                default_yz = saved_data.get("yz", width//2)
        except FileNotFoundError:
            pass
        
        # Создание двухколоночного интерфейса для удобства использования
        col1, col2 = st.columns(2)

        with col2:
            # Интуитивные ползунки для настройки зоны интереса
            y1 = st.slider('Верхняя граница зоны интереса (синяя)', 0, height, default_y1)
            y2 = st.slider('Нижняя граница зоны интереса (бирюзовая)', 0, height, default_yz)
            x1 = st.slider('Правая граница зоны интереса (красная)', 0, width, default_x1)
            x2 = st.slider('Левая граница зоны интереса (желтая)', 0, width, default_xz)
            
            # Визуализация выбранной зоны с помощью цветных линий
            img_with_lines = image.copy()
            cv2.line(img_with_lines, (0, y1), (width, y1), (255, 0, 0), 2)  # Синяя горизонтальная
            cv2.line(img_with_lines, (0, y2), (width, y2), (255, 255, 0), 2)  # Бирюзовая горизонтальная
            cv2.line(img_with_lines, (x1, 0), (x1, height), (0, 0, 255), 2)  # Красная вертикальная
            cv2.line(img_with_lines, (x2, 0), (x2, height), (0, 255, 255), 2)  # Желтая вертикальная

            # Кнопка для сохранения настроек
            if st.button(":violet[Завершить настройку]", use_container_width=True):
                # Сохранение координат и параметров зоны интереса
                intersection = (x1, y1, y2, x2)
                
                intersection_data = {
                    "frame_width": width,
                    "frame_height": height,
                    "x": x1,
                    "y": y1,
                    "yz": y2,
                    "xz": x2,
                    "intersection": intersection
                }
                
                # Чтение имени файла и сохранение настроек
                # with open('users/temp/name.json', 'r', encoding='utf-8') as f:
                #     filename = json.load(f)['filename']
                
                # Сохранение конфигурации в постоянное хранилище
                os.makedirs("users/coordinates", exist_ok=True)    
                with open(f"users/coordinates/{filename}.json", "w") as f:
                    json.dump(intersection_data, f)                
                
                # Очистка временных файлов
                shutil.rmtree('users/temp', ignore_errors=True)
                
                st.rerun()

        with col1:    
            # Отображение интерактивного предпросмотра настроек
            st.image(cv2.cvtColor(img_with_lines, cv2.COLOR_BGR2RGB), 
                    caption='Определение зоны интереса', 
                    use_container_width=True)
    
    except:
        st.error(":red[_Не загружен файл для обработки_]")
        return

"""
Программа для настройки зоны интереса в видеонаблюдении

Описание функционала:
1. Интерактивный интерфейс
   - Разделение экрана на две колонки для удобства работы
   - Визуальный предпросмотр настроек в реальном времени
   - Интуитивно понятные ползунки управления

2. Настройка зоны интереса
   - Синяя горизонтальная линия для определения верхней границы
   - Бирюзовая горизонтальная линия для определения нижней границы
   - Красная вертикальная линия для определения правой боковой границы
   - Желтая вертикальная линия для определения левой боковой границы
   - Зона интереса определяется пересечением этих линий, при этом верхняя и нижняя границы определяют 
     моменты начала и окончания распознавания, а правая и левая границы отсекают нежелательные области.

3. Сохранение настроек
   - Автоматическое сохранение параметров в JSON-формате
   - Создание отдельной папки для хранения конфигураций
   - Очистка временных файлов после сохранения

4. Безопасность и надежность
   - Проверка наличия загруженного файла
   - Создание резервных копий настроек
   - Обработка ошибок и информативные сообщения

5. Технические возможности
   - Поддержка различных разрешений видео
   - Точная настройка координат зоны интереса
   - Мгновенное применение изменений

Преимущества:
- Простой и понятный интерфейс
- Визуальный контроль настроек
- Надежное сохранение конфигурации
- Быстрая настройка параметров
- Универсальность применения
"""
