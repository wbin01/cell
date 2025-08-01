#/usr/bin/env python3
from ..base import Layout
from ...enum.orientation import Orientation


class Row(Layout):
    """Row layout object.

    Organizes elements side by side like a row.
    """
    def __init__(
            self, orientation: Orientation = Orientation.HORIZONTAL,
            *args, **kwargs) -> None:
        super().__init__(orientation=orientation, *args, **kwargs)
        self._element_type = 'Row'

    def __str__(self):
        return "<class 'Row'>"
