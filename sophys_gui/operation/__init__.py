"""
    The Sophys GUI is designed for controlling and monitoring the results of a Bluesky
    scan using a Queue Server.

    .. image:: ./_static/sophys_gui.png
        :width: 500
        :alt: Sophys GUI
        :align: center


    How to access it
    ================

    You can access this GUI with a command in the terminal.

    .. code-block:: python
        :linenos:

        sophys-gui --http-server HTTP_SERVER_IP  --kafka-bootstrap KAFKA_IP --kafka-topic KAFKA_TOPIC

    .. attention::
        You need to login in order to control the Run Engine or the Queue.
        If you are not logged in, you will only be able to monitor them.

"""

from .main import SophysOperationGUI
