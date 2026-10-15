from enum import StrEnum


class Ticker(StrEnum):
    BTC_USD = "btc_usd"
    ETH_USD = "eth_usd"

    @classmethod
    def _missing_(cls, value: object) -> "Ticker | None":
        # Allow "BTC_USD" and "Btc_Usd" in the query string.
        if isinstance(value, str):
            for member in cls:
                if member.value == value.lower():
                    return member
        return None
