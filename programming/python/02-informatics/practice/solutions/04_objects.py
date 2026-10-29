"""04 — Objects. Run: python3 04_objects.py"""


class Account:
    """Q1. A bank account.
    - Account(owner, balance=0); a negative opening balance raises ValueError.
    - deposit(amount) and withdraw(amount) return the new balance; amounts must be > 0.
    - withdraw more than the balance raises ValueError and leaves the balance unchanged.
    - repr: Account('Ada', 10.0)
    - == compares owner and balance; < compares balance (so sorted() works)."""

    def __init__(self, owner: str, balance: float = 0):
        if balance < 0:
            raise ValueError("opening balance must be >= 0")
        self.owner = owner
        self.balance = float(balance)

    def deposit(self, amount: float) -> float:
        if amount <= 0:
            raise ValueError("amount must be positive")
        self.balance += amount
        return self.balance

    def withdraw(self, amount: float) -> float:
        if amount <= 0:
            raise ValueError("amount must be positive")
        if amount > self.balance:
            raise ValueError("insufficient funds")
        self.balance -= amount
        return self.balance

    def __repr__(self) -> str:
        return f"Account({self.owner!r}, {self.balance!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Account):
            return NotImplemented
        return (self.owner, self.balance) == (other.owner, other.balance)

    def __lt__(self, other: "Account") -> bool:
        return self.balance < other.balance


class SavingsAccount(Account):
    """Q2. An Account with a rate. add_interest() adds balance * rate (rounded to cents)
    and returns the new balance. At most 3 withdrawals: the 4th raises ValueError."""

    def __init__(self, owner: str, balance: float = 0, rate: float = 0.02):
        super().__init__(owner, balance)
        self.rate = rate
        self.withdrawals = 0

    def add_interest(self) -> float:
        self.balance = round(self.balance * (1 + self.rate), 2)
        return self.balance

    def withdraw(self, amount: float) -> float:
        if self.withdrawals >= 3:
            raise ValueError("withdrawal limit reached")
        result = super().withdraw(amount)
        self.withdrawals += 1
        return result


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
