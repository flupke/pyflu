from louie import Signal


class update_finished(Signal):
    """
    Sent by :class:`~pyflu.update.qt.UpdateDialogMixin` when an update finished
    successfully.

    It receives a single argument, containing the path of the patched files.
    """
