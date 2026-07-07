import pytest
from unittest.mock import MagicMock

# E2E del flujo social por cluster: evaluacion de riesgo (ML mockeado) propaga el
# cluster al perfil social, y los endpoints /recommended filtran posts y grupos
# por el cluster de la usuaria autenticada, con fallback al contenido global.


@pytest.mark.integration
def test_cluster_flow_de_evaluacion_a_recomendaciones(client, app):
    def _register_patient(name, email, doctor_id):
        resp = client.post(
            "/api/v1/patients/register",
            json={
                "name": name,
                "last_name": "Social",
                "email": email,
                "password": "secret123",
                "role": "paciente",
                "birthdate": "1995-04-10",
                "doctor_id": doctor_id,
            },
        )
        assert resp.status_code == 201, resp.text
        return resp.json()

    def _token(email):
        resp = client.post("/api/v1/users/login", json={"email": email, "password": "secret123"})
        assert resp.status_code == 200, resp.text
        return {"Authorization": f"Bearer {resp.json()['access_token']}"}

    doctor_resp = client.post(
        "/api/v1/doctors/register",
        json={
            "name": "Dra", "last_name": "Cluster", "email": "dra.cluster@test.com",
            "password": "secret123", "role": "doctor",
            "professional_license": "LIC-777", "specialty": "Obstetricia",
        },
    )
    assert doctor_resp.status_code == 201, doctor_resp.text
    doctor_id = doctor_resp.json()["doctor_id"]

    ana = _register_patient("Ana", "ana.cluster@test.com", doctor_id)
    bea = _register_patient("Bea", "bea.cluster@test.com", doctor_id)

    record_resp = client.post(
        "/api/v1/medical-records/",
        json={
            "patient_id": ana["patient_id"], "doctor_id": doctor_id,
            "height_cm": 160, "initial_weight": 60.5,
            "initial_systolic": 118, "initial_diastolic": 76,
        },
    )
    assert record_resp.status_code == 201, record_resp.text
    medical_record_id = record_resp.json()["medical_record_id"]

    # Perfil creado ANTES de evaluar: sin prediccion todavia -> cluster null
    profile_resp = client.post("/api/v1/forums/profiles", json={"user_id": ana["user_id"], "alias": "ana"})
    assert profile_resp.status_code == 201, profile_resp.text
    assert profile_resp.json()["cluster_profile"] is None

    # Bea (otro cluster) via ML mockeado tambien tendra perfil
    client.post("/api/v1/forums/profiles", json={"user_id": bea["user_id"], "alias": "bea"})

    # Evaluacion con ML mockeado -> cluster 3 (riesgo metabolico)
    ml_mock = MagicMock()
    ml_mock.predict.return_value = {"risk_cluster": 3, "diagnosis": "Riesgo Metabolico"}
    with app.container.ml_prediction_service.override(ml_mock):
        eval_resp = client.post(
            f"/api/v1/medical-records/{medical_record_id}/risk-evaluation",
            headers=_token("dra.cluster@test.com"),
        )
    assert eval_resp.status_code == 201, eval_resp.text
    assert eval_resp.json()["status"] == "ok"

    # El cluster quedo propagado al perfil social de Ana
    perfil = client.get(f"/api/v1/forums/profiles/{ana['user_id']}")
    assert perfil.json()["cluster_profile"] == "3"

    # Posts: Ana (cluster 3) y Bea (sin cluster)
    client.post("/api/v1/forums/posts", json={"author_id": ana["user_id"], "title": "Mi dia a dia bajando de peso", "content": "..."})
    client.post("/api/v1/forums/posts", json={"author_id": bea["user_id"], "title": "Post de otro perfil", "content": "..."})

    # Grupos: uno etiquetado con el cluster 3 y uno general
    client.post("/api/v1/forums/groups", json={"name": "Control de peso en el embarazo", "created_by": ana["user_id"], "cluster_tag": "3"})
    client.post("/api/v1/forums/groups", json={"name": "General", "created_by": bea["user_id"]})

    # Sin token -> 401
    assert client.get("/api/v1/forums/posts/recommended").status_code == 401
    assert client.get("/api/v1/forums/groups/recommended").status_code == 401

    ana_headers = _token("ana.cluster@test.com")

    feed = client.get("/api/v1/forums/posts/recommended", headers=ana_headers)
    assert feed.status_code == 200, feed.text
    assert [p["title"] for p in feed.json()] == ["Mi dia a dia bajando de peso"]

    grupos = client.get("/api/v1/forums/groups/recommended", headers=ana_headers)
    assert grupos.status_code == 200, grupos.text
    assert [g["name"] for g in grupos.json()] == ["Control de peso en el embarazo"]

    # Bea no tiene cluster -> fallback: feed global y todos los grupos
    bea_headers = _token("bea.cluster@test.com")
    feed_bea = client.get("/api/v1/forums/posts/recommended", headers=bea_headers)
    assert len(feed_bea.json()) == 2
    grupos_bea = client.get("/api/v1/forums/groups/recommended", headers=bea_headers)
    assert len(grupos_bea.json()) == 2

    # --- Publicidad de doctores intercalada ---
    # Un doctor necesita perfil social para autorar posts; el gating es por rol.
    doctor_user_id = doctor_resp.json()["user_id"]
    client.post("/api/v1/forums/profiles", json={"user_id": doctor_user_id, "alias": "dra"})

    # Paciente NO puede marcar is_ad -> 400
    ana_ad = client.post(
        "/api/v1/forums/posts",
        json={"author_id": ana["user_id"], "title": "spam", "content": "x", "is_ad": True},
    )
    assert ana_ad.status_code == 400, ana_ad.text

    # Doctor SÍ puede publicar publicidad
    doc_ad = client.post(
        "/api/v1/forums/posts",
        json={"author_id": doctor_user_id, "title": "Consultorio Dra Cluster", "content": "Agenda tu cita", "is_ad": True},
    )
    assert doc_ad.status_code == 201, doc_ad.text
    assert doc_ad.json()["is_ad"] is True

    # El anuncio aparece intercalado en el feed de la paciente, marcado is_ad
    feed_con_ad = client.get("/api/v1/forums/posts/recommended", headers=ana_headers).json()
    anuncios = [p for p in feed_con_ad if p["is_ad"]]
    assert [a["title"] for a in anuncios] == ["Consultorio Dra Cluster"]
    # el post normal del cluster sigue presente y NO marcado como anuncio
    assert any(p["title"] == "Mi dia a dia bajando de peso" and not p["is_ad"] for p in feed_con_ad)
