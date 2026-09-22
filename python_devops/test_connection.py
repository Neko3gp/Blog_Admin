import oracledb

# Credenciales estándar del proyecto (del README)
USER = "blog_admin"
PASSWORD = "admin123"
DSN = "localhost:1521/FREEPDB1"

def main():
    try:
        with oracledb.connect(user=USER, password=PASSWORD, dsn=DSN) as connection:
            print("Conexión exitosa a Oracle.")
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 FROM DUAL")
                result = cursor.fetchone()
                print(f"Query de prueba OK. Resultado: {result[0]}")
    except oracledb.Error as e:
        print("XXXXX Error al conectar o ejecutar la query XXXXX")
        print(e)

if __name__ == "__main__":
    main()
