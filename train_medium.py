# ✍️ train_medium.py — GRPO RL for Essay Feedback Coach
import os
import torch
from datasets import Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import GRPOConfig, GRPOTrainer
from peft import LoraConfig, get_peft_model

MODEL_NAME = "HuggingFaceTB/SmolLM2-135M-Instruct"
OUTPUT_DIR = "./checkpoints/medium-essay-grpo-lora"

def reward_func_diversity(prompts, completions, **kwargs):
    """Reward for diverse feedback selection (targeting different dimensions)."""
    rewards = []
    # Simplified mock reward
    for completion in completions:
        try:
            if '"feedback_type"' in completion and '"focus_area"' in completion:
                rewards.append(1.0)
            else:
                rewards.append(0.0)
        except:
            rewards.append(0.0)
    return rewards

def main():
    print(f"🚀 Training Medium Agent (Essay Coach) on {MODEL_NAME}")
    
    # Dummy rollout data
    dummy_data = {
        "prompt": ["Essay Quality: grammar=50%, content=30%. Suggest feedback. JSON:"],
        "answer": ['{"feedback_type": "content_deepening", "focus_area": "content"}']
    }
    dataset = Dataset.from_dict(dummy_data)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, torch_dtype=torch.float32)
    
    peft_config = LoraConfig(
        r=4, lora_alpha=8, target_modules=["q_proj", "v_proj"],
        lora_dropout=0.05, bias="none", task_type="CAUSAL_LM"
    )
    model = get_peft_model(model, peft_config)

    training_args = GRPOConfig(
        output_dir=OUTPUT_DIR,
        learning_rate=5e-5,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        max_steps=50,
        logging_steps=10,
        save_steps=50,
        bf16=False,
        report_to="none"
    )

    trainer = GRPOTrainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        reward_funcs=[reward_func_diversity],
    )

    print("🏋️  Starting GRPO Training (CPU Mode)...")
    trainer.train()
    print(f"✅ Training Complete! Model saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
