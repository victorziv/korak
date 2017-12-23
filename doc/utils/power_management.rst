Power management utils
======================

.. automodule:: ivt.utils.power_management

ATS power management
--------------------

ATS switch
..........

.. autoclass:: ATSSwitch
    :members: off, on, reboot


BBUs power management
---------------------

BBU charging
............

.. autofunction:: check_bbus_are_charging


.. autofunction:: check_bbus_are_fully_charged


.. autofunction:: get_bbus_charge_state


.. autofunction:: wait_for_bbus_fully_charged


BBU outlets
...........

.. autofunction:: check_bbu_outlets_status

BBU switch
..........

.. autoclass:: BBUSwitch
    :members: off, on


Enclosures power management
---------------------------

Enclosure switch
................

.. autoclass:: EnclosureSwitch
    :members: off, on, reboot

Node PSU management
-------------------

.. autofunction:: wait_for_node_psu_current_draw

PDUs power management
---------------------

PDUs switch off
..............

.. autofunction:: turn_pdu_off

PDUs switch on
..............

.. autofunction:: turn_pdu_on
