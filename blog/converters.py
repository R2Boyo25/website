import base32_crockford


class FourDigitLeftPadIntConverter:
    regex = "[0-9]{4}"

    def to_python(self, value) -> int:
        return int(value)

    def to_url(self, value) -> str:
        return "%04d" % value


class TwoDigitLeftPadIntConverter:
    regex = "[0-9]{1,2}"

    def to_python(self, value) -> int:
        return int(value)

    def to_url(self, value) -> str:
        return "%02d" % value


class Base32Converter:
    regex = "[A-TV-Za-tv-z0-9]+"

    def to_python(self, value: str) -> int:
        return base32_crockford.decode(value)

    def to_url(self, value: int):
        return base32_crockford.encode(value)


class IntNotZero:
    regex = "[0-9]*[1-9]"

    def to_python(self, value: str) -> int:
        return int(value)

    def to_url(self, value: int) -> str:
        return str(value)
