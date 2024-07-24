Common problems
===============

Error response from daemon: dial unix /var/run/docker.sock: connect: no such file or directory
------------------------------------------------------------------------------------------------

This error may be raised on enable when the plugin is unable to mount one of the provided NFS servers. Check the server address and the network connection.

.. note::

Be careful to configure the correct path of the NFS during :ref:`installation`.


Error 30
--------

This error is raised when the plugin is unable to write to the NFS server.

