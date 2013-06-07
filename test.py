__author__ = 'nedr'

import unittest
import convert


class MyTestCase(unittest.TestCase):
    def test_filename_dirname_creation(self):
        test_response = convert.get_backup_path_filename(
            'full', '/home/nedr/backup/', '/home/nedr/source/path/test.mov', '/home/nedr/source/', '/home/nedr/source/path', 'test.mov')
        true_response = '/home/nedr/backup/home/nedr/source/path/test.mov', '/home/nedr/backup/home/nedr/source/path'
        self.assertEqual(test_response, true_response)




if __name__ == '__main__':
    unittest.main()
