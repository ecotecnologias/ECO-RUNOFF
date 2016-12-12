# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ECORunoff
                                 A QGIS plugin
 This tool automatize surface runoff simulations based on SCS methods
                             -------------------
        begin                : 2016-11-09
        copyright            : (C) 2016 by Jéssica Ribeiro Fontoura, Daniel Allasia, Vitor Geller, Robson Leo Pachaly
        email                : jessica.ribeirofontoura@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load ECORunoff class from file ECORunoff.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .eco_runoff import ECORunoff
    return ECORunoff(iface)
