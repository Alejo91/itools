# -*- coding: ISO-8859-1 -*-
# Copyright (C) 2004 Thierry Fromon <from.t@free.fr>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


import unittest
import oracle

class OracleTestCase(unittest.TestCase):

    def test_spain_long(self):
        text = u"""Nueva coordinadora de Humanidades. En sustituci�n de la
        doctora Olga Hansberg, el pasado martes 17 tom� posesi�n como
        coordinadora de Humanidades de la UNAM la doctora Mari Carmen Serra
        Puche. Con la doctora Serra se inicia un nuevo ciclo del cual se espera
        que las ciencias sociales y las humanidades sean lo que deben ser: la
        inteligencia y el alma de la UNAM.

        En la ceremonia de toma de posesi�n de la doctora Serra estuvo presente
        el rector Juan Ram�n de la Fuente, quien sostuvo que la m�xima casa de
        estudios est� preparada para enfrentar los nuevos retos que deber�
        enfrentar la instituci�n en la perspectiva de la reforma. La comunidad
        acad�mica tiene plena confianza en que la nueva coordinadora ser� punto
        de equilibrio y uni�n para que se produzcan una serie de cambios en este
        subsistema universitario. Por lo pronto y para que no digan que no se
        reconoce hay que decir que las autoridades ya anunciaron que el Centro
        de Estudios sobre la Universidad (CESU) y el Instituto de
        Investigaciones Econ�micas tendr�n nuevas instalaciones, decisi�n que
        est� m�s que justificada y, repito, se agradece."""
        self.assertEqual(oracle.guess_language(text), 'es')


    def test_spain_short(self):
        text = u"""Nueva coordinadora de Humanidades. En sustituci�n de la
        doctora Olga Hansberg, el pasado martes 17 tom� posesi�n como
        coordinadora de Humanidades de la UNAM la doctora Mari Carmen Serra
        Puche."""
        self.assertEqual(oracle.guess_language(text), 'es')


    def test_spain_very_sort(self):
        text = """Nueva coordinadora de Humanidades."""
        print self.assertEqual(oracle.guess_language(text), 'es')


    def test_french_long(self):
        text = u"""Le pi�ge de la guerre coloniale se referme sur les
        envahisseurs de lIrak. Comme les troupes fran�aises embourb�es jadis
        en Alg�rie, les Britanniques au Kenya, les Belges au Congo et les
        Portugais en Guin�e-Bissau (voire aujourdhui les Isra�liens � Gaza),
        les forces
        am�ricaines constatent que leur �crasante sup�riorit� ne suffit pas �
        leur �pargner enl�vements, embuscades et autres attentats mortels Pour
        les soldats sur le terrain, loccupation de lIrak se transforme en une
        descente aux enfers."""
        self.assertEqual(oracle.guess_language(text), 'fr')
                

    def test_french_short(self):
        text = u"""un dossier sp�cial consacr� � la � r�volution de velours �
        g�orgienne sur le site de lagence Radio Free Europe fond�e par le
        Congr�s des Etats-Unis."""
        self.assertEqual(oracle.guess_language(text), 'fr')
                

    def test_french_very_sort(self):
        text = u"""Les d�clarations du pr�sident Vladimir Poutine"""
        self.assertEqual(oracle.guess_language(text), 'fr')
                

    def test_english_long(self):
        text = """INDIA SOFTWARE REVENUE UP: India's revenue from exports of
        software and back-office services grew more than 30 percent during the
        fiscal year ended in March despite a backlash in the United States
        against outsourcing, a trade group said.
        .
        Those revenues rose to $12.5 billion in the latest fiscal year from $9.6
        billion a year earlier, said Kiran Karnik, president of the National
        Association of Software and Service Companies.
        .
        U.S. companies account for 70 percent of the revenue. Karnik forecast
        growth of 30 percent to 32 percent in the current"""
        self.assertEqual(oracle.guess_language(text), 'en')


    def test_english_short(self):
        text = """The French, too, paid much attention to French-German
        reconciliation and interpreted the ceremonies as a celebration of
        European integration and peace."""
        self.assertEqual(oracle.guess_language(text), 'en')


    def test_english_very_sort(self):
        text = """But from a cloudless blue sky"""
        self.assertEqual(oracle.guess_language(text), 'en')


if __name__ == '__main__':
    unittest.main()

