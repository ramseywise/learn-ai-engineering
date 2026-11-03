---
title: "Logistic regression in NumPy"
track: coding
topic: ml-coding
difficulty: hard
timebox_min: 40
concepts: [ml-coding]
source: https://github.com/alexeygrigorev/ai-engineering-gym
---
## Prompt

Implement logistic regression from scratch in NumPy. Train it with stochastic
gradient descent, add L2 regularization, and stop early when validation loss
stops improving. Expose fit(X, y) and predict_proba(X).

## Starter

Blank file in `programming/drills/coding/scratch/`. NumPy allowed unless the prompt says otherwise.

## Tests

Turn every example in the prompt into an `assert`, then add the edge cases you named while clarifying (empty input, one element, duplicates, the largest size) before you call it done.

## Hints

One at a time — open the next only after trying with the last.

<details><summary>Hint 1</summary>

The gradient of binary cross-entropy w.r.t. the pre-activation z is just (p - y), which gives you both the weight and bias updates.

</details>

<details><summary>Hint 2</summary>

SGD means update per example (shuffle each epoch), not per full pass. L2 adds a lambda*w term to the weight gradient only. Never regularize the bias.

</details>

<details><summary>Hint 3</summary>

Early stopping needs a validation split, so track val loss each epoch, keep the best weights, and stop after `patience` epochs with no improvement. Guard sigmoid against exp overflow.

</details>

## Solution

<details><summary>Solution: reference approach</summary>

Logistic regression models P(y=1|x) = sigmoid(w·x + b). Fit by minimizing the average binary cross-entropy loss plus an L2 penalty (lambda/2)*||w||^2 (don't regularize the bias). The gradient of cross-entropy is beautifully simple. For a single example, dL/dz = (sigmoid(z) - y), so the weight gradient is (p - y)*x + lambda*w and the bias gradient is (p - y). SGD updates the weights after each example (or small minibatch), shuffling each epoch. Early stopping holds out a validation split and tracks its loss each epoch. It stops when the loss fails to improve for `patience` epochs, restoring the best weights seen. Two numerical details matter: use a numerically stable sigmoid (branch on the sign of z, or use log1p) to avoid exp overflow, and standardize features so the single learning rate works across dimensions.

```python
def sigmoid(z):                      # stable: avoid exp(+large)
    return where(z >= 0, 1/(1+exp(-z)), exp(z)/(1+exp(z)))

def fit(X, y, lr, lam, epochs, patience):
    w = zeros(n_features); b = 0
    best_w, best_loss, bad = w, inf, 0
    Xtr, ytr, Xval, yval = split(X, y)
    for epoch in range(epochs):
        for i in shuffle(range(len(Xtr))):        # SGD: one example at a time
            p = sigmoid(Xtr[i] @ w + b)
            grad = p - ytr[i]                     # dL/dz
            w -= lr * (grad * Xtr[i] + lam * w)   # L2 on weights only
            b -= lr * grad
        vloss = bce(sigmoid(Xval @ w + b), yval) + (lam/2)*w@w
        if vloss < best_loss - 1e-6:
            best_loss, best_w, best_b, bad = vloss, w.copy(), b, 0
        else:
            bad += 1
            if bad >= patience: break             # early stopping
    return best_w, best_b

def predict_proba(X): return sigmoid(X @ w + b)
```

**Complexity** — time `O(epochs * n_samples * n_features)` for training; `O(n_features)` per prediction; space `O(n_features)` for the weight vector (plus the data)

</details>

## Notes

Follow-ups an interviewer may push on:

- How would you switch from pure SGD to minibatch, and what's the trade-off?
- How do you extend this to multiclass (softmax regression)?
- Where would L1 change the update, and why can't you just take its plain gradient at zero?
- How would you add a learning-rate schedule or momentum, and when does it help?
- How do you validate your gradient is correct (gradient checking)?

Sources:

- [Machine Learning Mastery — Logistic Regression with SGD from scratch in Python](https://machinelearningmastery.com/implement-logistic-regression-stochastic-gradient-descent-scratch-python/)
- [Towards Data Science — Implement Logistic Regression with L2 Regularization from Scratch](https://towardsdatascience.com/implement-logistic-regression-with-l2-regularization-from-scratch-in-python-20bd4ee88a59)
- [DataInterview — Mistral Machine Learning Engineer Interview](https://www.datainterview.com/blog/mistral-machine-learning-engineer-interview)

Adapted from [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/coding/aieng-logistic-regression-numpy.yaml`.
