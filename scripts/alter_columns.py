import sys
import os

# Agregamos la ruta principal al path para poder importar módulos de la app
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import engine
from sqlalchemy import text

def alter_columns():
    print("Iniciando alteración de columnas para soportar cifrado largo...")
    queries = [
        "ALTER TABLE users ALTER COLUMN name TYPE VARCHAR(500);",
        "ALTER TABLE users ALTER COLUMN last_name TYPE VARCHAR(500);",
        "ALTER TABLE users ALTER COLUMN phone TYPE VARCHAR(500);",
        "ALTER TABLE doctors ALTER COLUMN professional_license TYPE VARCHAR(500);",
        "ALTER TABLE doctors ALTER COLUMN office TYPE VARCHAR(500);"
    ]
    
    with engine.begin() as conn:
        for query in queries:
            try:
                conn.execute(text(query))
                print(f"Ejecutado: {query}")
            except Exception as e:
                print(f"Error al ejecutar '{query}': {e}")
                
    print("Alteración completada.")

if __name__ == "__main__":
    alter_columns()
