import csv
import warnings
from io import BufferedReader

from gridsim.decorators import accepts, returns


class Reader(object):

    def __init__(self):
        """
        __init__(self)

        This class is the based class of all readers/loaders.
        """
        super(Reader, self).__init__()

    def clear(self):
        """
        clear(self)

        Empties the data of the Reader.
        """
        raise NotImplementedError('Pure abstract method.')

    @accepts((1, (str, BufferedReader)),
             (2, type),
             (3, bool))
    @returns(dict)
    def load(self, stream, data_type=str, clear_data=False):
        """
        load(self, stream, data_type=str, clear_data=False)

        This method MUST returns formatted data following this format
        ``[(label1, data1], (label2, data2), ...]``

        with:

        * ``labelX``: a str
        * ``dataX``: a list of ``data_type``

        :param stream: a stream of data or a file name
        :type stream: str, BufferedReader

        :param data_type: the type of stored data
        :type data_type: type (default str)

        :param clear_data: if clear data is ``True`` load the file even if the
            file is already loaded.
        :type clear_data: bool

        :return: a dict of values
        :rtype: dict
        """
        raise NotImplementedError('Pure abstract method.')


class CSVReader(Reader):

    DEFAULT_DATA_NAME = "DATA_"
    """
    If no header, the label of the ``dict`` returned by
    :func:`gridsim.iodata.input.CSVReader.load` will be ``DATA_X`` with ``X`` an
    integer representing the column in the file:

    ``0 <= X < column number - 1``
    """

    def __init__(self):
        """
        __init__(self)

        This class reads a CSV file and stores the data as follow:

        ``[(label1, data1], (label2, data2), ...]``

        with:

        * ``labelX``: a str
        * ``dataX``: a list of ``data_type``

        """
        super(CSVReader, self).__init__()
        self._data = dict()

    def clear(self):
        """
        clear(self)

        :return:
        """
        self._data.clear()

    @accepts((1, (str, BufferedReader)),
             (2, type),
             (3, bool))
    @returns(dict)
    def load(self, stream, data_type=str, clear_data=False):
        """
        load(self, stream, data_type=str, clear_data=False)

        Loads the data from the given CSV data file.

        :param stream: A stream of the CSV data to read
        :type stream: str, BufferedReader
        :param data_type: the type of the stored data
        :type data_type: type
        :param clear_data: if ``True`` clear the data if the reader already
            loads a file.
        :type clear_data: bool
        """

        # empty the data if already filled
        if clear_data:
            self.clear()

        if len(self._data) == 0:
            # Open the csv data file.
            with open(stream, 'r') as csv_data:

                #create a sniffer
                sniffer = csv.Sniffer()

                #verify header
                has_header = sniffer.has_header(csv_data.read())
                if not has_header:
                    warnings.warn("The CVS data %s has no header" % stream,
                                  category=SyntaxWarning)

                # return to the begin
                csv_data.seek(0)

                # sniff the data to find a header
                dialect = sniffer.sniff(csv_data.read())
                # return to the begin
                csv_data.seek(0)

                # Create the CSV parser.
                reader = csv.reader(csv_data, dialect)

                # Read header

                data_names = reader.next()
                if not has_header:
                    for i in range(0, len(data_names)):
                        data_names[i] = CSVReader.DEFAULT_DATA_NAME+str(i)
                    csv_data.seek(0)

                # initialise the dict
                self._data = dict(zip(data_names, [[] for _ in data_names]))

                # Load data into the object.
                for row in reader:
                    if len(row) is not len(data_names):
                        raise SyntaxError('Invalid gridsim CSV file.')

                    for i in range(0, len(row)):
                        self._data[data_names[i]].append(data_type(row[i]))

        return self._data
