from dependency_injector import containers, providers
from src.infrastructure.config.settings import Settings


class Container(containers.DeclarativeContainer):
    config = providers.Singleton(Settings)


container = Container()
