from abc import ABC, abstractmethod


class BaseStorage(ABC):
    @abstractmethod
    def get_container(self):
        pass

    @abstractmethod
    def mark_modified(self):
        pass


class SessionStorage(BaseStorage):
    def __init__(self, session):
        self.session = session

    def get_container(self):
        return self.session.setdefault("cart", {"items": {}})

    def mark_modified(self):
        self.session.modified = True
