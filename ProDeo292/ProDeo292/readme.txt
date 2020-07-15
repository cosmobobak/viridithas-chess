Pro Deo (version 2.9) 
Copyright ©2018, by Ed Schröder, The Netherlands
www.rebel13.nl

Installation ProDeo
===================

. To run ProDeo you will need to announce the engine first, under 
  Chessbase this means:

   Engine -> New UCI engine -> Browse -> RebelUCI.exe

. That's it! ProDeo may now be used in the ChessBase Interface. 

. Under ChessPartner do:

   Extra -> Engine Import Wizard -> Winboard engines -> Install -> ProDeo.exe

. For Arena:

   Engines -> Install new engine -> RebelUCI.exe



Hash Table
==========

. You can increase (or decrease) the Hash Table size by editing the 
  WB2UCI.ENG file. Modify the "w4" item of the parameter: 
       
           Program = prodeo.exe w4 prodeo.eng
  
  into:    w0,w1,w2,w3,w4,w5,w6,w7,w8,w9,wa,wb,wc or wd

           w0=  16Mb | w1=  48Mb | w2=  64Mb | w3=  96Mb | w4= 128Mb 
           w5= 192Mb | w6= 256Mb | w7= 384Mb | w8= 512Mb | w9= 768Mb 
           wa=   8Mb | wb=  4Mb  | wc=   2Mb | wd=   1Mb

  Save the file and restart the program. The change is permanent.

. You can turn off ProDeo's opening book by removing the ";" character
  from the parameter:     ; InitString = BookOff/n


Copyright Stuff
===============

. The ProDeo chess engine and its components although distributed as 
  freeware in no way might become subject to any form of commerce. 
  Permission must be asked first.

. The ProDeo chess engine and its components comes as is and can only be 
  used as such. It's forbidden to change, add, delete any of its components
  and only can be distributed in original form.

. Always check the rebel13.nl website for the correct version.


    Credits
    =======

    Chess program : Ed Schröder
     Opening Book : Jeroen Noomen
 Winboard support : Lex Loep
    UCI Interface : Odd Gunnar Malin
     Beta testers : Thorsten Czub

