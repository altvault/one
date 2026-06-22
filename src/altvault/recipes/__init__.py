from typing import NamedTuple

from altvault.recipes import (
    apollo,
    facebook,
    infuse,
    instagram,
    x,
    youtube,
    youtubemusic,
)
from altvault.recipes.base import Recipe, Tweak

recipes: dict[str, Recipe] = {}

recipes[apollo.recipe.name] = apollo.recipe
recipes[facebook.recipe.name] = facebook.recipe
recipes[infuse.recipe.name] = infuse.recipe
recipes[instagram.recipe.name] = instagram.recipe
recipes[x.recipe.name] = x.recipe
recipes[youtube.recipe.name] = youtube.recipe
recipes[youtubemusic.recipe.name] = youtubemusic.recipe


def get_recipe(name: str | None, bundle_identifier: str | None) -> Recipe:
    if not name and not bundle_identifier:
        raise ValueError("Missing name or bundle_identifier")
    for r in recipes.values():
        if r.name == name or r.bundle_identifier == bundle_identifier:
            return r

    raise LookupError(
        f"App not found: name={name!r}, bundle_identifier={bundle_identifier!r}"
    )


class AppAndTweak(NamedTuple):
    app: Recipe
    tweak: Tweak


def get_tweak_recipe(name: str) -> AppAndTweak:
    if not name:
        raise ValueError("Missing name")

    for r in recipes.values():
        for t in r.tweaks:
            if t.name == name:
                return AppAndTweak(app=r, tweak=t)

    raise LookupError(f"Tweak not found: name={name!r}")
