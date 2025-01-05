import streamlit.web.cli as stcli
import sys

"""
Этот скрипт запускает Streamlit приложение.

Как это работает:
1. Импортируем необходимые библиотеки:
    - streamlit.web.cli для запуска приложения
    - sys для работы с аргументами командной строки

2. В блоке if __name__ == "__main__":
    - Устанавливаем аргументы командной строки для запуска Streamlit
    - Запускаем приложение main.py через Streamlit CLI
"""

if __name__ == "__main__":
     sys.argv = ["streamlit", "run", "main_diplom/main.py", "--theme.base", "dark"]
     sys.exit(stcli.main())