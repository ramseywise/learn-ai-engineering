"""04 — Objects. Run: python3 04_objects.py"""


class Account:
    """Q1. A bank account.
    - Account(owner, balance=0); a negative opening balance raises ValueError.
    - deposit(amount) and withdraw(amount) return the new balance; amounts must be > 0.
    - withdraw more than the balance raises ValueError and leaves the balance unchanged.
    - repr: Account('Ada', 10.0)
    - == compares owner and balance; < compares balance (so sorted() works)."""

    def __init__(self, owner: str, balance: float = 0):
        raise NotImplementedError

    def deposit(self, amount: float) -> float:
        raise NotImplementedError

    def withdraw(self, amount: float) -> float:
        raise NotImplementedError

    def __repr__(self) -> str:
        raise NotImplementedError

    def __eq__(self, other: object) -> bool:
        raise NotImplementedError

    def __lt__(self, other: "Account") -> bool:
        raise NotImplementedError


class SavingsAccount(Account):
    """Q2. An Account with a rate. add_interest() adds balance * rate (rounded to cents)
    and returns the new balance. At most 3 withdrawals: the 4th raises ValueError."""

    def __init__(self, owner: str, balance: float = 0, rate: float = 0.02):
        raise NotImplementedError

    def add_interest(self) -> float:
        raise NotImplementedError

    def withdraw(self, amount: float) -> float:
        raise NotImplementedError


def _raises(fn) -> bool:
    try:
        fn()
    except ValueError:
        return True
    return False


if __name__ == "__main__":
    a = Account("Ada", 10)
    assert a.deposit(5) == 15 and a.withdraw(3) == 12
    assert _raises(lambda: a.withdraw(100)) and a.balance == 12
    assert _raises(lambda: a.deposit(0)) and _raises(lambda: Account("X", -1))
    assert repr(a) == "Account('Ada', 12.0)"
    assert Account("Ada", 12) == a and Account("Bob", 12) != a
    assert [x.owner for x in sorted([Account("b", 5), Account("a", 1), Account("c", 3)])] == ["a", "c", "b"]
    s = SavingsAccount("Sam", 100, rate=0.05)
    assert isinstance(s, Account) and s.add_interest() == 105.0
    for _ in range(3):
        s.withdraw(1)
    assert _raises(lambda: s.withdraw(1)) and s.balance == 102.0
    print("all good")
