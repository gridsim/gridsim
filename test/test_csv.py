import unittest
import warnings

from gridsim.iodata.input import CSVReader


class TestCSVReader(unittest.TestCase):

    def test_default_load_with_header(self):

        ref_data = {'humidity': ['0.2', '0.25', '0.1', '0.7'],
                    'temperature': ['20.0', '20.0', '18', '4.1'],
                    'time': ['0', '1', '2', '3']}

        cvs_reader = CSVReader()

        data = cvs_reader.load('./test/data/datatest_with_header.csv')

        self.assertEqual(ref_data, data)

    def test_convert_load_with_header(self):

        ref_data = {'humidity': [0.2, 0.25, 0.1, 0.7],
                    'temperature': [20.0, 20.0, 18, 4.1],
                    'time': [0, 1, 2, 3]}

        cvs_reader = CSVReader()

        data = cvs_reader.load('./test/data/datatest_with_header.csv',
                               data_type=float)

        self.assertEqual(ref_data, data)

    def test_default_load_no_header(self):

        ref_data = {CSVReader.DEFAULT_DATA_NAME+str(2): ['0.2', '0.25', '0.1'],
                    CSVReader.DEFAULT_DATA_NAME+str(1): ['20.0', '20.0', '18'],
                    CSVReader.DEFAULT_DATA_NAME+str(0): ['0', '1', '2']}

        cvs_reader = CSVReader()

        warnings.simplefilter("always", SyntaxWarning)
        data = cvs_reader.load('./test/data/datatest_no_header.csv')

        self.assertEqual(ref_data, data)

    def test_convert_load_no_header(self):

        ref_data = {CSVReader.DEFAULT_DATA_NAME+str(2): [0.2, 0.25, 0.1],
                    CSVReader.DEFAULT_DATA_NAME+str(1): [20.0, 20.0, 18],
                    CSVReader.DEFAULT_DATA_NAME+str(0): [0, 1, 2]}

        cvs_reader = CSVReader()

        warnings.simplefilter("always", SyntaxWarning)
        data = cvs_reader.load('./test/data/datatest_no_header.csv',
                                   data_type=float)

        self.assertEqual(ref_data, data)

    def test_warning_no_header(self):

        cvs_reader = CSVReader()

        warnings.simplefilter("error", SyntaxWarning)
        with self.assertRaises(SyntaxWarning):
            warnings.simplefilter("error", SyntaxWarning)
            cvs_reader.load('./test/data/datatest_no_header.csv')
            warnings.simplefilter('always', SyntaxWarning)

if __name__ == '__main__':
    unittest.main()
