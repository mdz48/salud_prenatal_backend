from datetime import date

from app.features.users.domain.pregnancy_calculations import age_years, gestational_weeks


class TestGestationalWeeks:
    def test_calcula_desde_ultimo_periodo(self):
        assert gestational_weeks(date(2026, 1, 1), None, today=date(2026, 3, 12)) == 10

    def test_sin_periodo_usa_semanas_de_registro(self):
        assert gestational_weeks(None, 8, today=date(2026, 3, 12)) == 8

    def test_sin_datos_devuelve_none(self):
        assert gestational_weeks(None, None) is None

    def test_periodo_tiene_prioridad_sobre_registro(self):
        assert gestational_weeks(date(2026, 3, 5), 20, today=date(2026, 3, 12)) == 1


class TestAgeYears:
    def test_cumpleanos_ya_paso(self):
        assert age_years(date(1995, 4, 10), today=date(2026, 7, 4)) == 31

    def test_cumpleanos_no_llega(self):
        assert age_years(date(1995, 12, 25), today=date(2026, 7, 4)) == 30

    def test_cumpleanos_exacto(self):
        assert age_years(date(1995, 7, 4), today=date(2026, 7, 4)) == 31

    def test_sin_birthdate_devuelve_none(self):
        assert age_years(None) is None
