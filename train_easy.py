# 🧠 train_easy.py — GRPO RL for Adaptive Quiz Tutor
import os
import torch
from datasets import Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import GRPOConfig, GRPOTrainer
from peft import LoraConfig, get_peft_model

from openenv_core_submission.models import EducationAction, EducationObservation

# 1. Configuration
MODEL_NAME = "HuggingFaceTB/SmolLM2-135M-Instruct"
OUTPUT_DIR = "./checkpoints/easy-quiz-grpo-lora"

def reward_func_accuracy(prompts, completions, answer, **kwargs):
    """Reward for correct topic select + difficulty within ZPD."""
    rewards = []
    # Simplified mock reward for training logic demonstration
    for completion in completions:
        try:
            # Check if JSON contains 'topic' and 'difficulty'
            if '"topic"' in completion and '"difficulty"' in completion:
                rewards.append(1.0)
            else:
                rewards.append(0.0)
        except:
            rewards.append(0.0)
    return rewards

def main():
    print(f"🚀 Training Easy Agent (Quiz Tutor) on {MODEL_NAME}")
    
    # 2. Dataset — In a real RL setup, this would be generated from rollout buffer
    # Here we use dummy data for the training loop script base
    dummy_data = {
        "prompt": ["Student scores: fractions=0.2, algebra=0.5. Next topic and difficulty? Output JSON:"],
        "answer": ['{"topic": "fractions", "difficulty": 1}']
    }
    dataset = Dataset.from_dict(dummy_data)

    # 3. Model & Tokenizer
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    tokenizer.pad_token = tokenizer.eos_token
    
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, torch_dtype=torch.float32)
    
    # 4. LoRA config (Memory efficient)
    peft_config = LoraConfig(
        r=4, lora_alpha=8, target_modules=["q_proj", "v_proj"],
        lora_dropout=0.05, bias="none", task_type="CAUSAL_LM"
    )
    model = get_peft_model(model, peft_config)

    # 5. GRPO Training Config
    training_args = GRPOConfig(
        output_dir=OUTPUT_DIR,
        learning_rate=5e-5,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        max_steps=50, # Demo sized
        logging_steps=10,
        save_steps=50,
        bf16=False, # CPU friendly
        push_to_hub=False,
        report_to="none"
    )

    # 6. Trainer
    trainer = GRPOTrainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        reward_funcs=[reward_func_accuracy],
    )

    print("🏋️  Starting GRPO Training (CPU Mode)...")
    trainer.train()
    
    print(f"✅ Training Complete! Model saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
