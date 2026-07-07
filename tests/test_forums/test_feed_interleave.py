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


def test_posts_vacio_no_inyecta_anuncios():
    assert interleave([], ["a1", "a2"], every=2) == []


def test_more_ads_than_slots_solo_usa_los_que_caben():
    posts = ["p1", "p2"]
    ads = ["a1", "a2", "a3"]

    result = interleave(posts, ads, every=2)

    # solo hay un hueco (tras p2)
    assert result == ["p1", "p2", "a1"]


def test_feed_mas_corto_que_intervalo_igual_muestra_un_ad():
    # feed corto (1 post) con every=4: el anuncio debe aparecer al final,
    # si no, en feeds cortos la publicidad nunca se veria.
    result = interleave(["p1"], ["a1"], every=4)

    assert result == ["p1", "a1"]
