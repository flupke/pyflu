"""
QGraphics* utilities.
"""

from PyQt4.QtGui import QGraphicsItem, QTransform


def scene_bbox(item, view=None):
    """
    Returns the bounding box of an item in scene space.

    If view is given and the object has the
    QGraphicsItem::ItemIgnoresTransformations flag set, additional steps are
    taken to compute the exact bounding box of the item.
    """
    bbox = item.boundingRect()
    if not (item.flags() & QGraphicsItem.ItemIgnoresTransformations):
        # Normal item, simply map its bounding box to scene space
        bbox = item.mapRectToScene(bbox)
    else:
        # Item with the ItemIgnoresTransformations flag, need to compute its
        # bounding box with deviceTransform()
        if view is not None:
            vp_trans = view.viewportTransform()
        else:
            vp_trans = QTransform()
        item_to_vp_trans = item.deviceTransform(vp_trans)
        # Map bbox to viewport space
        bbox = item_to_vp_trans.mapRect(bbox)
        # Map bbox back to scene space
        bbox = vp_trans.inverted()[0].mapRect(bbox)
    return bbox                    
