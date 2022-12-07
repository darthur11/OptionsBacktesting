from dataclasses import dataclass

@dataclass
class InstrumentInfo:
    ticker: str
    expiration: str
    strike: float
    put_call: str
    amount: float
    price: float

@dataclass
class Position:
    id: str
    ticker: str
    expiration: str
    strike: float
    put_call: str
    amount: float
    price: float
    open_at: str
    closed_at: str or None
    strategy_id: str or None

@dataclass
class StrategyPosition:
    id: str
    instrument_list: list
