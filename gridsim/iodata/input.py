import csv
import warnings

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

    @accepts((1, str))
    @returns(dict)
    def load(self, data_type=None):
        """
        load(self, data_type=None)

        This method MUST returns formatted data following this format
        ``[(label1, data1], (label2, data2), ...]``

        with:

        * ``labelX``: a str
        * ``dataX``: a list of ``data_type``

        :param data_type: the type of stored data if ``None`` no conversion
            are done.
        :type data_type: type (default None)

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

    def __init__(self, stream):
        """
        __init__(self)

        This class reads a CSV file and stores the data as follow:

        ``[(label1, data1], (label2, data2), ...]``

        with:

        * ``labelX``: a str
        * ``dataX``: a list of ``data_type``

        :param stream: a stream of data or a file name
        :type stream: str, BufferedReader

        """
        super(CSVReader, self).__init__()
        self._data = dict()

        self._stream = stream

    def clear(self):
        """
        clear(self)

        :return:
        """
        self._data.clear()

    @accepts((1, str))
    @returns(dict)
    def load(self, data_type=None):
        """
        load(self, stream, data_type=None, clear_data=False)

        Loads the data from the given CSV data file.

        :param data_type: the type of the stored data if ``None`` no conversion
            are done.
        :type data_type: type
        """

        # Open the csv data file.
        with open(self._stream, 'r') as csv_data:

            #create a sniffer
            sniffer = csv.Sniffer()

            #verify header
            has_header = sniffer.has_header(csv_data.read())
            if not has_header:
                warnings.warn("The CVS data %s has no header" % self._stream,
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
                    if data_type is None:
                        self._data[data_names[i]].append(row[i])
                    else:
                        self._data[data_names[i]].append(data_type(row[i]))

        return self._data
