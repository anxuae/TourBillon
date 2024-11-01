|PythonVersions| |PypiPackage| |Downloads| |Pylint| |Tests| |Codecov|
::

        oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
        o ---------------------------------------------------------------------------- o
        o |                                                                          | o
        o |    oTTTo                                                                 | o
        o    oTTTo                                                                   | o
           oTTTo#&  ////                                                             | o
         oTTTo& #&//////                     BBBBBBB                                 | o
       oTTTo #& //////                       BB     BB       LL  LL                  | o
          #& #&/////                         BB      BB      LL  LL                  | o
          #&/#&//&                           BB      BB      LL  LL                  | o
         /#&/#& #&                           BB     BB   OO  LL  LL                  | o
       ///#& #& #&                           BBBBBBBB        LL  LL                  | o
     ///  #& #& #&   OOOO   UU  UU  RR RRR   BB     BB   II  LL  LL   OOOO   N NNNN  | o
   //     #& #& #&  OO  OO  UU  UU  RRR  RR  BB      BB  II  LL  LL  OO  OO  NNN NN  | o
  o       #& #& #&  OO  OO  UU  UU  RR       BB      BB  II  LL  LL  OO  OO  NN  NN  | o
          #& #& #&  OO  OO  UU  UU  RR       BB     BB   II  LL  LL  OO  OO  NN  NN  | o
          #& #& #&   OOOO    UUUU   RR       BBBBBBB     II  LL  LL   OOOO   NN  NN  | o
          #& #&                                                                      | o
          #& #&    ------------------------------------------------------------------- o
          #&     ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
          #&                                              Version 6.0.0 © La Billonnière


TourBillon
==========

Tourbillon is free software (distributed under LPG license) which makes it possible to organize the
`Billons tournaments <https://www.facebook.com/labillonniere>`_.
This software is a **Swiss-style Tournament Manager** for teams of one or more player(s).

Swiss-style tournaments generally have three rules:
 - Teams are paired with opponents who have similar scores.
 - Teams cannot play the same opponent twice.
 - Teams are never eliminated.

The winner is the team with the highest aggregate points earned in all rounds.

From 32 to 64 teams, it is recomended to perform between 5 and 6 rounds per tournament.


Dependencies
============

* Python >= 3.8 (mandatory)
* PyYaml >= 5.0 (mandatory)
* WxPython >= 4.0 (optional: used for `standelone` mode)
* fastapi >= 0.111.1 (optional: used for `server` mode)


Install
=======

Download the binaries corresponding to your operating system from the page
`releases <https://github.com/anxuae/tourbillon-gui/releases>`_

Or install from the source downloaded on Github ::

    $ pip install poetry
    $ poetry install


Quick start
===========

Tourbillon settles and is used in a jiffy. Two interfaces are possible:

To start the `standelone` mode, run::

    $ poetry run tourbillon

To start the `server` mode, run::

    $ poetry run tourbillon --backend

And now it turns! Note that in `server` mode, Tourbillon runs by
default on port 59290.


.. |PythonVersions| image:: https://img.shields.io/badge/python-3.8+-red.svg
   :target: https://www.python.org/downloads
   :alt: Python 3.8+

.. |PypiPackage| image:: https://badge.fury.io/py/tourbillon.svg
   :target: https://pypi.org/project/tourbillon
   :alt: PyPi package

.. |Downloads| image:: https://img.shields.io/pypi/dm/tourbillon?color=purple
   :target: https://pypi.org/project/tourbillon
   :alt: PyPi downloads

.. |Pylint| image:: https://github.com/anxuae/TourBillon/actions/runs/10316603069/artifacts/1794212304/pylint/badge.svg
   :target: https://github.com/anxuae/TourBillon/actions/workflows/pylint.yml
   :alt: Pylint

.. |Tests| image:: https://github.com/anxuae/TourBillon/actions/workflows/tests.yml/badge.svg
   :target: https://github.com/anxuae/TourBillon/actions/workflows/tests.yml
   :alt: Tests

.. |Codecov| image:: https://codecov.io/gh/anxuae/TourBillon/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/anxuae/TourBillon
    :alt: Codecov
