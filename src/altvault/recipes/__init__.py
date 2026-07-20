import importlib
import pkgutil
from typing import NamedTuple, overload

from altvault.recipes.base import Recipe, Tweak
from altvault.steps.manualupload import ManualUploadStep

recipes: dict[str, Recipe] = {}

for _, module_name, is_pkg in pkgutil.iter_modules(__path__):
    if module_name == "base":
        continue
    module = importlib.import_module(f"{__name__}.{module_name}")
    recipe = getattr(module, "recipe", None)
    if isinstance(recipe, Recipe):
        recipes[recipe.name] = recipe


@overload
def get_recipe(*, name: str, bundle_identifier: str | None = None) -> Recipe: ...


@overload
def get_recipe(*, name: str | None = None, bundle_identifier: str) -> Recipe: ...


def get_recipe(
    *, name: str | None = None, bundle_identifier: str | None = None
) -> Recipe:
    if not name and not bundle_identifier:
        raise ValueError("Missing name or bundle_identifier")
    for r in recipes.values():
        if r.name == name or r.bundle_identifier == bundle_identifier:
            return r

    raise LookupError(
        f"App not found: name={name!r}, bundle_identifier={bundle_identifier!r}"
    )


def get_ci_tweak_names() -> list[str]:
    """Tweaks runnable in CI (excludes interactive ManualUploadStep pipelines)."""
    return sorted(
        (
            t.name
            for r in recipes.values()
            for t in r.tweaks
            if not any(isinstance(s, ManualUploadStep) for s in t.pipeline)
        ),
        key=str.casefold,
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
