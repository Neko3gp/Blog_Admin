# Administrador de Blog — Bases de Datos Avanzadas

Proyecto de 1ª evaluación: sistema de administración de blog con persistencia en Oracle (PL/SQL) y GUI en Python (`oracledb` + CustomTkinter).

## Cómo levantar el entorno

1. Tener Docker Desktop corriendo.
2. Desde la raíz del repo:
   ```
   docker compose up -d
   ```
3. La primera vez tarda unos minutos en inicializar. Verifica con:
   ```
   docker logs -f blog_oracle_db
   ```
   Espera al mensaje `DATABASE IS READY TO USE!`.
4. Cargar el schema y los paquetes PL/SQL (solo la primera vez, o tras recrear el volumen):
   ```
   docker exec -i blog_oracle_db sqlplus -s blog_admin/admin123@FREEPDB2 < Schema_db/01_schema.sql
   docker exec -i blog_oracle_db sqlplus -s blog_admin/admin123@FREEPDB2 < pl_sql_backend/02_procedures.sql
   ```

## Aplicación Python (GUI)

1. Entra a la carpeta de la app:
   ```
   cd python_devops
   ```
2. Crea un entorno virtual e instala dependencias:
   ```
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Prueba la conexión:
   ```
   python test_connection.py
   ```
4. Arranca la GUI:
   ```
   python main_gui.py
   ```

### Nota macOS (ventana negra / vacía)

CustomTkinter necesita **Tcl/Tk ≥ 8.6**. El Python de Command Line Tools (`/usr/bin/python3`, Tk 8.5) abre la GUI como fondo oscuro sin widgets.

Usa un Python 3.11+ con Tk moderno (Homebrew `python-tk`, instalador de python.org, o el script `install_python.sh` de la raíz del repo) y crea el venv con ese intérprete. Comprueba la versión de Tk:

```
python -c "import tkinter as tk; print(tk.Tcl().eval('info patchlevel'))"
```

Debe mostrar `8.6.x` o superior (p. ej. `9.0.x`), no `8.5.9`.

## Credenciales de conexión (estándar del equipo — no modificar)

| Parámetro | Valor |
|---|---|
| Host | `localhost` |
| Puerto | `1521` |
| Service / PDB | `FREEPDB2` |
| Usuario | `blog_admin` |
| Password | `admin123` |

String de conexión para `oracledb`: `blog_admin/admin123@localhost:1521/FREEPDB2`

## Estructura del repo

- `Schema_db/01_schema.sql` — DDL + datos semilla (Integrante 1)
- `pl_sql_backend/02_procedures.sql` — Paquetes PL/SQL (Integrante 2)
- `python_devops/` — Aplicación GUI (Integrante 3)

## Reglas del equipo

- Nadie programa directo en `main`. Trabajar en `/schema-db`, `/plsql-backend` o `/python-frontend` según el rol.
- Antes de fusionar a `main`, correr el código de esa rama localmente al menos una vez.
- Los nombres de columnas y el contrato de nombres de paquetes/procedimientos (ver documento del proyecto) están **congelados**: no se cambian sin avisar al equipo.
- Orden de fusión: 1º DDL → 2º PL/SQL → 3º Python.
