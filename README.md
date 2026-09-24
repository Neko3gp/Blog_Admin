# Administrador de Blog

Aplicación de escritorio para administrar un blog con una interfaz Python/CustomTkinter, persistencia en Oracle Database Free y lógica de negocio en paquetes PL/SQL.
## Qué incluye

- Feed de artículos con orden por fecha y filtros por categoría y etiqueta.
- Vista de detalle con el texto completo y comentarios.
- Alta de artículos con selección múltiple de etiquetas y categorías.
- Gestión de usuarios, categorías y etiquetas desde la interfaz.
- Base de datos Oracle reproducible mediante Docker Compose.
- Datos semilla para poder probar la aplicación inmediatamente.
- Pruebas de conexión e integración en `python_devops/`.
## Requisitos

- Docker Desktop instalado y abierto.
- Git, si el proyecto se obtuvo desde un repositorio.
- Python 3.11 o superior para la aplicación.
- Una sesión gráfica activa para abrir CustomTkinter.
- En macOS, Python debe incluir Tcl/Tk 8.6 o superior. El Python de Command Line Tools puede traer Tk 8.5 y no es compatible con esta GUI.

La base de datos se ejecuta dentro de Docker, por lo que no es necesario instalar Oracle localmente.
## Inicio rápido en macOS

Desde la raíz del proyecto:

```bash
chmod +x start.sh install_python.sh
./start.sh
```

`start.sh` comprueba Docker, levanta Oracle, espera a que esté disponible, carga el esquema y los paquetes PL/SQL si todavía no existen tablas, crea el entorno virtual y ejecuta la prueba de conexión.

Cuando termine, abre la aplicación con:

```bash
cd python_devops
TK_SILENCE_DEPRECATION=1 .venv/bin/python main_gui.py
```

El script `start.sh` utiliza el `python3` disponible en el sistema. Si la comprobación de Tk falla o la ventana aparece vacía, prepara primero un Python compatible:

```bash
./install_python.sh
cd python_devops
TK_SILENCE_DEPRECATION=1 .venv/bin/python main_gui.py
```

El instalador descarga CPython 3.12 para Apple Silicon (`arm64`) o Intel (`x86_64`) dentro de `.python/`, comprueba Tcl/Tk y recrea `python_devops/.venv`.
## Instalación manual

### 1. Levantar Oracle

```bash
docker compose up -d
docker compose ps
```

Espera a que `blog_oracle_db` aparezca como `healthy`. La primera ejecución puede tardar varios minutos. También puedes seguir el arranque con:

```bash
docker logs -f blog_oracle_db
```

### 2. Cargar el esquema y PL/SQL

Solo es necesario al crear el volumen por primera vez o después de eliminarlo:

```bash
docker exec -i blog_oracle_db sqlplus -s blog_admin/admin123@localhost:1521/FREEPDB2 < Schema_db/01_schema.sql
docker exec -i blog_oracle_db sqlplus -s blog_admin/admin123@localhost:1521/FREEPDB2 < pl_sql_backend/02_procedures.sql
```

`Schema_db/01_schema.sql` recrea las tablas y vuelve a insertar los datos semilla. Es un script destructivo: elimina las tablas existentes antes de crearlas.

### 3. Crear el entorno Python

```bash
cd python_devops
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/pip install -r requirements.txt
```

En macOS, confirma que el intérprete del entorno usa Tk moderno:

```bash
.venv/bin/python -c "import tkinter as tk; print(tk.Tcl().eval('info patchlevel'))"
```

El resultado debe ser `8.6.x`, `9.x` u otra versión superior a `8.5`.

### 4. Probar y abrir la aplicación

```bash
.venv/bin/python test_connection.py
.venv/bin/python main_gui.py
```

## Uso de la aplicación

Al abrirse, la pantalla **Inicio** muestra el feed.

- **Inicio:** ordena por artículos recientes o antiguos y filtra por una categoría o etiqueta.
- **Tarjeta de artículo:** haz clic en el título o metadatos para abrir el detalle.
- **Detalle:** muestra el texto, comentarios existentes y el formulario para agregar comentarios. Selecciona el usuario, escribe el comentario y pulsa **Comentar**.
- **Usuarios:** consulta los usuarios disponibles y permite registrar nuevos usuarios.
- **Categorías:** consulta, registra, edita y elimina categorías; el slug URL se genera automáticamente.
- **Etiquetas:** consulta, registra, edita y elimina etiquetas; el slug URL se genera automáticamente.
- **Publicar artículo:** abre una ventana independiente. Completa título, texto y autor; abre **Etiquetas** y **Categorías** para marcar varias opciones y pulsa **Publicar Artículo**.
- **Botón de menú:** oculta o muestra la barra lateral para ampliar el área de contenido.

Las operaciones de escritura se realizan mediante procedimientos PL/SQL. Los listados tienen consultas de respaldo en Python para que la interfaz pueda seguir mostrando datos aunque un procedimiento de lectura no devuelva un cursor.

## Credenciales y conexión

Estos valores están definidos en `docker-compose.yml` y `python_devops/db_connection.py`:

| Parámetro | Valor |
|---|---|
| Host | `localhost` |
| Puerto | `1521` |
| Service/PDB | `FREEPDB2` |
| Usuario de aplicación | `blog_admin` |
| Contraseña | `admin123` |

Cadena equivalente: `blog_admin/admin123@localhost:1521/FREEPDB2`.

No cambies un valor sin actualizar tanto Docker como Python. Estas credenciales son de desarrollo local, no de producción.

## Pruebas y comprobaciones

Desde `python_devops/`:

```bash
.venv/bin/python test_connection.py
.venv/bin/python test_integration.py
python -m py_compile db_connection.py main_gui.py theme.py ui_toolkit.py utils.py views/*.py widgets/*.py
```

La primera prueba verifica conexión, consulta básica y lectura de CLOB. La segunda verifica tablas semilla y llamadas a los paquetes PL/SQL.

### Importante sobre `test_integration.py`

La prueba de integración inserta datos de prueba y espera las cantidades iniciales del esquema. No es idempotente: si se ejecuta varias veces sobre el mismo volumen, los conteos aumentan y algunas comprobaciones pueden informar duplicados, por ejemplo `Email ya registrado`, `Tag ya asignado` o `Categoría ya asignada`. Eso indica datos de ejecuciones previas, no necesariamente un fallo de conexión.

Para una ejecución limpia de la integración, elimina el volumen de Oracle y vuelve a inicializar todo:

```bash
docker compose down -v
docker compose up -d
./start.sh
```

Este procedimiento borra todos los datos guardados en la base local. Úsalo únicamente cuando no necesites conservarlos.

## Arquitectura y estructura

```text
.
├── docker-compose.yml             # Oracle Database Free en Docker
├── Schema_db/01_schema.sql        # Tablas, claves, relaciones y datos semilla
├── pl_sql_backend/02_procedures.sql # Paquetes PL/SQL de escritura y lectura
├── start.sh                        # Arranque automático del entorno
├── install_python.sh               # Python 3.12 con Tcl/Tk para macOS
├── documento_descriptivo.tex       # Documento descriptivo del proyecto
└── python_devops/
   ├── db_connection.py           # Conexión Oracle y helpers de procedimientos
   ├── main_gui.py                 # Punto de entrada de la interfaz
   ├── requirements.txt            # Dependencias Python
   ├── test_connection.py          # Prueba mínima de conexión
   ├── test_integration.py         # Prueba de integración Oracle/PL/SQL
   ├── theme.py                   # Colores y estilos compartidos
   ├── utils.py                   # Consultas seguras y mapas de usuarios
   ├── views/                     # Feed, detalle, usuarios y taxonomía
   └── widgets/                   # Tarjetas, chips y componentes reutilizables
```

El modelo de datos contiene usuarios, artículos, comentarios, etiquetas y categorías. Las relaciones muchos-a-muchos se almacenan en `article_tags` y `article_categories`. La conexión Python usa `oracledb` y convierte automáticamente los CLOB a texto.

## Solución de problemas

### Docker no está listo

Abre Docker Desktop y comprueba:

```bash
docker info
docker compose ps
```

Si el contenedor quedó detenido:

```bash
docker compose up -d
```

### `ORA-12514`, `ORA-12154` o fallo de conexión

Comprueba que el contenedor esté `healthy`, que el puerto `1521` no esté ocupado y que se use `FREEPDB2` con el DSN completo:

```bash
docker exec -i blog_oracle_db sqlplus -s blog_admin/admin123@localhost:1521/FREEPDB2
```

### La GUI no aparece o aparece vacía en macOS

Comprueba Tk con el intérprete que realmente ejecuta la app:

```bash
.venv/bin/python -c "import tkinter as tk; print(tk.Tcl().eval('info patchlevel'))"
```

Si muestra Tk 8.5, ejecuta `./install_python.sh` y vuelve a crear el entorno. No mezcles el `python` del sistema con el `.venv`.

### Faltan artículos, usuarios, categorías o etiquetas

Verifica que el esquema y los procedimientos se hayan cargado. Para reconstruir la base desde cero, usa `docker compose down -v` y repite el inicio rápido.

### El puerto 1521 está ocupado

Detén el servicio que usa el puerto o cambia el mapeo en `docker-compose.yml` y el puerto utilizado en `DB_DSN` dentro de `python_devops/db_connection.py`.

## Desarrollo y mantenimiento

- Mantén sin cambios los nombres de tablas, columnas y procedimientos porque Python depende de ese contrato.
- Después de modificar SQL, vuelve a cargar primero el esquema si cambió el modelo y después `02_procedures.sql`.
- Después de modificar Python, ejecuta al menos `test_connection.py` y la compilación con `py_compile`.
- No guardes credenciales reales en el repositorio; las incluidas son únicamente para el entorno local de desarrollo.
