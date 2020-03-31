import unittest
import qurandl

class TestQuranDl(unittest.TestCase):
    def test_remove_zero(self):
        self.assertEqual(qurandl.remove_zero("019"), "19")

    def test_extract_number(self):
        self.assertEqual(qurandl.extract_number("edris-abkar-001.mp3"),"1")

if __name__ == "__main__":
    unittest.main()