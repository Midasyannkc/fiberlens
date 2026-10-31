"""County FIPS keys. Every source must agree on one key format or joins drop rows silently."""


def to_fips(value):
    """Return the county key used to join sources."""
    return str(int(float(value)))
