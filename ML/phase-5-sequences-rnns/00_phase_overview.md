# Phase 5: Sequence Models & RNNs

> **Goal:** Understand how to process time-series and sequential data. This is the stepping stone to Transformers.
> **Duration:** 2 weeks

## The Problem with Sequences
Standard neural networks require fixed-size inputs. But text and time-series have variable lengths.

## Recurrent Neural Networks (RNNs)
RNNs process sequences step-by-step, maintaining an internal **hidden state** (memory) that is updated at each step.
- *Flaw:* **Vanishing Gradients.** They forget early inputs in long sequences.

## LSTMs and GRUs
Long Short-Term Memory (LSTM) networks introduced **gates** to control what information is kept, forgotten, or added to the memory state.
- They largely solved the vanishing gradient problem.
- *Flaw:* They are inherently sequential. You can't process step 100 until you've processed steps 1-99. This makes them slow to train on GPUs.

## Homework
- Complete `homework/P5-1_lstm_forecasting.md`
