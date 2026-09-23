#!/usr/bin/env bash
# Jalankan semua server + UI (Linux/macOS). Ctrl+C menghentikan semuanya.
cd "$(dirname "$0")"
export PYTHONPATH="$(pwd)"

# Pakai virtualenv lokal jika ada
if [ -f .venv/bin/activate ]; then
    source .venv/bin/activate
fi

# Muat variabel dari .env
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

trap 'kill $(jobs -p) 2>/dev/null' EXIT

python -m uvicorn service_directory.app:app --host 0.0.0.0 --port 9000 &
sleep 2
python -m uvicorn finance_server.app:app --host 0.0.0.0 --port 8101 &
python -m uvicorn inventory_server.app:app --host 0.0.0.0 --port 8102 &
python -m uvicorn sales_server.app:app --host 0.0.0.0 --port 8103 &
python -m uvicorn management_server.app:app --host 0.0.0.0 --port 8104 &
sleep 3
python -m streamlit run finance_server/ui.py --server.port 8501 &
python -m streamlit run inventory_server/ui.py --server.port 8502 &
python -m streamlit run sales_server/ui.py --server.port 8503 &
python -m streamlit run management_server/ui.py --server.port 8504 &
wait
