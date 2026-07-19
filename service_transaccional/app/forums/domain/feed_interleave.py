from typing import List

def interleave(posts: list, ads: list, every: int = 4) -> list:
    """Intercala anuncios en el stream de posts normales: un anuncio despues de
    cada `every` posts. Los anuncios que no alcanzaron un hueco (mas ads que
    posts, o feed corto) se agregan al final, para que NINGUN anuncio se
    descarte. Los ads no dependen de los posts: sin posts normales, se muestran
    todos los anuncios. Funcion pura, sin dependencias de dominio."""
    if not ads:
        return list(posts)

    result: List = []
    ad_iter = iter(ads)
    next_ad = next(ad_iter, None)

    for i, post in enumerate(posts, start=1):
        result.append(post)
        if next_ad is not None and i % every == 0:
            result.append(next_ad)
            next_ad = next(ad_iter, None)

    # Sobrantes: todos los anuncios que no cayeron en un hueco van al final.
    while next_ad is not None:
        result.append(next_ad)
        next_ad = next(ad_iter, None)

    return result
