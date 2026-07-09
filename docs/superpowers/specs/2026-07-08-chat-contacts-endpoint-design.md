# Chat: endpoint unificado de contactos (`GET /chat/contacts`)

## Problema

El front resuelve la lista de contactos del chat con 2 llamadas separadas (`GET /doctors/{id}/patients` + `GET /users/`), pasando `doctor_id` como query param y filtrando client-side. Se pide reemplazarlas por un único endpoint `GET /api/v1/chat/contacts` que resuelva todo server-side a partir del JWT del usuario autenticado.

## Corrección de un supuesto del pedido original

El pedido asume que el JWT ya trae `role`/`user_id`/`doctor_id`. Verificado en código: `create_access_token` (`app/features/users/application/auth/authenticate_user_usecase.py:29-31`) solo codifica `sub`, `user_id`, `role`. `get_current_user` (`app/core/dependencies.py:27-40`) decodifica el email (`sub`) y vuelve a resolver el `UserEntity` completo desde DB — no hay `doctor_id` en el token ni en el `UserEntity` resultante.

Esto no cambia el contrato con el front (sigue sin mandar nada más que el Bearer token): el `doctor_id` relevante por rol se resuelve **server-side**, dentro del use case, vía los repositorios existentes — el mismo patrón que ya usa `authenticate_user_usecase.py` para poblar el login response.

## Alcance

- Endpoint nuevo: `GET /api/v1/chat/contacts`.
- Auth: `Authorization: Bearer <JWT>`, mismo esquema que el resto de `/chat/*`. Sin `RoleChecker` — los 4 roles pasan la autenticación; el comportamiento por rol se resuelve dentro del use case (ver tabla abajo), no con un 403 a nivel de ruta.
- Sin paginación (mismo criterio que `/chat/inbox`).
- Fuera de alcance: cualquier cambio a `/doctors/{id}/patients` o `/users/` (quedan como están; el front deja de llamarlos para este caso de uso pero los endpoints no se tocan ni se deprecan en este trabajo).

## Comportamiento por rol

| Rol autenticado | Contactos devueltos |
|---|---|
| `doctor` | Sus pacientes (`patient.doctor_id == doctor propio`) |
| `recepcionista` | Pacientes del doctor de su consultorio + todos los usuarios con rol `doctor` (dedupe por `user_id`, excluye al propio usuario autenticado) |
| `paciente` | Su doctor asignado + el/los recepcionista(s) de ese mismo consultorio (mismo `doctor_id`) |
| `admin` (o cualquier rol no contemplado) | `[]` |

Reglas transversales:
- Excluir siempre al usuario autenticado de su propia lista de contactos.
- Sin duplicados — dedupe por `user_id` donde aplique (relevante en el caso `recepcionista`, donde teóricamente un mismo `user_id` no debería aparecer dos veces pero se dedupea defensivamente).
- Si el usuario autenticado no tiene perfil de `doctor`/`receptionist`/`patient` resuelto (dato inconsistente), el use case devuelve `[]` para ese rol en vez of lanzar error.

## Diseño técnico

### Response

Reutiliza el DTO existente `ChatUser` (`app/features/chat/domain/dtos.py`) como `response_model` — ya expone exactamente `user_id`, `name`, `last_name`, `role`, el shape pedido. No se crea un schema nuevo (mismo criterio que `InboxItemResponse`, que también vive en `domain/` y se usa directo como `response_model` en `chat_router.py`).

```json
[
  { "user_id": 5, "name": "María", "last_name": "Vela", "role": "paciente" },
  { "user_id": 2, "name": "Juan", "last_name": "Pérez", "role": "doctor" }
]
```

### Puerto nuevo (propio de `chat`, sigue el patrón "ports propios + adapters" del proyecto)

`app/features/chat/domain/ports.py` — agregar:

```python
class IChatContactsLookup(Protocol):
    def get_doctor_id_for_doctor(self, user_id: int) -> Optional[int]: ...
    def get_doctor_id_for_receptionist(self, user_id: int) -> Optional[int]: ...
    def get_doctor_id_for_patient(self, user_id: int) -> Optional[int]: ...
    def get_patients_of_doctor(self, doctor_id: int) -> List[ChatUser]: ...
    def get_receptionists_of_doctor(self, doctor_id: int) -> List[ChatUser]: ...
    def get_doctor_contact(self, doctor_id: int) -> Optional[ChatUser]: ...
    def get_all_doctors(self) -> List[ChatUser]: ...
```

Cada método es una traducción pura (users → `ChatUser`), sin lógica de negocio — la orquestación por rol vive en el use case, no en el adapter.

### Adapter: `ChatContactsLookupAdapter`

`app/features/chat/infrastructure/adapters/chat_contacts_lookup_adapter.py`, implementa `IChatContactsLookup`, envuelve (constructor) `DoctorRepository`, `ReceptionistRepository`, `PatientRepository`, `UserRepository` (las 4 ya existen en `users`, ya registradas en el container).

- `get_doctor_id_for_doctor(user_id)` → `doctor_repository.get_by_user_id(user_id)` → `.doctor_id` o `None`.
- `get_doctor_id_for_receptionist(user_id)` → `receptionist_repository.get_by_user_id(user_id)` → `.doctor_id` o `None`.
- `get_doctor_id_for_patient(user_id)` → `patient_repository.get_by_user_id(user_id)` → `.doctor_id` o `None`.
- `get_patients_of_doctor(doctor_id)` → `patient_repository.get_patients_by_doctor(doctor_id)` (ya hace `joinedload(Patient.user)`) → mapea cada `PatientEntity` a `ChatUser(user_id=p.user_id, name=p.user.name, last_name=p.user.last_name, role="paciente")`.
- `get_receptionists_of_doctor(doctor_id)` → `receptionist_repository.get_by_doctor_id(doctor_id)` (ya devuelve `List[UserEntity]`) → mapea a `ChatUser(..., role="recepcionista")`.
- `get_doctor_contact(doctor_id)` → `doctor_repository.get_by_id(doctor_id)` → si existe, `user_repository.get_by_id(doctor.user_id)` → `ChatUser(..., role="doctor")`; `None` si falta cualquiera de los dos.
- `get_all_doctors()` → `user_repository.get_by_role(RoleEnum.doctor)` (método nuevo, ver abajo) → mapea a `ChatUser(..., role="doctor")`.

### Método nuevo en `IUserRepository` / `UserRepository`

`app/features/users/domain/ports.py` — agregar a `IUserRepository`: `def get_by_role(self, role: RoleEnum) -> List[UserEntity]: ...`

`app/features/users/infrastructure/repositories/user_repository.py` — implementación:
```python
def get_by_role(self, role: RoleEnum) -> List[UserEntity]:
    users_db = self.db.query(Usuario).filter(Usuario.role == role, Usuario.is_active == True).all()
    return [UserEntity.model_validate(u) for u in users_db]
```
(mismo criterio `is_active == True` que ya usan `patient_repository.get_patients_by_doctor` y `receptionist_repository.get_by_doctor_id`).

### Use case: `GetChatContactsUseCase`

`app/features/chat/application/get_chat_contacts_usecase.py`:

```python
class GetChatContactsUseCase:
    def __init__(self, contacts_lookup: IChatContactsLookup):
        self.contacts_lookup = contacts_lookup

    def execute(self, current_user_id: int, role: str) -> List[ChatUser]:
        if role == "doctor":
            doctor_id = self.contacts_lookup.get_doctor_id_for_doctor(current_user_id)
            return self.contacts_lookup.get_patients_of_doctor(doctor_id) if doctor_id else []

        if role == "recepcionista":
            doctor_id = self.contacts_lookup.get_doctor_id_for_receptionist(current_user_id)
            contacts = self.contacts_lookup.get_patients_of_doctor(doctor_id) if doctor_id else []
            contacts = contacts + self.contacts_lookup.get_all_doctors()
            seen = set()
            deduped = []
            for c in contacts:
                if c.user_id == current_user_id or c.user_id in seen:
                    continue
                seen.add(c.user_id)
                deduped.append(c)
            return deduped

        if role == "paciente":
            doctor_id = self.contacts_lookup.get_doctor_id_for_patient(current_user_id)
            if not doctor_id:
                return []
            contacts = []
            doctor_contact = self.contacts_lookup.get_doctor_contact(doctor_id)
            if doctor_contact:
                contacts.append(doctor_contact)
            contacts += self.contacts_lookup.get_receptionists_of_doctor(doctor_id)
            return contacts

        return []
```

### Controller y ruta

`ChatController.get_contacts(current_user_id, role)` → delega a `get_chat_contacts_usecase.execute(...)`.

`app/features/chat/infrastructure/routes/chat_router.py` — nueva ruta:
```python
@router.get("/contacts", response_model=List[ChatUser])
@inject
def get_contacts(
    current_user: UserEntity = Depends(get_current_user),
    controller: ChatController = Depends(Provide[Container.chat_controller])
):
    role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    return controller.get_contacts(current_user.user_id, role)
```

### Wiring (`app/core/containers.py`)

```python
chat_contacts_lookup_adapter = providers.Factory(
    ChatContactsLookupAdapter,
    doctor_repository=doctor_repository,
    receptionist_repository=receptionist_repository,
    patient_repository=patient_repository,
    user_repository=user_repository,
)
get_chat_contacts_use_case = providers.Factory(GetChatContactsUseCase, contacts_lookup=chat_contacts_lookup_adapter)
```
`chat_controller` factory gana un cuarto argumento: `get_chat_contacts_use_case`.

## Testing

- Unit test de `GetChatContactsUseCase` (mock `IChatContactsLookup`): un caso por rol (`doctor`, `recepcionista` con dedupe/exclusión, `paciente`, `admin`/rol desconocido → `[]`).
- Unit test de `ChatContactsLookupAdapter` con mocks de los 4 repos de `users` (verifica el mapeo a `ChatUser`, no la lógica de negocio).
- Test de `UserRepository.get_by_role` (in-memory SQLite aislado, mismo patrón que `test_medical_record_repository.py`): filtra por rol y por `is_active`.
- E2E (`tests/test_chat/test_chat_auth_e2e.py`): un doctor con paciente y recepcionista registrados — verificar que `GET /chat/contacts` devuelve lo esperado para cada uno de los 3 roles registrados (doctor ve a su paciente, recepcionista ve paciente+doctor, paciente ve doctor+recepcionista), más el caso sin auth (401).
