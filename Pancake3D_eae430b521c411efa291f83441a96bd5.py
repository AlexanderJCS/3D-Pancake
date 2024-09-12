"""
Dragonfly plugin made for version 2024.1
"""

__version__ = '1.0.0'

from ORSServiceClass.OrsPlugin.orsPlugin import OrsPlugin
from ORSServiceClass.decorators.infrastructure import menuItem
from ORSServiceClass.actionAndMenu.menu import Menu
from ORSServiceClass.OrsPlugin.uidescriptor import UIDescriptor


class Pancake3D_eae430b521c411efa291f83441a96bd5(OrsPlugin):

    # Plugin definition
    multiple = True
    savable = False
    keepAlive = False
    canBeGenericallyOpened = False

    # UIs
    UIDescriptors = [UIDescriptor(name="MainFormPancake3D",
                                  title="3D Pancake",
                                  dock="Floating",
                                  tab="Main",
                                  modal=False,
                                  collapsible=True,
                                  floatable=True)]

    def __init__(self, varname=None):
        super().__init__(varname)

    @classmethod
    def getMainFormName(cls):
        return "MainFormPancake3D"

    @classmethod
    def getMainFormClass(cls):
        from .mainformpancake3d import MainFormPancake3D
        return MainFormPancake3D

    @classmethod
    def openGUI(cls):
        instance = Pancake3D_eae430b521c411efa291f83441a96bd5()

        if instance is not None:
            instance.openWidget("MainFormPancake3D")

    @classmethod
    @menuItem("Plugins")
    def Pancake3D(cls):
        menu_item = Menu(title="Start 3D Pancake",
                         id_="Pancake3D_eae430b521c411efa291f83441a96bd5_1",
                         section="",
                         action="Pancake3D_eae430b521c411efa291f83441a96bd5.openGUI()")

        return menu_item
