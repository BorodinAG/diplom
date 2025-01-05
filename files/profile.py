import streamlit as st
import json
import os
import datetime
from PIL import Image

def user_profile():

    st.header(":violet[Профиль пользователя]", divider='rainbow')
    
    # Создаем каталог пользователя, если он еще не существует
    os.makedirs(f"users/{st.session_state.username}", exist_ok=True)
            
    # Загрузка информации о пользователе
    user_info_file = f"users/{st.session_state.username}/{st.session_state.username}.json"
    if os.path.exists(user_info_file):
        with open(user_info_file, "r") as f:
            user_info = json.load(f)
    else:
    # Если файл не существует, создаем его и заполняем пустыми значениями
        st.warning('Внимание! Заполните и сохраните информацию о себе!')
        st.warning('Это необходимо для корректной работы приложения!')
        user_info = {
            "фамилия": "",
            "имя": "",
            "отчество": "",
            "дата_рождения": "",
            "пол": "",
            "фото": None
        }

    # Отображение текущей информации
    col1, col2 = st.columns([1, 2])
    with col1:
        if user_info["фото"] is not None:
            st.image(user_info["фото"], caption="Фото пользователя", width=200)
        else:
            st.info("Фото не загружено")
            
    with col2:
        data = {
            "Параметр": ["Фамилия", "Имя", "Отчество", "Дата рождения", "Пол"],
            "Значение": [
                user_info["фамилия"] or "Не указано",
                user_info["имя"] or "Не указано",
                user_info["отчество"] or "Не указано",
                user_info["дата_рождения"] or "Не указано",
                user_info["пол"] or "Не указано"                  
            ]
        }
        st.table(data)

    if 'show_menu' not in st.session_state:
        st.session_state.show_menu = False

    
    if not st.session_state.show_menu:
        if st.sidebar.button(":blue[Изменить]", use_container_width=True):
            st.session_state.show_menu = True
            st.rerun()
    else:
        with st.form("edit_form"):
            col1, col2 = st.columns(2)
            with col2:
                # Отображение и редактирование информации о пользователе
                user_info["дата_рождения"] = st.date_input("_Дата рождения_*", value=datetime.datetime.strptime(user_info["дата_рождения"], "%Y-%m-%d").date() if user_info["дата_рождения"] else None, min_value=datetime.date(1920, 1, 1))
                user_info["пол"] = st.selectbox("_Пол_*", ["", "Мужской", "Женский"], index=["", "Мужской", "Женский"].index(user_info["пол"]))

                # Загрузка фото
                uploaded_file = st.file_uploader("_Фото пользователя_*", type=["jpg", "jpeg", "png"])
                if uploaded_file is not None:
                    image = Image.open(uploaded_file)
                    st.image(image, caption="Фото пользователя", use_container_width=True)
                    # Сохранение фото
                    photo_path = fr"users/{st.session_state.username}/{st.session_state.username}_photo.png"
                    image.save(photo_path)
                    user_info["фото"] = photo_path
                
            with col1:
                # Отображение и редактирование информации о пользователе
                user_info["фамилия"] = st.text_input("_Фамилия_*", user_info["фамилия"])                
                user_info["имя"] = st.text_input("_Имя_*", user_info["имя"])
                user_info["отчество"] = st.text_input("_Отчество_*", user_info["отчество"])

                col11, col21 = st.columns(2)
                with col11:
                    if st.form_submit_button(":blue[Сохранить]", use_container_width=True):
                                                
                        # Проверка заполнения всех обязательных полей
                        if not user_info["фамилия"] or not user_info["имя"] or not user_info["отчество"] or not user_info["дата_рождения"] or not user_info["пол"] or not os.path.exists(user_info.get("фото", "")):
                            st.error("Пожалуйста, заполните все обязательные поля и загрузите фото")
                            st.stop()
                        
                        # Преобразование даты в строку для сохранения в JSON
                        user_info["дата_рождения"] = user_info["дата_рождения"].strftime("%Y-%m-%d") if user_info["дата_рождения"] else ""
                        
                        # Сохранение информации о пользователе
                        # os.makedirs(f"users/{st.session_state.username}", exist_ok=True)                    
                        with open(user_info_file, "w") as f:
                            json.dump(user_info, f)
                        st.success("Информация успешно сохранена")
                        st.session_state.show_menu = False
                        st.rerun()

                with col21:
                    if st.form_submit_button(":red[Отмена]", use_container_width=True):
                        # Проверка заполнения всех обязательных полей
                        if not user_info["фамилия"] or not user_info["имя"] or not user_info["отчество"] or not user_info["дата_рождения"] or not user_info["пол"] or not os.path.exists(user_info.get("фото", "")):                            
                            st.error("Пожалуйста, заполните все обязательные поля и загрузите фото")
                            st.stop()
                        
                        st.session_state.show_menu = False
                        st.rerun()

"""
Модуль профиля пользователя (profile.py)

Данный модуль реализует функционал управления профилем пользователя в системе. 
Основные возможности:

1. Отображение профиля:
   - Показ фотографии пользователя
   - Вывод персональных данных в виде таблицы (ФИО, дата рождения, пол)
   - Интуитивно понятный интерфейс с разделением на колонки

2. Редактирование профиля:
   - Удобная форма для изменения всех персональных данных
   - Загрузка фотографии пользователя (поддержка форматов JPG, JPEG, PNG)
   - Валидация обязательных полей
   - Кнопки "Сохранить" и "Отмена" для управления изменениями

3. Хранение данных:
   - Автоматическое создание пользовательской директории
   - Сохранение информации в JSON-формате
   - Отдельное хранение фотографии пользователя
   - Обработка случаев отсутствия данных

4. Безопасность:
   - Проверка заполнения всех обязательных полей
   - Контроль корректности введенных данных
   - Защита от потери данных при отмене изменений

5. Удобство использования:
   - Интерактивные уведомления о статусе операций
   - Подсказки при незаполненных данных
   - Автоматическое обновление интерфейса после изменений
   - Интуитивно понятная навигация

Технические особенности:
- Использование библиотеки Streamlit для создания веб-интерфейса
- Работа с изображениями через библиотеку PIL
- Управление файловой системой через модуль os
- Обработка дат с помощью datetime
- Сериализация данных в формат JSON
"""