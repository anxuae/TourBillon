
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
          #&                                              Version 5.0.5 © La Billonnière



TourBillon
==========

TourBillon est un logiciel libre (distribué sous licence GPL) qui permet d'organiser les
tournois de billons. Tourbillon s'installe et s'utilise en un tour de main, trois interfaces
sont possibles: "standalone" (par defaut), "shell" ou "backend" (server HTTP RESTful).


Dépendances
===========

* Python >= 2.7 (requis)
* PyYaml version 3.10 (requis)
* WxPython version 2.8 (optionel: mode "standalone")
* Flask version 0.10.1 + flask-restful (optionel: mode "serveur")
* Pyreadline version 1.7 (optionel: mode "shell")


Installation
============

Télécharger les binaires correspondant à votre système d'exploitation depuis la page
`releases <https://github.com/anxuae/tourbillon-gui/releases>`_


Démarrage rapide
================

Pour une utilisation `standelone`, double-clickez sur l'executable (Windows: *TrourBillon.exe*
ou Mac OSX: *TrourBillon.app*) ou tapez la commande *tourbillon* sur un système unix.

Pour une utilisation `server`, lancer::

    $ tourbillon --backend

Pour une utilisation `shell`, lancer::

    $ tourbillon --shell

Et maintenant, ça tourne! Fantastique! Notez qu'en mode `server`, TourBillon tourne par
défaut sur le port 14000.
