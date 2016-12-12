# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ECORunoffDialog
                                 A QGIS plugin
 This tool automatize surface runoff simulations based on SCS methods
                             -------------------
        begin                : 2016-11-09
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Jéssica Ribeiro Fontoura, Daniel Allasia, Vitor Geller, Robson Leo Pachaly
        email                : jessica.ribeirofontoura@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from PyQt4 import QtGui, uic

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'eco_runoff_dialog_base.ui'))


class ECORunoffDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(ECORunoffDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
