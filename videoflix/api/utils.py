class RangeFileWrapper:
    """
    Wrapper for a file-like object to iterate over a specific byte range.

    This class allows reading chunks of a file starting from a given offset up to a specified length,
    yielding data blocks of a defined size.

    Attributes:
        file (file-like object): The underlying file object to read from.
        remaining (int or None): Number of bytes left to read; None means read until EOF.
        blksize (int): Size of each data block to read and yield.
    """

    def __init__(self, file, offset=0, length=None, blksize=8192):
        """
        Initialize the RangeFileWrapper.

        Args:
            file (file-like object): The file to wrap.
            offset (int, optional): The byte offset from where to start reading. Defaults to 0.
            length (int or None, optional): Number of bytes to read. None to read until EOF. Defaults to None.
            blksize (int, optional): Size of chunks to read in bytes. Defaults to 8192.
        """
        self.file = file
        self.file.seek(offset)
        self.remaining = length
        self.blksize = blksize

    def __iter__(self):
        """
        Iterate over the file in blocks of size `blksize` until the specified length is exhausted.

        Yields:
            bytes: A block of data read from the file.
        """
        while True:
            if self.remaining is not None and self.remaining <= 0:
                break
            data = self.file.read(self.blksize)
            if not data:
                break
            if self.remaining:
                data = data[:self.remaining]
                self.remaining -= len(data)
            yield data
