__author__ = 'nedr'

import unittest
import convert


class MyTestCase(unittest.TestCase):
    def test_filename_dirname_creation(self):
        test_response = convert.get_backup_path_filename(
            'full', '/home/nedr/backup/', '/home/nedr/source/path/test.mov', '/home/nedr/source/', '/home/nedr/source/path', 'test.mov')
        true_response = '/home/nedr/backup/home/nedr/source/path/test.mov', '/home/nedr/backup/home/nedr/source/path'
        self.assertEqual(test_response, true_response)

    def test_verification_same_files(self):
        test_response = convert.identity_verification('test_area/same_files_check1.txt',
                                                      'test_area/same_files_check1.txt')
        true_response = 'same'
        self.assertEqual(test_response, true_response)

    def test_verification_different_files(self):
        test_response = convert.identity_verification('./test_area/same_files_check1.txt',
                                                      './test_area/same_files_check2.txt')
        true_response = 'different'
        self.assertEqual(test_response, true_response)


if __name__ == '__main__':
    unittest.main()
