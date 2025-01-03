@echo off
REM Cambiar al directorio del proyecto Django
cd /web-philia


REM Ejecutar el servidor de desarrollo de Django
python manage.py runserver

REM Mantener la ventana abierta si ocurre un error
pause