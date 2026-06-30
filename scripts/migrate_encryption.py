import sys
import os

# Agregamos la ruta principal al path para poder importar módulos de la app
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy.orm.attributes import flag_modified
from app.core.database import SessionLocal
import main # Import the main module so all routers and models are loaded
from app.features.users.models.user_model import Usuario
from app.features.users.models.doctor_model import Doctor
from app.features.users.models.patient_model import Patient
from app.features.appointments.models.appointment_model import Appointment

def migrate():
    print("Iniciando migración de cifrado...")
    db = SessionLocal()
    try:
        # Migrar Usuarios
        usuarios = db.query(Usuario).all()
        print(f"Migrando {len(usuarios)} usuarios...")
        for user in usuarios:
            # Forzamos a SQLAlchemy a marcar estos campos como "sucios/modificados".
            # Como usamos EncryptedString, al guardar en BD volverán a pasar por el CipherPipe.
            flag_modified(user, "name")
            flag_modified(user, "last_name")
            if user.phone:
                flag_modified(user, "phone")
        
        # Migrar Doctores
        doctores = db.query(Doctor).all()
        print(f"Migrando {len(doctores)} doctores...")
        for doctor in doctores:
            if doctor.professional_license:
                flag_modified(doctor, "professional_license")
            if doctor.office:
                flag_modified(doctor, "office")
                
        db.commit()
        print("Migración completada con éxito. Todos los registros ahora usan el nuevo formato (enc::v1::).")
        
    except Exception as e:
        db.rollback()
        print(f"Error durante la migración: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
