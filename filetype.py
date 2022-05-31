from enum import Enum
import chardet
class FileType(Enum):
    TEXT=1,
    BINARY=2
    @staticmethod
    def check(filepath,readsize = 1024):
        bytes_to_check=open(filepath,mode="rb").read(readsize)
        if not bytes_to_check:
            return FileType.TEXT
            
        _control_chars = b'\n\r\t\f\b'
        if bytes is str:
            _printable_ascii = _control_chars + b''.join(map(chr, range(32, 127)))
            _printable_high_ascii = b''.join(map(chr, range(127, 256)))
        else:
            _printable_ascii = _control_chars + bytes(range(32, 127))
            _printable_high_ascii = bytes(range(127, 256))

        low_chars = bytes_to_check.translate(None, _printable_ascii)
        nontext_ratio1 = float(len(low_chars)) / float(len(bytes_to_check))

        high_chars = bytes_to_check.translate(None, _printable_high_ascii)
        nontext_ratio2 = float(len(high_chars)) / float(len(bytes_to_check))

        if nontext_ratio1 > 0.90 and nontext_ratio2 > 0.90:
            return FileType.BINARY

        is_likely_binary = (
            (nontext_ratio1 > 0.3 and nontext_ratio2 < 0.05) or
            (nontext_ratio1 > 0.8 and nontext_ratio2 > 0.8)
        )
        detected_encoding = chardet.detect(bytes_to_check)
        decodable_as_unicode = False
        if (detected_encoding['confidence'] > 0.9 and
                detected_encoding['encoding'] != 'ascii'):
            try:
                try:
                    bytes_to_check.decode(encoding=detected_encoding['encoding'])
                except TypeError:
                    # happens only on Python 2.6
                    unicode(bytes_to_check, encoding=detected_encoding['encoding'])  # noqa
                decodable_as_unicode = True
            except LookupError:
                raise Exception('failure: could not look up encoding %(encoding)s',
                             detected_encoding)
            except UnicodeDecodeError:
                raise Exception('failure: decodable_as_unicode: '
                             '%(decodable_as_unicode)r', locals())

        if is_likely_binary:
            if decodable_as_unicode:
                return FileType.TEXT
            else:
                return FileType.BINARY
        else:
            if decodable_as_unicode:
                return FileType.TEXT
            else:
                if b'\x00' in bytes_to_check or b'\xff' in bytes_to_check:
                    return FileType.BINARY
            return FileType.TEXT

