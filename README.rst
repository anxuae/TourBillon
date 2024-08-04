
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

TourBillon est un logiciel libre (distribué sous licence GPL) qui permet d'organiser les
tournois de billons. Tourbillon s'installe et s'utilise en un tour de main, deux interfaces
sont possibles: "standalone" (par defaut) ou "backend" (server HTTP RESTful).


Dépendances
===========

* Python >= 3.8 (requis)
* PyYaml >= 5.0 (requis)
* WxPython >= 4.0 (optionel: mode "standalone")
* fastapi >= 0.111.1 (optionel: mode "serveur")


Installation
============

Télécharger les binaires correspondant à votre système d'exploitation depuis la page
`releases <https://github.com/anxuae/tourbillon-gui/releases>`_ 

Ou installer depuis le dossier source téléchargé sur GitHub::

    $ pip install poetry
    $ poetry install


Démarrage rapide
================

Pour une utilisation `standelone`, lancer::

    $ poetry run tourbillon

Pour une utilisation `server`, lancer::

    $ poetry run tourbillon --backend

Et maintenant, ça tourne! Fantastique! Notez qu'en mode `server`, TourBillon tourne par
défaut sur le port 59219.
