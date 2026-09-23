@echo off
cd /d "%~dp0"
set PYTHONPATH=%cd%

rem Pakai virtualenv lokal jika ada
if exist .venv\Scripts\activate.bat call .venv\Scripts\activate.bat

rem Muat variabel dari .env
if exist .env for /f "usebackq eol=# tokens=1,* delims==" %%a in (".env") do set "%%a=%%b"

start "Service Directory" cmd /k python -m uvicorn service_directory.app:app --host 0.0.0.0 --port 9000
timeout /t 2 >nul

start "Finance API" cmd /k python -m uvicorn finance_server.app:app --host 0.0.0.0 --port 8101
start "Inventory API" cmd /k python -m uvicorn inventory_server.app:app --host 0.0.0.0 --port 8102
start "Sales API" cmd /k python -m uvicorn sales_server.app:app --host 0.0.0.0 --port 8103
start "Management API" cmd /k python -m uvicorn management_server.app:app --host 0.0.0.0 --port 8104

timeout /t 3 >nul

start "Finance UI" cmd /k python -m streamlit run finance_server/ui.py --server.port 8501
start "Inventory UI" cmd /k python -m streamlit run inventory_server/ui.py --server.port 8502
start "Sales UI" cmd /k python -m streamlit run sales_server/ui.py --server.port 8503
start "Management UI" cmd /k python -m streamlit run management_server/ui.py --server.port 8504
