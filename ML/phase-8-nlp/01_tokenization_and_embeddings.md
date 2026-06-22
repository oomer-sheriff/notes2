# Tokenization and Embeddings

Before a neural network can process text, the text must be converted into numbers. This happens in two stages:
1. **Tokenization:** Break text into discrete chunks (tokens) and assign each an integer ID.
2. **Embedding:** Map each integer ID to a dense vector of floating-point numbers.

---

## Part 1: Tokenization

How do we split a string like `"I love AI!"`?

### Option 1: Character-Level
`['I', ' ', 'l', 'o', 'v', 'e', ' ', 'A', 'I', '!']`
- **Pros:** Tiny vocabulary (e.g., 256 ASCII chars or ~100k Unicode). Never encounters an "Unknown" token.
- **Cons:** A single sentence becomes hundreds of tokens. The model has to learn that 'c', 'a', 't' together mean something furry. Very inefficient context window usage.

### Option 2: Word-Level
`['I', 'love', 'AI', '!']`
- **Pros:** Each token has intrinsic meaning. Short sequences.
- **Cons:** Vocabulary explosion. There are millions of words, plus typos, plus capitalization (`Cat` vs `cat`). What happens when it sees a word it wasn't trained on (e.g., `"ChatGPT"`)? It gets mapped to `[UNK]` (Unknown), destroying information.

### Option 3: Subword Tokenization (The Sweet Spot)
This is what all modern LLMs use (BPE, WordPiece, SentencePiece).
It breaks down rare words into common subwords, but keeps frequent words intact.

`"unhappiness"` → `["un", "happi", "ness"]`
`"ChatGPT"` → `["Chat", "G", "PT"]`

---

## Byte-Pair Encoding (BPE)

BPE is the algorithm used by GPT-2, GPT-3, and GPT-4. It is a data compression algorithm adapted for NLP.

**How BPE is trained (Algorithm):**
1. Start with a vocabulary of individual characters.
   `vocab = {'a', 'b', 'c', ..., 'z'}`
2. Scan the training corpus and count the frequency of all adjacent token pairs.
   `(s, t): 500, (t, h): 450, (e, r): 300`
3. Find the most frequent pair and merge it into a new single token. Add it to the vocab.
   `vocab.add('st')`
4. Repeat this process $N$ times (where $N$ is your target vocabulary size, e.g., 50,000).

**Example Trace:**
Corpus: `"low low lowest newer newer"`
Initial split: `l o w`, `l o w`, `l o w e s t`, `n e w e r`, `n e w e r`
Most frequent pair: `(e, r)` occurs twice. Merge to `er`.
Next: `(l, o)` occurs 3 times. Merge to `lo`.
Next: `(lo, w)` occurs 3 times. Merge to `low`.

Resulting vocabulary now contains the whole word `low`, the subword `er`, etc.

**Why is this brilliant?**
- Common words like `"the"` or `"computer"` get merged into a single token (efficient).
- Rare or completely made up words like `"snorklewacker"` get broken into subwords `["sn", "ork", "le", "wack", "er"]`. The model can still process them without throwing an `[UNK]` error, and might even infer meaning from the prefixes/suffixes!

---

## Part 2: Embeddings

Once we have a sequence of token IDs like `[45, 1209, 8, 30]`, we need to feed them into a neural network.

You *cannot* just pass the integer `1209`. Why? Because integers imply an ordering. The network would think that token `1209` is somehow "greater than" token `45`, which is mathematically nonsensical for words.

We use an **Embedding Layer**. Think of it as a simple lookup table.

```python
import torch
import torch.nn as nn

vocab_size = 50000
d_model = 256  # Dimension of the vector

# Create the embedding table: a matrix of size (50000, 256)
embedding = nn.Embedding(num_embeddings=vocab_size, embedding_dim=d_model)

token_id = torch.tensor([1209])
vector = embedding(token_id)
print(vector.shape)  # Output: [1, 256]
```

### What do these vectors represent?

Initially, the 256 numbers in the vector are completely random. As the network trains (e.g., predicting the next word), it adjusts these vectors via backpropagation.

Eventually, the vectors organize themselves in a high-dimensional space such that **semantically similar words are grouped together**.

- `vector("king")` will be near `vector("queen")` and `vector("prince")`
- `vector("dog")` will be near `vector("cat")`

**Vector Math:**
Famously, you can do linear algebra on these learned vectors:
`vector("King") - vector("Man") + vector("Woman") ≈ vector("Queen")`

### Contextual vs Static Embeddings
- **Static (Word2Vec, GloVe):** The word `"bank"` always gets the exact same vector, whether you mean "river bank" or "Chase bank".
- **Contextual (Transformers - BERT, GPT):** The initial embedding is static, but as it passes through the self-attention layers of the Transformer, it gathers information from surrounding words. The *final* vector for `"bank"` will be completely different in "river bank" vs "Chase bank".

---
## References
*   [Andrej Karpathy: Let's build the GPT Tokenizer](https://www.youtube.com/watch?v=zduSFxRajkE)
*   [Sennrich et al. (2015): Neural Machine Translation of Rare Words with Subword Units (BPE paper)](https://arxiv.org/abs/1508.07909)
*   [Mikolov et al. (2013): Efficient Estimation of Word Representations in Vector Space (Word2Vec)](https://arxiv.org/abs/1301.3781)
