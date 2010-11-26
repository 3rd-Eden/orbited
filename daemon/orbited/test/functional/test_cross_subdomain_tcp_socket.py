from selenium import selenium
import unittest, time, re

class TestCrossSubDomainTCPSocket(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("www.orbited", 4444, "*chrome", "http://www.orbited:8000/")
        self.selenium.start()
    
    def test_same_domain_t_c_p_socket(self):
        sel = self.selenium
        sel.open("/static/tests/")
        sel.click("link=Same Domain")
        sel.wait_for_page_to_load("30000")
        try: self.failUnless(sel.is_text_present(""))
        except AssertionError, e: self.verificationErrors.append(str(e))
        time.sleep(NaN)
        try: self.failUnless(sel.is_text_present(""))
        except AssertionError, e: self.verificationErrors.append(str(e))
        try: self.failUnless(sel.is_text_present(""))
        except AssertionError, e: self.verificationErrors.append(str(e))
        try: self.failUnless(sel.is_text_present(""))
        except AssertionError, e: self.verificationErrors.append(str(e))
    
    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
