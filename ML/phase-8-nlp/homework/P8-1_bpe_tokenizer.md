# Task P8-1: Build a BPE Tokenizer

**Goal:** Understand how text is turned into integers by implementing the exact algorithm OpenAI uses (Byte-Pair Encoding) from scratch.

Create a Jupyter Notebook in `homework/lab-files/`.

## Part 1: BPE Training
1. Download a small text corpus (e.g., a few chapters of a public domain book, or just use a long string).
2. Start by converting the text into a list of individual characters. Your initial vocabulary is just the unique characters.
3. Write a function `get_stats(ids)` that takes a list of integers and returns a dictionary of the frequencies of all adjacent pairs.
4. Write a function `merge(ids, pair, idx)` that takes a list of integers, finds all occurrences of `pair`, and replaces them with a new integer `idx`.
5. Run the training loop: Find the most frequent pair, add it to your vocabulary, and merge it in your training data. Do this for `num_merges = 20`.

## Part 2: Encode and Decode
1. Write a `decode(ids)` function that takes a list of token IDs and converts them back to the original string using your learned vocabulary merges.
2. Write an `encode(text)` function that takes a new string, converts it to characters, and iteratively applies your learned merges in the exact order they were learned.
3. **Verify:** Test that `decode(encode("some new text")) == "some new text"`.

## Part 3: Compare with Tiktoken
1. `pip install tiktoken`
2. Load the `cl100k_base` tokenizer (used by GPT-4).
3. Encode the string `"Hello, world! 123"` using your tokenizer and using `tiktoken`. Notice how `tiktoken` groups words efficiently because it has ran millions of merges!
