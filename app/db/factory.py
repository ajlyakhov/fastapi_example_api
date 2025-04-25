from app.db.base import DatabaseProvider
from app.db.dynamodb import DatabaseDynamoDb


class DatabaseFactory:
    @staticmethod
    def get_provider(provider_name: str) -> DatabaseProvider:
        """Using "Strategy" pattern allows us to use multiple DB engines with easy switching
        :param provider_name: name of DB provider
        :return: specific DatabaseProvider instance
        """
        providers = {
            "dynamodb": DatabaseDynamoDb,
        }
        if provider_name not in providers:
            raise ValueError(f"Unknown provider: {provider_name}")
        return providers[provider_name]()
