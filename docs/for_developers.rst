Developers Guide
================

This guide is intended for developers who want to contribute to the project. It covers the following topics:

- How to set up the development environment
- How to run the tests
- How to build and publish the project
- How to debug the plugin

Requirements
------------
- Docker
- Docker Compose
- Python
- Pip
- Git
- Make

Setting up the development environment
--------------------------------------

1. Install the dependencies:

.. code-block:: console

    pip install -r requirements-dev.txt

2. Configure the environment variables in the Makefile:

- PLUGIN_NAME: The name of the plugin
- PLUGIN_TAG: The tag of the plugin

.. note::
    Plugin will be published on dockerhub with the name ``PLUGIN_NAME``, make sure you're allowed to publish it (mandatory for tests).

3. Connect to dockerhub:

.. code-block:: console

    docker login

Running the tests
-----------------

1. Publish test version of the plugin:

.. code-block:: console

    make publish PLUGIN_TAG=test

2. To run the tests, execute the following command:

.. code-block:: console

    make test

Building the project
--------------------

.. note::
    The plugin will be built with the name ``PLUGIN_NAME`` and the tag ``PLUGIN_TAG``.

To build the project, execute the following command:

.. code-block:: console

    make build

To publish the plugin, execute the following command:

.. code-block:: console

    make publish

.. note::
    The plugin will be published on dockerhub with the name ``PLUGIN_NAME``, make sure you're allowed to publish it.

To install locally the plugin, execute the following command:

.. code-block:: console

    make all

.. note::
    ``publish`` and ``all`` commands will automatically build the plugin it.

Debugging the plugin
--------------------

You can get plugin's and docker daemon's logs respectively with the following commands:

.. code-block:: console

    make log_plugin

.. code-block:: console

    make log_dockerd

.. note::
    Plugin's logs during tests in DinD will be available under ``/tests/logs`` directory.