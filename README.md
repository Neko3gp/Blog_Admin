# Administrador de Blog — Bases de Datos Avanzadas

Proyecto de 1ª evaluación: sistema de administración de blog con persistencia en Oracle (PL/SQL) y consola en Python (`oracledb`).

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

## Credenciales de conexión (estándar del equipo — no modificar)

| Parámetro | Valor |
|---|---|
| Host | `localhost` |
| Puerto | `1521` |
| Service / PDB | `FREEPDB1` |
| Usuario | `blog_admin` |
| Password | `admin123` |

String de conexión para `oracledb`: `blog_admin/admin123@localhost:1521/FREEPDB1`

## Estructura del repo

- `sql/01_schema.sql` — DDL + datos semilla (Integrante 1)
- `sql/02_procedures.sql` — Paquetes PL/SQL (Integrante 2)
- `python/` — Aplicación de consola (Integrante 3)

## Reglas del equipo

- Nadie programa directo en `main`. Trabajar en `feat/schema-db`, `feat/plsql-backend` o `feat/python-frontend` según el rol.
- Antes de fusionar a `main`, correr el código de esa rama localmente al menos una vez.
- Los nombres de columnas y el contrato de nombres de paquetes/procedimientos (ver documento del proyecto) están **congelados**: no se cambian sin avisar al equipo.
- Orden de fusión: 1º DDL → 2º PL/SQL → 3º Python.
