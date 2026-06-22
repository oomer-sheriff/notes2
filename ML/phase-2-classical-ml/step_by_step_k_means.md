# Step-by-Step: K-Means Clustering

**Input:** 4 points in 2D space. Goal: find 2 clusters.

---

## 1. The Data

```
Point    x     y     True group
  A      1.0   1.0   (bottom-left cluster)
  B      1.5   2.0   (bottom-left cluster)
  C      5.0   4.0   (top-right cluster)
  D      5.5   5.0   (top-right cluster)
```

Plotted:

```
y
5 |          D
4 |       C
3 |
2 |  B
1 |A
  +------------- x
  1    3    5
```

---

## 2. Step 0: Initialize Centroids

We randomly pick **2** initial centroids (k=2). Let's pick point A and point C:

```
Centroid 1 (μ1) = [1.0, 1.0]   (initialized at A)
Centroid 2 (μ2) = [5.0, 4.0]   (initialized at C)
```

---

## 3. Step 1: Assignment — Assign Each Point to Nearest Centroid

Distance formula: Euclidean distance = `√((x2-x1)² + (y2-y1)²)`

**Point A = [1.0, 1.0]:**
```
dist(A, μ1) = √((1-1)² + (1-1)²) = √0          =  0.0
dist(A, μ2) = √((1-5)² + (1-4)²) = √(16+9)     =  5.0
→ Assign to Cluster 1 (closer to μ1)
```

**Point B = [1.5, 2.0]:**
```
dist(B, μ1) = √((1.5-1)² + (2-1)²) = √(0.25+1) = 1.12
dist(B, μ2) = √((1.5-5)² + (2-4)²) = √(12.25+4) = 4.03
→ Assign to Cluster 1 (closer to μ1)
```

**Point C = [5.0, 4.0]:**
```
dist(C, μ1) = √((5-1)² + (4-1)²) = √(16+9)     = 5.0
dist(C, μ2) = √((5-5)² + (4-4)²) = √0          = 0.0
→ Assign to Cluster 2 (closer to μ2)
```

**Point D = [5.5, 5.0]:**
```
dist(D, μ1) = √((5.5-1)² + (5-1)²) = √(20.25+16) = 6.02
dist(D, μ2) = √((5.5-5)² + (5-4)²) = √(0.25+1)   = 1.12
→ Assign to Cluster 2 (closer to μ2)
```

**Assignments after Step 1:**
```
Cluster 1: {A, B}
Cluster 2: {C, D}
```

---

## 4. Step 2: Update — Recompute Centroids as Mean of Assigned Points

**New μ1 = mean of {A, B}:**
```
μ1_new_x = (1.0 + 1.5) / 2 = 1.25
μ1_new_y = (1.0 + 2.0) / 2 = 1.5

μ1_new = [1.25, 1.5]
```

**New μ2 = mean of {C, D}:**
```
μ2_new_x = (5.0 + 5.5) / 2 = 5.25
μ2_new_y = (4.0 + 5.0) / 2 = 4.5

μ2_new = [5.25, 4.5]
```

Centroids moved from:
```
μ1: [1.0, 1.0] → [1.25, 1.5]
μ2: [5.0, 4.0] → [5.25, 4.5]
```

---

## 5. Step 3: Re-Assign with New Centroids

**Point A = [1.0, 1.0]:**
```
dist(A, μ1_new) = √((1-1.25)² + (1-1.5)²) = √(0.0625+0.25) = 0.559
dist(A, μ2_new) = √((1-5.25)² + (1-4.5)²) = √(18.06+12.25) = 5.50
→ Cluster 1 ✓ (unchanged)
```

**Point B = [1.5, 2.0]:**
```
dist(B, μ1_new) = √((1.5-1.25)² + (2-1.5)²) = √(0.0625+0.25) = 0.559
dist(B, μ2_new) = √((1.5-5.25)² + (2-4.5)²) = √(14.06+6.25) = 4.51
→ Cluster 1 ✓ (unchanged)
```

Assignments are identical to Step 1 — **centroids have converged!**

---

## 6. Final Result

```
Cluster 1: {A=[1.0,1.0], B=[1.5,2.0]}   μ1 = [1.25, 1.5]
Cluster 2: {C=[5.0,4.0], D=[5.5,5.0]}   μ2 = [5.25, 4.5]
```

The algorithm found the two natural groups correctly!

---

## 7. The Inertia (What K-Means Minimizes)

K-Means minimizes the **within-cluster sum of squared distances** (inertia):

```
Cluster 1 inertia:
  dist(A, μ1)² = 0.559² = 0.312
  dist(B, μ1)² = 0.559² = 0.312
  Total: 0.624

Cluster 2 inertia:
  dist(C, μ2)² = √((5-5.25)²+(4-4.5)²)² = (0.0625+0.25) = 0.312
  dist(D, μ2)² = √((5.5-5.25)²+(5-4.5)²)² = 0.312
  Total: 0.624

Total Inertia = 0.624 + 0.624 = 1.248
```

---

## Key Takeaways

| Step | What happens |
|---|---|
| Initialize | Pick k random centroids |
| Assign | Each point goes to its nearest centroid (Euclidean distance) |
| Update | Recompute centroid = mean of all assigned points |
| Repeat | Until assignments stop changing (convergence) |
| Inertia | The objective: minimize total squared distance to assigned centroid |
| Choosing k | Use the Elbow Method: plot inertia vs k, find the "elbow" |
