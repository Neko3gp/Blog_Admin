#!/usr/bin/env bash
# Arranca Oracle (Docker) y deja lista la app Python.
set -euo pipefail
cd "$(dirname "$0")"

echo "==> Verificando Docker..."
if ! docker info >/dev/null 2>&1; then
  echo "Docker no está listo. Abre Docker Desktop y vuelve a ejecutar este script."
  open -a Docker 2>/dev/null || open /Applications/Docker.app || true
  exit 1
fi

echo "==> Levantando Oracle (docker compose up -d)..."
docker compose up -d

echo "==> Esperando DATABASE IS READY TO USE! (puede tardar varios minutos la 1ª vez)..."
until docker logs blog_oracle_db 2>&1 | grep -q "DATABASE IS READY TO USE!"; do
  sleep 5
  echo "    ...aún inicializando..."
done
echo "==> Oracle listo."

echo "==> Aplicando schema + procedimientos (si hace falta)..."
# Carga idempotente vía sqlplus dentro del contenedor (usuario de app)
if ! docker exec blog_oracle_db bash -c "echo 'SELECT COUNT(*) FROM user_tables;' | sqlplus -s blog_admin/admin123@FREEPDB2" 2>/dev/null | grep -Eq '[1-9][0-9]*'; then
  echo "    Cargando Schema_db/01_schema.sql ..."
  docker exec -i blog_oracle_db sqlplus -s blog_admin/admin123@FREEPDB2 < Schema_db/01_schema.sql
  echo "    Cargando pl_sql_backend/02_procedures.sql ..."
  docker exec -i blog_oracle_db sqlplus -s blog_admin/admin123@FREEPDB2 < pl_sql_backend/02_procedures.sql
else
  echo "    Tablas ya presentes; se omite la carga DDL."
fi

echo "==> Probando conexión Python..."
cd python_devops
if [ ! -d .venv ]; then
  python3 -m venv .venv
  .venv/bin/pip install -r requirements.txt customtkinter
fi
.venv/bin/python test_connection.py

echo ""
echo "Listo. Para abrir la GUI:"
echo "  cd python_devops && .venv/bin/python main_gui.py"
