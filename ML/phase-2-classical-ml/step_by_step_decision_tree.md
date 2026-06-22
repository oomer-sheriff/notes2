# Step-by-Step: Decision Tree (Gini Impurity Split)

**Input:** 4 samples, 2 features, binary classification (class 0 = healthy, class 1 = sick).

---

## 1. The Dataset

```
Sample   Fever (x1)   Cough (x2)   Label (y)
  1          1             0           1   (sick)
  2          1             1           1   (sick)
  3          0             1           0   (healthy)
  4          0             0           0   (healthy)
```

The tree will decide which feature to split on at the root node.

---

## 2. Gini Impurity — The Splitting Criterion

**Gini Impurity** measures how "mixed" a group is.

```
Gini(node) = 1 - Σ p_i²

where p_i = proportion of class i in the node
```

A pure node (all same class): Gini = 0  
A perfectly mixed node (50/50): Gini = 0.5 (for binary)

**Root node (all 4 samples):**
```
Class 1 count = 2, Class 0 count = 2, Total = 4
p_1 = 2/4 = 0.5,   p_0 = 2/4 = 0.5

Gini(root) = 1 - (0.5² + 0.5²) = 1 - (0.25 + 0.25) = 0.5
```

Gini = 0.5 means the root is maximally impure. We need to split.

---

## 3. Evaluating Split on Feature x1 (Fever)

**x1 = 1 branch:** Samples 1, 2 → labels [1, 1]
```
p_1 = 2/2 = 1.0,  p_0 = 0/2 = 0.0
Gini(left) = 1 - (1.0² + 0.0²) = 1 - 1 = 0.0   ← PURE!
```

**x1 = 0 branch:** Samples 3, 4 → labels [0, 0]
```
p_1 = 0/2 = 0.0,  p_0 = 2/2 = 1.0
Gini(right) = 1 - (0.0² + 1.0²) = 1 - 1 = 0.0   ← PURE!
```

**Weighted Gini after split on x1:**
```
Weighted Gini = (2/4)*Gini(left) + (2/4)*Gini(right)
              = 0.5 * 0.0 + 0.5 * 0.0
              = 0.0
```

**Information Gain from x1:**
```
Gain(x1) = Gini(root) - Weighted Gini(x1)
          = 0.5 - 0.0
          = 0.5   ← Maximum possible!
```

---

## 4. Evaluating Split on Feature x2 (Cough)

**x2 = 1 branch:** Samples 2, 3 → labels [1, 0]
```
p_1 = 1/2 = 0.5,  p_0 = 1/2 = 0.5
Gini(left) = 1 - (0.5² + 0.5²) = 0.5   ← Still impure
```

**x2 = 0 branch:** Samples 1, 4 → labels [1, 0]
```
p_1 = 1/2 = 0.5,  p_0 = 1/2 = 0.5
Gini(right) = 0.5   ← Still impure
```

**Weighted Gini after split on x2:**
```
Weighted Gini = (2/4)*0.5 + (2/4)*0.5 = 0.5
```

**Information Gain from x2:**
```
Gain(x2) = 0.5 - 0.5 = 0.0   ← No gain!
```

---

## 5. Choose the Best Split

```
Gain(x1=Fever) = 0.5   ← WINNER
Gain(x2=Cough) = 0.0

→ Split on Fever (x1)
```

---

## 6. The Resulting Tree

```
            Root: All 4 samples (Gini=0.5)
            Question: Is Fever=1?
           /                       \
    YES (Fever=1)              NO (Fever=0)
  Samples 1, 2                Samples 3, 4
  Labels: [1, 1]              Labels: [0, 0]
  Gini = 0.0                  Gini = 0.0
  Predict: SICK               Predict: HEALTHY
```

Both leaf nodes are pure — the tree is done in a single split!

---

## 7. Making a Prediction

**New patient: Fever=1, Cough=0**

```
Step 1: Is Fever=1? → YES
Step 2: Go to left leaf
Step 3: Predict → SICK (class 1)
```

**New patient: Fever=0, Cough=1**

```
Step 1: Is Fever=1? → NO
Step 2: Go to right leaf
Step 3: Predict → HEALTHY (class 0)
```

---

## Key Takeaways

| Concept | What it means |
|---|---|
| Gini = 0 | Node is perfectly pure — all same class |
| Gini = 0.5 | Node is perfectly mixed — 50/50 split |
| Information Gain | How much a split reduces impurity |
| Best split | The feature + threshold that gives maximum gain |
| Leaf node | A terminal node — no more splits, just predict majority class |
