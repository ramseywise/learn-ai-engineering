"""08 — Objects, inheritance and the MRO. Run: python3 08_objects_mro.py"""


class A: ...
class B(A): ...
class C(A): ...
class D(B, C): ...


def mro_names(cls: type) -> list[str]:
    """Q1. Return the names of cls's ancestors in method resolution order, cls first and
    `object` last: mro_names(D) -> ['D', 'B', 'C', 'A', 'object']."""
    raise NotImplementedError


def is_linearizable(*bases: type) -> bool:
    """Q2. True if a class could be defined with these bases, False if Python would raise
    TypeError for an inconsistent MRO. Define a throwaway class inside the function."""
    raise NotImplementedError


class Bounded:
    """Q3. A data descriptor for a number that must stay inside [low, high].
    - Assigning a value outside the range raises ValueError; reading returns the stored value.
    - Store the value in the instance __dict__ under the attribute's own name
      (use __set_name__), so one Bounded on the class serves every instance."""

    def __init__(self, low: float, high: float) -> None:
        raise NotImplementedError

    def __set_name__(self, owner: type, name: str) -> None:
        raise NotImplementedError

    def __get__(self, obj, objtype=None):
        raise NotImplementedError

    def __set__(self, obj, value: float) -> None:
        raise NotImplementedError


class Config:
    top_p = Bounded(0.0, 1.0)

    def __init__(self, top_p: float) -> None:
        self.top_p = top_p


class Provider:
    """Q4. Using __init_subclass__, refuse any subclass that has no callable `complete`,
    raising TypeError when the class statement runs."""


if __name__ == "__main__":
    assert mro_names(D) == ["D", "B", "C", "A", "object"]

    class E(C, B): ...

    assert mro_names(E) == ["E", "C", "B", "A", "object"]
    assert is_linearizable(B, C) and is_linearizable(C, B)
    assert not is_linearizable(D, E)

    one, two = Config(0.5), Config(0.9)
    assert one.top_p == 0.5 and two.top_p == 0.9
    try:
        one.top_p = 1.5
        raise AssertionError("expected ValueError")
    except ValueError:
        pass
    assert one.top_p == 0.5

    class Good(Provider):
        def complete(self, prompt: str) -> str:
            return prompt

    try:

        class Bad(Provider): ...

        raise AssertionError("expected TypeError")
    except TypeError:
        pass
    print("all good")
