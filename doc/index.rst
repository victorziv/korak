IVT Automation
==============


.. |Infinidat_TM| unicode:: Infinidat U+2122

.. |automation_infrastructure| raw:: html

    <a href="http://infraweb/docs/tutorial/" target="_blank">automation infrastructure</a>

.. |ivt_tests| raw:: html

    <a href="https://vziv@git.infinidat.com/ivt/ivt-tests.git" target="_blank">ivt-tests</a>

This is documentation for |Infinidat_TM| IVT Automation development and procedures.

All IVT automation code is now gathered under |ivt_tests| repository on *git.infinidat.com* server
and includes the following components:

- IVT  automatic tests that ride on the common |automation_infrastructure|. 
  The tests code is committed under *tests/* directory.

- A collection of scripts coded in Bash and Python is placed under *tools/* directory.

- Re-usable functionality for both tests and tools is provided  by IVT related infrastructure modules. 
  They are developed by the team and committed under *ivt/utils* directory. 


Table Of Contents
-----------------

.. toctree::
    :maxdepth: 1
    
   sdk_usage
   tests
   utils


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
