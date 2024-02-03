"""Module of Deal Class"""
from ..api import EIDeal

class Deal(EIDeal):
    """Implementation of EIDeal"""
    def as_dict(self) -> dict:
        """Return deal as dictionary"""
        return {'id': self.id, 'symbol': self.symbol.value, 'datetime': self.datetime,
                'type': self.type.name, 'volume': self.volume, 'price': self.price}
