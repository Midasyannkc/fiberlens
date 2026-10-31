"""County FIPS keys. Every source must agree on one key format or joins drop rows silently.

The canonical key is the 5-character zero-padded string: state FIPS (2) plus county FIPS (3), e.g. '01001'."""


def to_fips(value):
    """Return the 5-character zero-padded county key used to join sources."""
    return f"{int(float(value)):05d}"
