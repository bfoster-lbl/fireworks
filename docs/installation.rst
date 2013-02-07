Basic FireWorks installation
============================

*Currently, we suggest that you install FireWorks in developer mode using the instructions below rather than using pip or easy-install.*

Install required software
-------------------------
To prepare for installation, you should:

1. Install `python 2.7 <http://www.python.org>`_ (preferably Python 2.7.3), if not already packaged with your system.
2. Install `git <http://git-scm.com>`_, if not already packaged with your system. This will allow you to download the latest source code.
3. Install `pip <http://www.pip-installer.org/en/latest/installing.html>`_, if not already packaged with your system. This will allow you to download required dependencies.

.. tip:: if you have easy_install configured, e.g. through `setuptools <http://pypi.python.org/pypi/setuptools>`_, you should be able to install pip using the command 'easy_install pip'

*TODO: write about a potential virtualenv style installation.*

Download FireWorks and dependencies
-----------------------------------
1. Run the following code to download the FireWorks source::

    git clone git@github.com:materialsproject/fireworks.git

2. Navigate inside the FireWorks directory containing the file setup.py::

    cd fireworks

3. run the following command (you might need administrator privileges, so pre-pend the word 'sudo' as needed)::

    python setup.py develop

3. Install the needed dependencies using pip with the following commands (with administrator privileges)::

    pip install nose
    pip install pyyaml
    pip install simplejson
    pip install pymongo

Run unit tests
--------------
1. Staying in the directory containing setup.py, run the following command::

    nosetests
    
2. Ideally, a printout should indicate that all tests have passed. If not, you might try to debug based on the error indicated, or you can let us know the problem so we can improve the docs (see :ref:`contributing-label`).