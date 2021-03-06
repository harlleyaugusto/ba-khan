import sys
import unittest
import TestLoginUtp
import TestPautasTestUtp
import TestVercursoVergruposContactos1erMedioA
 
class Test_Suite(unittest.TestCase):

    def test_main(self):
         
        # suite of TestCases
        self.suite = unittest.TestSuite()
        self.suite.addTests([            
            unittest.defaultTestLoader.loadTestsFromTestCase(TestLoginUtp.TestLoginUtp),
            unittest.defaultTestLoader.loadTestsFromTestCase(TestPautasTestUtp.TestPautasTestUtp),
            unittest.defaultTestLoader.loadTestsFromTestCase(TestVercursoVergruposContactos1erMedioA.TestVercursoVergruposContactos1erMedioA),
                                 
            ])
        runner = unittest.TextTestRunner()
        runner.run (self.suite)

import unittest
if __name__ == "__main__":
    unittest.main()