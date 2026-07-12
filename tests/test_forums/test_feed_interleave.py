from app.features.forums.domain.feed_interleave import interleave


def test_sin_anuncios_devuelve_posts_tal_cual():
    posts = [1, 2, 3]
    assert interleave(posts, [], every=2) == [1, 2, 3]


def test_intercala_un_anuncio_cada_n_posts():
    posts = ["p1", "p2", "p3", "p4", "p5", "p6"]
    ads = ["a1", "a2"]

    result = interleave(posts, ads, every=2)

    # un ad tras cada 2 posts normales, hasta agotar ads
    assert result == ["p1", "p2", "a1", "p3", "p4", "a2", "p5", "p6"]


def test_menos_anuncios_que_huecos_no_falla():
    posts = ["p1", "p2", "p3", "p4"]
    ads = ["a1"]

    result = interleave(posts, ads, every=2)

    assert result == ["p1", "p2", "a1", "p3", "p4"]


def test_posts_vacio_muestra_solo_los_anuncios():
    # Los ads NO dependen de los posts: sin posts normales, igual se muestran.
    assert interleave([], ["a1", "a2"], every=2) == ["a1", "a2"]


def test_ads_sobrantes_van_al_final():
    # Mas ads que huecos: el que cae en el hueco se intercala, el resto se
    # agrega al final. Ningun anuncio se descarta.
    posts = ["p1", "p2"]
    ads = ["a1", "a2", "a3"]

    result = interleave(posts, ads, every=2)

    assert result == ["p1", "p2", "a1", "a2", "a3"]


def test_todos_los_ads_aparecen_con_intervalo_4():
    # 4 posts, 4 ads, every=4: 1 ad en el hueco (tras el 4o post) y los 3
    # restantes al final. Reproduce el caso real reportado en produccion.
    posts = ["p1", "p2", "p3", "p4"]
    ads = ["a1", "a2", "a3", "a4"]

    result = interleave(posts, ads, every=4)

    assert result == ["p1", "p2", "p3", "p4", "a1", "a2", "a3", "a4"]


def test_feed_mas_corto_que_intervalo_igual_muestra_los_ads():
    # feed corto (1 post) con every=4: los anuncios aparecen al final,
    # si no, en feeds cortos la publicidad nunca se veria.
    result = interleave(["p1"], ["a1", "a2"], every=4)

    assert result == ["p1", "a1", "a2"]
