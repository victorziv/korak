InfiniSDK Usage How To
======================

|InfiniSDK| is Infinidat’s Official Python SDK for interacting with Infinidat storage products.
InfiniSDK is widely used by IVT automatic tests, utilites and tools.

Following are a couple of usage clarifications and how-to examples.

Obtaining Infinibox system-under-test object
............................................

The object is obtained and returned by *fxsystem* fixture function in *test/fixtures/component_fixtures.py* fixtures module.

Then **fxsystem** object can be passed as a parameter to any test function or method.

.. code-block:: python

    def test_system_under_test(fxsystem):
        # run some validations on fxsystem        


Accessing nodes 
...............

Nodes object for the system can be obtained as

    `fxsystem.components.nodes`

An individual node object can be fetched by an index.
Here is an example:

.. code-block:: python

    def test_node1_for_something(fxsystem):
        nodes = fxsystem.components.nodes
        node1 = nodes.get(index=1)
        ...

The node object in turn provides a number of useful methods and attributes:

   - `node.is_active()`
   - `node.get_fc_ports()`
   - `node.get_drives()`
   ...


.. |InfiniSDK| raw:: html

    <a href="http://infraweb/devdocs/infradev/infinisdk/" target="_blank">InfiniSDK</a>


    
