from abc import ABC, abstractmethod
from typing import Dict, Any, List, Callable, Optional
from django.http import HttpRequest


class BaseContextBuilder(ABC):
    def __init__(
        self,
        request: HttpRequest,
        base_context: Dict[str, Any] = None,
        **kwargs
    ):
        self.request = request
        self.context = base_context or {}
        self.extra_data = kwargs
        self._processors: List[Callable] = self._get_default_processors()

    def _get_default_processors(self) -> List[Callable]:
        return []

    @abstractmethod
    def get_base_data(self) -> Dict[str, Any]:
        pass

    def build(self) -> Dict[str, Any]:
        self.context.update(self.get_base_data())

        for processor in self._processors:
            processor()

        return self.context
