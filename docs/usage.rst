Usage
=====

.. _installation:

Installation
------------

To use NFS volumes, first install it from docker hub:

.. code-block:: console
   docker plugin install francoisjn/nfs-volumes

Configure the plugin by setting the following environment variables:

.. code-block:: console
   docker plugin set francoisjn/nfs-volumes NFS_MOUNT="<server_address>:<remote_path> [NFS mount options] [;<other_server_addresses>:<remote_paths>; ...]"
Remember to replace ``<server_address>`` and ``<remote_path>`` with the appropriate values.

For options check https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/8/html/managing_file_systems/mounting-nfs-shares_managing-file-systems#frequently-used-nfs-mount-options_mounting-nfs-shares

Finally, enable the plugin:

.. code-block:: console
   docker plugin enable francoisjn/nfs-volumes

Repeat the above steps on all the hosts that will use the plugin.

Using volumes
----------------

To use the plugin, you can create a volume with the following command:

.. code-block:: console
   docker volume create -d francoisjn/nfs-volumes <volume_name>

You may also want to specify how to choose the server that will host your volume.

There are different strategies to choose the server:

- `selected`: Allows you to specify the server that will host the volume, using `-o drive=<storage>`
    - `storage` is the server address that will host the volume, with the path, `/` replaced by '_'.
        example: `storage1.example.com:/path/to/volume` becomes `storage1.example.com:_path_to_volume`
- `lowest_usage`: Selects the server with the lowest usage.
- `highest_space`: Selects the server with the most available space.
- `lowest_percentage`: Selects the server with the lowest percentage of used space.

You can specify the strategy when creating the volume:

.. code-block:: console
   docker volume create -d francoisjn -o drive_selector=<selector_name> <volume_name>

For other , you can use plugins' volumes as any other.
.. warning::
    Deletions will be effective on all hosts, so be careful when deleting volumes.