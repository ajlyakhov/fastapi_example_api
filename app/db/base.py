from abc import ABC, abstractmethod

from app.api.models import TrackingItem


class DatabaseProvider(ABC):
    """Abstract base class for database providers."""

    @abstractmethod
    def get_tracking_item(self, tracking_number: str, carrier: str) -> TrackingItem | None:
        pass
