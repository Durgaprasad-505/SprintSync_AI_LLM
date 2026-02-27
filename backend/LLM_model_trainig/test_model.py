# test_model.py
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import torch

# Load your trained model
base_model = AutoModelForCausalLM.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")
model = PeftModel.from_pretrained(base_model, "./sprintsync-model/final")
tokenizer = AutoTokenizer.from_pretrained("./sprintsync-model/final")

def generate_description(title: str) -> str:
    prompt = f"Task title: {title}\n\nDescription:"
    
    inputs = tokenizer(prompt, return_tensors="pt")
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=150,     # max description length
            temperature=0.7,        # creativity
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Extract only the description part
    description = response.split("Description:")[-1].strip()
    return description

# Test it
titles = [
    "Build login page",
    "Fix database connection bug",
    "Add search feature",
    "Write unit tests",
]

for title in titles:
    print(f"\nTitle: {title}")
    print(f"Description: {generate_description(title)}")