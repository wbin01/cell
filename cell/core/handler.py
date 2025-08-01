#/usr/bin/env python3
from PySide6 import QtCore, QtQuick

from .tools import change_element_style_state
from ..enum import Event, FrameState
from ..ui.base import Element, Frame, Layout
from ..ui.frame import MainFrame


class Handler(QtCore.QObject):
    """Handles QML UI integration with Frame graphical elements.

    Retrieves the graphic elements from the Frame and integrates them with the 
    initial UI elements, and then sets the style of the elements and the Frame 
    in each state.
    """

    def __init__(
            self, gui: QtQuick.QQuickWindow = None, ui: MainFrame = None
            ) -> None:
        """The init receives a QML-based UI and the app's Frame.

        :param gui: QML based UI.
        :param ui: The app's Frame.
        """
        super().__init__()
        self.__gui = gui
        self.__ui = ui
        self.__main_rect = self.__gui.findChild(QtCore.QObject, 'mainRect')
        self.__elements = self.__main_rect.findChildren(
            QtCore.QObject, options=QtCore.Qt.FindChildrenRecursively)

        self.__gui.windowStateChanged.connect(self.__state_changed)
        self.__state_style()
        self.__integrate_graphic_elements(self.__ui)

    @QtCore.Slot()
    def __element_clicked(self) -> None:
        # Elements clicked state colors (ignored for now).
        if not self.__main_rect.property('isActive'):
            return

    @QtCore.Slot()
    def __element_pressed(self, element: QtQuick.QQuickItem) -> None:
        # Elements pressed state colors.
        if not self.__main_rect.property('isActive'):
            return

        change_element_style_state(element, ':clicked', self.__ui.style)

    @QtCore.Slot()
    def __element_hover(self, element: QtQuick.QQuickItem) -> None:
        # Elements hover state colors.
        is_active = self.__main_rect.property('isActive')

        if element.property('hovered'):
            state = ':hover' if is_active else ':inactive'
        else:
            state = '' if is_active else ':inactive'

        change_element_style_state(element, state, self.__ui.style)

    def __integrate_graphic_elements(self, layout) -> None:
        # Integration Frame graphic elements into the MainFrame UI.
        for attr, value in layout.__dict__.items():
            if attr.startswith('_') and '__' in attr:
                continue

            element = getattr(layout, attr)
            obj_value = self.__gui.findChild(QtCore.QObject, attr)
            if not obj_value:
                continue
            element._obj = obj_value

            if isinstance(element, Layout):
                self.__integrate_graphic_elements(element)
            
            elif isinstance(element, Element):
                if hasattr(element, 'callbacks'):
                    callbacks = element.callbacks()

                    if Event.MOUSE_PRESS in callbacks:
                        element.connect(
                            callbacks[Event.MOUSE_PRESS], Event.MOUSE_PRESS)
                    elif Event.MOUSE_HOVER in callbacks:
                        element.connect(
                            callbacks[Event.MOUSE_HOVER], Event.MOUSE_HOVER)

        if isinstance(layout, Frame):
            layout._obj = self.__gui

    def __state_style(self) -> None:
        # Style of the elements and the Frame in each state.
        if self.__ui.frame_state == FrameState.MAXIMIZED:
            self.__main_rect.setProperty('radius', 0)
            self.__main_rect.setProperty('borderWidth', 0)
            self.__main_rect.setProperty('margins', 0)
        else:
            self.__main_rect.setProperty(
                'radius', self.__ui.style['[MainFrame]']['border_radius'])
            self.__main_rect.setProperty('borderWidth', 1)
            self.__main_rect.setProperty('margins', 1)

        for child in self.__elements:
            if not child.property('qmlType'):
                continue
            
            if getattr(child, 'clicked', None):
                child.clicked.connect(self.__element_clicked)
            if getattr(child, 'hoveredChanged', None):
                child.hoveredChanged.connect(
                    lambda child=child: self.__element_hover(child))
            if getattr(child, 'pressed', None):
                child.pressed.connect(
                    lambda child=child: self.__element_pressed(child))
            if getattr(child, 'released', None):
                child.released.connect(
                    lambda child=child: self.__element_hover(child))

    @QtCore.Slot()
    def __state_changed(self, state: QtCore.Qt.WindowState) -> None:
        # Frame style in full-screen or normal-screen states.
        if self.__main_rect:
            if (state == QtCore.Qt.WindowFullScreen
                    or state == QtCore.Qt.WindowMaximized):
                self.__main_rect.setProperty('radius', 0)
                self.__main_rect.setProperty('borderWidth', 0)
                self.__main_rect.setProperty('margins', 0)
            else:  # QtCore.Qt.WindowNoState
                self.__main_rect.setProperty(
                    'radius', self.__ui.style['[MainFrame]']['border_radius'])
                self.__main_rect.setProperty('borderWidth', 1)
                self.__main_rect.setProperty('margins', 1)

    @QtCore.Slot()
    def start_move(self) -> None:
        """Move the apps Frame natively in CSD mode.

        Qt internal method to use native system movement when dragging/moving 
        the application Frame.
        """
        self.__gui.startSystemMove()

    @QtCore.Slot(int)
    def start_resize(self, edge: int) -> None:
        """Resize the app Frame natively in CSD mode.

        Qt's built-in method to use native system resizing in the apps Frame.
        """
        edge = QtCore.Qt.Edge(edge)
        self.__gui.startSystemResize(edge)

    def __str__(self):
        return "<class 'Handler'>"
