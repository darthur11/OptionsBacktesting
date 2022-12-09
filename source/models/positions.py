from dataclasses import dataclass

@dataclass
class InstrumentInfo:
    ticker: str
    expiration: str
    strike: float
    put_call: str
    amount: float
    open_price: float

@dataclass
class Position:
    id: str
    ticker: str
    expiration: str
    strike: float
    put_call: str
    amount: float
    open_price: float
    liquidation_price: float or None
    open_at: str
    closed_at: str or None
    strategy_id: str or None
    profit: float or None

@dataclass
class StrategyPosition:
    id: str
    instrument_list: list
