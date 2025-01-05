import streamlit as st
import hashlib
import json
import os
import files.profile as pf
import files.editData as ed
import files.adminSettingsVideoZone as asvz
import files.videoProcessing as vp

# Файл для хранения базы данных пользователей
os.makedirs(f'users', exist_ok=True)
DB_FILE = "users/users_database.json"

# Функция для загрузки пользователей из файла
def load_users():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {}

# Функция для сохранения пользователей в файл
def save_users(users):
    with open(DB_FILE, "w") as f:
        json.dump(users, f)

users = load_users()

# Функция для хеширования пароля
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Функция для регистрации нового пользователя
def register_user(username, password):
    if username in users:
        return False
    users[username] = hash_password(password)
    save_users(users)
    return True

# Функция для аутентификации пользователя
def authenticate_user(username, password):
    if username not in users:
        return False
    return users[username] == hash_password(password)

def personal_account_admin():
    # Отображение имени пользователя в боковой панели
    st.sidebar.header(f":violet[ 👤 Личный кабинет админнистратора {st.session_state.username}]", divider='rainbow')
    
    # Временные папки
    os.makedirs("users/detected_cars", exist_ok=True)
    os.makedirs("users/detected_plates", exist_ok=True)
    os.makedirs("users/detected_numbers", exist_ok=True)
       
    # Создание переключателя страниц
    page = st.sidebar.radio("Выберите пункт:", 
                            ["👤 Профиль", "⚙️ Настройка зоны интереса", 
                             "📋 Создание / редактирование базы номеров", "🎥 Обработка видео"])

    st.sidebar.markdown("---")
   
    # Отображение выбранной страницы и соответствующей боковой панели
    if page == "👤 Профиль":
        pf.user_profile()
    elif page == "⚙️ Настройка зоны интереса":
        asvz.video_zone()
        asvz.area_of_interest()
    elif page == "📋 Создание / редактирование базы номеров":
        ed.edit_data()
    elif page == "🎥 Обработка видео":
        vp.main()
    
    st.sidebar.markdown("---")
    
    # Кнопка выхода в боковой панели
    if st.sidebar.button("🚪 :red[Выход]", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()
    
    st.sidebar.markdown("---")     
    
    
# Функция для отображения личного кабинета пользователя
def personal_account():
    
    # Отображение имени пользователя в боковой панели
    st.sidebar.header(f":violet[ 👤 Личный кабинет пользователя {st.session_state.username}]", divider='rainbow')
    
    # Создание переключателя страниц
    page = st.sidebar.radio("Выберите пункт:", 
                            ["👤 Профиль", "🎥 Обработка видео"])

    st.sidebar.markdown("---")
   
    # Отображение выбранной страницы и соответствующей боковой панели
    if page == "👤 Профиль":
        pf.user_profile()
    elif page == "🎥 Обработка видео":
        vp.main()
   
    st.sidebar.markdown("---")
    
    # Кнопка выхода в боковой панели
    if st.sidebar.button("🚪 :red[Выход]", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()
    
    st.sidebar.markdown("---")        

# Основная функция приложения
def main():

    # Устанавливаем конфигурацию страницы в режиме "wide" (расширенный вид)
    st.set_page_config(layout="wide")

    # Проверка наличия файла с пользователями
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        # st.title("Личный кабинет")
        st.header(":blue[ИИ-система для автоматизированного распознавания автомобилей и предоставления доступа на территорию заказчика]", divider='rainbow', anchor='center')

        # Создаем 3 колонки
        col1, col2, col3 = st.columns(3)
        with col1:
            st.image("main_diplom/background/foto2.png")
        with col2:
            # Создаем вкладки для входа и регистрации
            tab1, tab2 = st.tabs([":violet[_Вход в систему_]", ":green[_Регистрация_]"])

            with tab1:
                st.header(":violet[Вход в систему]", divider='rainbow')
                login_username = st.text_input(":violet[_Логин_]", key="login_username")
                login_password = st.text_input(":violet[_Пароль_]", type="password", key="login_password")

                if st.button(":violet[Войти]", key="login_button"):
                    if authenticate_user(login_username, login_password):
                        st.session_state.logged_in = True
                        st.session_state.username = login_username
                        st.success(f"Добро пожаловать, {login_username}!")
                        st.rerun()
                    else:
                        st.error("Неверный логин или пароль.")

            with tab2:
                st.header(":green[Регистрация]", divider='rainbow')
                reg_username = st.text_input(":green[_Придумайте логин_]", key="reg_username")
                reg_password = st.text_input(":green[_Придумайте пароль_]", type="password", key="reg_password")

                if st.button(":green[Зарегистрироваться]"):
                    if register_user(reg_username, reg_password):
                        st.success("Регистрация успешна! Теперь вы можете войти.")
                    else:
                        st.error("Пользователь с таким логином уже существует.")
        with col3:
            st.image("main_diplom/background/foto1.png")
    else:
        if st.session_state.username == "admin":
            personal_account_admin()
        else:
            personal_account()



if __name__ == "__main__":
  main()
