# from datasets import load_dataset
# from transformers import (
#     AutoTokenizer,
#     AutoModelForCausalLM,
#     TrainingArguments,
# )
# from trl import SFTTrainer
# from peft import LoraConfig
# import torch

# # ── 1. Load your training data ─────────────────────────────────────────
# dataset = load_dataset("json", data_files="training_data.jsonl", split="train")

# print(f"Loaded {len(dataset)} training examples")

# # ── 2. Load base model ─────────────────────────────────────────────────
# MODEL_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"  # small, fast, free

# tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
# tokenizer.pad_token = tokenizer.eos_token

# model = AutoModelForCausalLM.from_pretrained(
#     MODEL_NAME,
#     dtype=torch.float32,         # ← correct parameter
#     device_map="auto",
# )

# # ── 3. LoRA config — fine-tunes only a small part of the model ─────────
# # This is the magic that makes fine-tuning possible on a normal laptop
# # Instead of updating all 1 billion parameters, we only update ~1 million
# lora_config = LoraConfig(
#     r=8,               # rank — how many parameters to train
#     lora_alpha=16,     # scaling factor
#     target_modules=["q_proj", "v_proj"],  # which layers to tune
#     lora_dropout=0.05,
#     bias="none",
#     task_type="CAUSAL_LM",
# )

# # ── 4. Format training examples ────────────────────────────────────────
# # NEW
# def format_example(example):
#     return {
#         "text": f"{example['prompt']}\n\nDescription: {example['completion']}<|endoftext|>"
#     }

# dataset = dataset.map(format_example, remove_columns=["prompt", "completion"])

# # ── 5. Training settings ───────────────────────────────────────────────
# training_args = TrainingArguments(
#     output_dir="./sprintsync-model",   # where to save
#     num_train_epochs=10,               # how many times to see all data
#     per_device_train_batch_size=2,     # examples per step
#     learning_rate=2e-4,                # how fast to learn
#     logging_steps=10,                  # print progress every 10 steps
#     save_steps=50,                     # save checkpoint every 50 steps
#     warmup_steps=20,
#     fp16=False,                        # set True if you have GPU
# )

# # ── 6. Train! ──────────────────────────────────────────────────────────
# trainer = SFTTrainer(
#     model=model,
#     processing_class=tokenizer,
#     train_dataset=dataset,
#     peft_config=lora_config,
#     args=training_args,
# )

# print("Starting training...")
# trainer.train()

# # ── 7. Save the trained model ──────────────────────────────────────────
# trainer.save_model("./sprintsync-model/final")
# tokenizer.save_pretrained("./sprintsync-model/final")
# print("Model saved to ./sprintsync-model/final")

from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments
from trl import SFTTrainer
from peft import LoraConfig
import torch

# 1. Load data
dataset = load_dataset("json", data_files="training_data.jsonl", split="train")
print(f"Loaded {len(dataset)} training examples")

# 2. Load base model
MODEL_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    device_map="auto",
)

# 3. LoRA config
lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)

# 4. Format dataset
def format_example(example):
    return {
        "text": f"{example['prompt']}\n\nDescription: {example['completion']}<|endoftext|>"
    }

dataset = dataset.map(format_example, remove_columns=["prompt", "completion"])

# 5. Training args
training_args = TrainingArguments(
    output_dir="./sprintsync-model",
    num_train_epochs=10,
    per_device_train_batch_size=2,
    learning_rate=2e-4,
    logging_steps=10,
    save_steps=50,
    warmup_steps=20,
    fp16=False,
)

# 6. Trainer
trainer = SFTTrainer(
    model=model,
    processing_class=tokenizer,
    train_dataset=dataset,
    peft_config=lora_config,
    args=training_args,
)

# 7. Train
print("Starting training...")
trainer.train()

# 8. Save
trainer.save_model("./sprintsync-model/final")
tokenizer.save_pretrained("./sprintsync-model/final")
print("Done! Model saved to ./sprintsync-model/final")