IVT Utils
=========

Automation utilities is a Python library which both automatic tests and tools can use.

For convenience the library modules are somehow loosely categorized by the type of functionality and placed under appropriate file hierarchy.
For example, power management related functions can be found in the modules under *ivt/utils/power_management/* directory, modules responsible 
for Infinibox system inventory and manipulations go under *ivt/utils/ibox_system* and so on.

Note though that all exported functions and classes are pre-loaded in **ivt.utils** package ( *ivt/utils/__init__.py* file )
and can be imported by a test or a tool from there without needing to know exactly which category the utility module belongs to.

.. code-block:: python
    
    from ivt.utils import set_pdu_reboot_delay
    ...

.. toctree::
    :maxdepth: 2

    utils/ibox_system
    utils/ibox_drives
    utils/power_management
    utils/fcport_management
    
