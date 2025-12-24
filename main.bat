@echo off
REM Активируем виртуальное окружение
call .venv\Scripts\activate.bat

REM Запускаем наше приложение
python gui_app.py

REM Пауза для удобства просмотра сообщений (если потребуется)
pause