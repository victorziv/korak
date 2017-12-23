Standalone Tests
----------------

The standalone tests can not ride on the existent Infinibox automation infrastructure.
The reason is they must to take the Ibox system out of ACTIVE state, which is not tolerated by the infra.


Fiber Channel Loopback Testing
..............................

.. automodule:: tests.ibox_system.test_fcloopback

.. autoclass:: TestFCLoopback(Test)
    :members: test_fcloopback
