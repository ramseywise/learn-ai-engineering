---
origin: vendored snapshot: nn-zero-to-hero (Karpathy, MIT; kept as practice)
sources:
  - ../practice/nn-zero-to-hero/micrograd/
  - https://www.youtube.com/watch?v=VMj-3S1tku0
  - https://github.com/karpathy/micrograd
confidence: high
cleaned: 2026-10-31
---
# 15 — micrograd: Backpropagation from Scratch

> A scalar-valued automatic differentiation engine in about 100 lines, and a tiny neural-network library on top of it. Every framework in this folder (Keras, PyTorch, JAX) does exactly this, vectorised over tensors. After this note, `loss.backward()` is not magic: it is a topological sort and the chain rule applied once per node.

This is the first of three notes on Karpathy's *Neural Networks: Zero to Hero*. [16](16-makemore.md) builds language models from bigrams to a WaveNet-style CNN; [17](17-nanogpt.md) builds GPT. Watch the lecture and code along in the notebooks; these notes are the summary to come back to.

---

## Derivatives, numerically

The derivative of `f` at `x` is how much `f` changes per unit nudge of `x`:

```python
def f(x): return 3*x**2 - 4*x + 5
h = 1e-6
(f(3.0 + h) - f(3.0)) / h       # ≈ 14.0   (analytically 6x − 4 = 14)
```

With several inputs, nudge one at a time to get the partial derivative with respect to each. For `d = a*b + c` at `a=2, b=−3, c=10`: ∂d/∂a = b = −3, ∂d/∂b = a = 2, ∂d/∂c = 1. Numerical gradients are how you *check* an implementation (Ng's gradient checking in [07](07-neural-networks-fundamentals.md) is the same idea); they are far too slow to train with, one forward pass per parameter.

---

## The `Value` object

Wrap each scalar so that every arithmetic operation records its inputs and knows how to pass gradient back to them.

```python
import math

class Value:
    def __init__(self, data, _children=(), _op="", label=""):
        self.data = data
        self.grad = 0.0                   # d(output)/d(self), filled in by backward()
        self._backward = lambda: None     # how to push out.grad into the children
        self._prev = set(_children)
        self._op, self.label = _op, label

    def __add__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data + other.data, (self, other), "+")
        def _backward():
            self.grad += 1.0 * out.grad       # addition routes the gradient unchanged to both inputs
            other.grad += 1.0 * out.grad
        out._backward = _backward
        return out

    def __mul__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data * other.data, (self, other), "*")
        def _backward():
            self.grad += other.data * out.grad   # multiplication swaps: d(ab)/da = b
            other.grad += self.data * out.grad
        out._backward = _backward
        return out

    def __pow__(self, k):                        # k is a plain int/float
        out = Value(self.data ** k, (self,), f"**{k}")
        def _backward():
            self.grad += k * self.data ** (k - 1) * out.grad
        out._backward = _backward
        return out

    def tanh(self):
        t = math.tanh(self.data)
        out = Value(t, (self,), "tanh")
        def _backward():
            self.grad += (1 - t**2) * out.grad
        out._backward = _backward
        return out

    def exp(self):
        out = Value(math.exp(self.data), (self,), "exp")
        def _backward():
            self.grad += out.data * out.grad     # the lecture used = here; the notebook fixes it to +=
        out._backward = _backward
        return out

    # everything else is built from the above
    def __neg__(self): return self * -1
    def __sub__(self, other): return self + (-other)
    def __truediv__(self, other): return self * other**-1
    def __radd__(self, other): return self + other
    def __rmul__(self, other): return self * other      # so 2 * Value(3) works

    def backward(self):
        topo, visited = [], set()
        def build(v):
            if v not in visited:
                visited.add(v)
                for child in v._prev:
                    build(child)
                topo.append(v)                 # a node is appended only after all its inputs
        build(self)
        self.grad = 1.0                        # d(self)/d(self)
        for node in reversed(topo):            # output first, leaves last
            node._backward()
```

### The three ideas in that code

| Idea | Where | Why it matters |
|---|---|---|
| **Local derivatives** | Each `_backward` knows only its own op's derivative | Adding a new op means writing one small closure |
| **Chain rule** | `self.grad += local * out.grad` | Gradient at a node = (gradient arriving from above) × (local derivative) |
| **Topological order** | `backward()` | A node's `_backward` runs only after every node that uses it has finished contributing |

**Why `+=` and not `=`.** If a value is used twice (`b = a + a`, or a weight shared across examples), gradient arrives along every path and must be summed. Using `=` silently keeps only the last path; the lecture hit exactly this bug and the notebook comments the fix. It is also why gradients must be zeroed before each backward pass: `+=` accumulates across calls too.

**Granularity is a choice.** `tanh` can be a single op with derivative `1 − t²`, or built as `(e − 1)/(e + 1)` with `e = (2n).exp()`; both give the same gradients. Frameworks pick fused ops for speed and numerical stability.

---

## One neuron, checked against PyTorch

```python
x1, x2 = Value(2.0, label="x1"), Value(0.0, label="x2")
w1, w2 = Value(-3.0, label="w1"), Value(1.0, label="w2")
b = Value(6.8813735870195432, label="b")     # chosen so the output is a round number
n = x1*w1 + x2*w2 + b                        # 0.8814
o = n.tanh()                                 # 0.7071
o.backward()
# do/dn = 1 - o² = 0.5 ; w1.grad = x1 * 0.5 = 1.0 ; x1.grad = w1 * 0.5 = -1.5 ; w2.grad = x2 * 0.5 = 0.0
```

The same in PyTorch, where the tensors are the `Value`s and autograd is the `backward()`:

```python
import torch
x1 = torch.tensor([2.0], dtype=torch.double, requires_grad=True)
w1 = torch.tensor([-3.0], dtype=torch.double, requires_grad=True)
# ... x2, w2, b likewise
o = torch.tanh(x1*w1 + x2*w2 + b)
o.backward()
x1.grad.item(), w1.grad.item()               # (-1.5, 1.0): identical
```

`w2.grad` is 0 because `x2 = 0`: a weight on a zero input cannot affect the output, so it gets no gradient. The notebooks draw each expression as a graph with `graphviz` (`draw_dot(o)`), showing `data` and `grad` at every node. Drawing it once by hand is the fastest way to internalise backprop.

---

## A neural-network library on top

```python
import random

class Neuron:
    def __init__(self, nin):
        self.w = [Value(random.uniform(-1, 1)) for _ in range(nin)]
        self.b = Value(random.uniform(-1, 1))
    def __call__(self, x):
        return sum((wi*xi for wi, xi in zip(self.w, x)), self.b).tanh()
    def parameters(self):
        return self.w + [self.b]

class Layer:
    def __init__(self, nin, nout):
        self.neurons = [Neuron(nin) for _ in range(nout)]
    def __call__(self, x):
        outs = [n(x) for n in self.neurons]
        return outs[0] if len(outs) == 1 else outs
    def parameters(self):
        return [p for n in self.neurons for p in n.parameters()]

class MLP:
    def __init__(self, nin, nouts):
        sz = [nin] + nouts
        self.layers = [Layer(sz[i], sz[i+1]) for i in range(len(nouts))]
    def __call__(self, x):
        for layer in self.layers:
            x = layer(x)
        return x
    def parameters(self):
        return [p for layer in self.layers for p in layer.parameters()]

model = MLP(3, [4, 4, 1])         # 3 inputs, two hidden layers of 4, one output: 41 parameters
```

This mirrors `torch.nn`: modules hold parameters, are callable, and expose `parameters()`.

### The training loop

```python
xs = [[2.0, 3.0, -1.0], [3.0, -1.0, 0.5], [0.5, 1.0, 1.0], [1.0, 1.0, -1.0]]
ys = [1.0, -1.0, -1.0, 1.0]

for k in range(20):
    ypred = [model(x) for x in xs]                                   # 1. forward
    loss = sum((yp - yt)**2 for yt, yp in zip(ys, ypred))            # 2. loss (sum of squared errors)
    for p in model.parameters():                                     # 3. zero grads
        p.grad = 0.0
    loss.backward()                                                  # 4. backward
    for p in model.parameters():                                     # 5. step: move against the gradient
        p.data += -0.05 * p.grad
    print(k, loss.data)
```

| Step | PyTorch equivalent |
|---|---|
| forward | `ypred = model(X)` |
| loss | `loss = F.mse_loss(ypred, y)` |
| zero grads | `optimizer.zero_grad()` (or `p.grad = None`) |
| backward | `loss.backward()` |
| step | `optimizer.step()` |

Forgetting step 3 is the most common bug in hand-written loops: gradients from previous iterations pile up and training behaves erratically. It is easy to make here and just as easy in PyTorch.

---

## From scalars to tensors

micrograd builds one graph node per scalar multiply. That is fine for 41 parameters and hopeless for millions. Real frameworks make each node a tensor op (`matmul`, `softmax`, `layernorm`) whose backward is a few matrix expressions, run on a GPU. The concepts carry over exactly:

| micrograd | PyTorch |
|---|---|
| `Value` | `torch.Tensor` with `requires_grad=True` |
| `_prev`, `_op` | `tensor.grad_fn` and its `next_functions` |
| `_backward` closure | `torch.autograd.Function.backward` |
| `backward()` topo sort | the autograd engine |
| `p.data += -lr * p.grad` | `torch.optim.SGD` (Adam keeps running averages of grad and grad²) |

[16 — makemore part 4](16-makemore.md#part-4-becoming-a-backprop-ninja) does the tensor version by hand: deriving the backward pass for cross-entropy, batch norm and a linear layer and checking each against autograd.

---

## Exercises worth doing

| Exercise | What it teaches |
|---|---|
| Add `relu`, `log`, and true division with gradient for both operands | Writing local derivatives |
| Replace squared error with a softmax cross-entropy on 3 classes | Why cross-entropy's gradient is `p − y` |
| Train the MLP on `sklearn.datasets.make_moons` with a hinge loss and L2 penalty (the micrograd repo's demo) | Regularisation, decision boundaries ([02](02-supervised-learning.md)) |
| Compare every gradient to a finite-difference estimate | Gradient checking |
| Use a node twice (`a*a`) and verify `+=` gives `2a` | Gradient accumulation |

---

## Practice

| Notebook | Covers | Runs |
|---|---|---|
| [`micrograd_lecture_first_half_roughly`](../practice/nn-zero-to-hero/micrograd/micrograd_lecture_first_half_roughly.ipynb) | Numerical derivatives, `Value`, manual backprop through a graph, graphviz drawing | Runs offline; `graphviz` (Python package and system binary) for the diagrams |
| [`micrograd_lecture_second_half_roughly`](../practice/nn-zero-to-hero/micrograd/micrograd_lecture_second_half_roughly.ipynb) | Full `Value` with `backward()`, PyTorch comparison, Neuron/Layer/MLP, training loop | Runs offline; `torch` for the comparison cell |

Lecture: [The spelled-out intro to neural networks and backpropagation](https://www.youtube.com/watch?v=VMj-3S1tku0) (2.5 h).

---

→ Next: [16-makemore.md](16-makemore.md) — character-level language models from bigram counts to a WaveNet-style CNN, and how to keep deep networks trainable.
