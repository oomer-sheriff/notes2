# Task P8-3: Fine-Tune an LLM with LoRA

**Goal:** Fine-tune a causal language model to follow a specific style using Parameter-Efficient Fine-Tuning (PEFT) and LoRA.

Create a Jupyter Notebook in `homework/lab-files/`. **Run on Google Colab (T4 GPU).**

## Part 1: The Base Model
1. `pip install transformers peft accelerate bitsandbytes datasets`
2. Load a small, base language model like `gpt2` or `TinyLlama/TinyLlama-1.1B-intermediate-step-1431k-3T`.
3. Try prompting the base model with: `"To bake a chocolate cake, you need"`
4. Notice how it likely just continues the sentence or rambles, because it hasn't been instruction-tuned.

## Part 2: Preparing the LoRA Adapters
1. We cannot fine-tune all 1.1 Billion parameters on a Colab GPU. We will use LoRA.
2. Initialize a `LoraConfig`:
   ```python
   from peft import LoraConfig, get_peft_model
   config = LoraConfig(
       r=8, 
       lora_alpha=32, 
       target_modules=["c_attn"] if "gpt2" in model.name_or_path else ["q_proj", "v_proj"],
       lora_dropout=0.05,
       bias="none",
       task_type="CAUSAL_LM"
   )
   model = get_peft_model(model, config)
   ```
3. Call `model.print_trainable_parameters()`. You should see that you are only training around 0.1% to 1% of the total parameters!

## Part 3: The Dataset and Training
1. Choose a tiny dataset from Hugging Face, such as `Abirate/english_quotes` (which contains quotes and their authors).
2. Format the dataset so the model learns to output the author when given a quote:
   `"Quote: {quote} \nAuthor: {author} <|endoftext|>"`
3. Use the Hugging Face `Trainer` to fine-tune the model for a few hundred steps.

## Part 4: Inference
1. After training, prompt the model with a new quote:
   `"Quote: I think, therefore I am. \nAuthor:"`
2. The model should now perfectly format its response and provide the author, stopping at `<|endoftext|>`.
3. You have successfully aligned the model to your specific task using only a tiny fraction of the computational cost!
