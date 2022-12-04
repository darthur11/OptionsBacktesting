from dataclasses import dataclass

@dataclass
class InstrumentInfo:
    ticker: str
    expiration: str
    strike: float
    put_call: str
    amount: float
    price: float
    date: str

@dataclass
class Position:
    id: str
    ticker: str
    expiration: str
    strike: float
    put_call: str
    amount: float
    price: float
    date: str
    strategy_id: str

@dataclass
class StrategyPosition:
    id: str
    instrument_list: list
