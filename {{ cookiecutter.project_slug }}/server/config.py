import os
from functools import lru_cache
from typing import Dict, Optional, Type

from .settings.base import Settings as BaseSettings
from .settings.local import Settings as LocalSettings


@lru_cache(maxsize=None)
def get_settings() -> BaseSettings:
    available_settings: Dict[Optional[str], Type[BaseSettings]] = {
        None: LocalSettings,
        "local": LocalSettings,
    }

    gcp_project = os.getenv("GOOGLE_CLOUD_PROJECT")

    return available_settings[gcp_project]()


settings: BaseSettings = get_settings()
