from typing import List

def interleave(posts: list, ads: list, every: int = 4) -> list:
    """Intercala anuncios en el stream de posts normales: un anuncio despues de
    cada `every` posts, hasta agotar los anuncios disponibles. No inyecta nada si
    no hay posts. Funcion pura, sin dependencias de dominio."""
    if not posts or not ads:
        return list(posts)

    result: List = []
    ad_iter = iter(ads)
    next_ad = next(ad_iter, None)

    for i, post in enumerate(posts, start=1):
        result.append(post)
        if next_ad is not None and i % every == 0:
            result.append(next_ad)
            next_ad = next(ad_iter, None)

    # Bloque final parcial (feed no multiplo de `every`): un anuncio al cierre,
    # para que la publicidad tambien aparezca en feeds cortos.
    if next_ad is not None and len(posts) % every != 0:
        result.append(next_ad)

    return result
