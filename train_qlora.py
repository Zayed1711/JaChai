#!/usr/bin/env python3
"""
JaChai E-Commerce Linguistic Router - Phase 3: QLoRA Fine-Tuning Pipeline
-------------------------------------------------------------------------
Fine-tunes Qwen/Qwen2.5-1.5B-Instruct using 4-bit QLoRA on JaChai's
2,052+ multi-lingual and Banglish e-commerce disambiguation instruction pairs.

Pipeline Architecture:
  - Base Model: Qwen/Qwen2.5-1.5B-Instruct (or Qwen/Qwen2.5-3B-Instruct)
  - Quantization: 4-bit NormalFloat (NF4) via BitsAndBytesConfig with double quantization
  - PEFT (LoRA):
      * Target Modules: q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj
      * Rank (r): 16
      * Alpha: 32
      * Dropout: 0.05
  - Training Arguments:
      * Per-device batch size: 4
      * Gradient accumulation steps: 4 (effective batch size: 16)
      * Learning rate: 2e-4 (Cosine schedule)
      * Max gradient norm: 0.3
      * Warmup ratio: 0.03
      * Mixed precision: fp16 (or bf16 on Ampere+)
  - Output Adapter: models/jachai-router-qwen2.5-lora
"""

import os
import sys
import argparse
import json
import torch

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "train_router.jsonl")
OUTPUT_DIR = os.path.join(BASE_DIR, "models", "jachai-router-qwen2.5-lora")

def parse_args():
    parser = argparse.ArgumentParser(description="JaChai Linguistic Router QLoRA Trainer")
    parser.add_argument("--model_id", type=str, default="Qwen/Qwen2.5-1.5B-Instruct", help="Hugging Face base model")
    parser.add_argument("--data_path", type=str, default=DATA_PATH, help="Path to train_router.jsonl")
    parser.add_argument("--output_dir", type=str, default=OUTPUT_DIR, help="Directory to save LoRA adapter")
    parser.add_argument("--epochs", type=int, default=3, help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=4, help="Per device batch size")
    parser.add_argument("--grad_accum", type=int, default=4, help="Gradient accumulation steps")
    parser.add_argument("--lr", type=float, default=2e-4, help="Peak learning rate")
    parser.add_argument("--max_seq_length", type=int, default=512, help="Maximum sequence length")
    parser.add_argument("--dry_run", action="store_true", help="Validate dataset and configuration without running full training")
    return parser.parse_args()

def verify_dataset(data_path: str):
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Training dataset not found at: {data_path}. Run scripts/generate_training_pairs.py first.")
    
    with open(data_path, "r", encoding="utf-8") as f:
        count = sum(1 for line in f if line.strip())
    print(f"[*] Dataset verified: {count:,} records in {data_path}")
    return count

def check_dependencies():
    missing = []
    for pkg in ["transformers", "peft", "trl", "bitsandbytes", "accelerate", "datasets"]:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    return missing

def main():
    args = parse_args()
    print("=" * 70)
    print("JaChai E-Commerce Linguistic Router - QLoRA Fine-Tuning Pipeline")
    print(f"Base Model:      {args.model_id}")
    print(f"Dataset Path:    {args.data_path}")
    print(f"Output Adapter:  {args.output_dir}")
    print(f"CUDA Available:  {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"GPU Device:      {torch.cuda.get_device_name(0)}")
        print(f"VRAM:            {torch.cuda.get_device_properties(0).total_memory / (1024**3):.2f} GB")
    print("=" * 70)

    # 1. Dataset Verification
    num_samples = verify_dataset(args.data_path)

    # 2. Dependency Check
    missing_pkgs = check_dependencies()
    if missing_pkgs:
        print(f"\n[!] Notice: Missing required packages: {', '.join(missing_pkgs)}")
        print("[*] To install required fine-tuning dependencies, run:")
        print("    pip install transformers peft trl bitsandbytes accelerate datasets\n")
        
        if not args.dry_run and not torch.cuda.is_available():
            print("[i] Dry-run verification can be run via: python train_qlora.py --dry_run")
            return

    if args.dry_run:
        print("\n[*] --- DRY-RUN VERIFICATION MODE ---")
        print(f"  [✓] Dataset path valid: {args.data_path}")
        print(f"  [✓] Total training samples: {num_samples:,}")
        print(f"  [✓] Target LoRA modules: ['q_proj', 'k_proj', 'v_proj', 'o_proj', 'gate_proj', 'up_proj', 'down_proj']")
        print(f"  [✓] Hyperparameters: r=16, lora_alpha=32, lora_dropout=0.05, lr={args.lr}")
        print(f"  [✓] Effective Batch Size: {args.batch_size} * {args.grad_accum} = {args.batch_size * args.grad_accum}")
        print(f"  [✓] Output adapter path: {args.output_dir}")
        print("[*] Dry-run validation successful!\n")
        return

    # Import libraries after dependency verification
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        BitsAndBytesConfig,
        TrainingArguments
    )
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from trl import SFTTrainer
    from datasets import load_dataset

    # 3. 4-Bit NormalFloat Quantization Setup
    use_cuda = torch.cuda.is_available()
    compute_dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16

    if use_cuda:
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=compute_dtype,
            bnb_4bit_use_double_quant=True
        )
    else:
        print("[!] Warning: CUDA is not available. Loading in standard CPU float32 mode.")
        bnb_config = None

    # 4. Load Base Tokenizer & Model
    print(f"[*] Loading tokenizer for: {args.model_id} ...")
    tokenizer = AutoTokenizer.from_pretrained(args.model_id, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    print(f"[*] Loading base model weights: {args.model_id} ...")
    model_kwargs = {
        "trust_remote_code": True,
        "device_map": "auto" if use_cuda else None
    }
    if bnb_config:
        model_kwargs["quantization_config"] = bnb_config
    else:
        model_kwargs["torch_dtype"] = torch.float32

    model = AutoModelForCausalLM.from_pretrained(args.model_id, **model_kwargs)
    
    if use_cuda:
        model = prepare_model_for_kbit_training(model)

    # 5. PEFT LoRA Configuration
    print("[*] Configuring PEFT LoRA adapter...")
    peft_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )
    model = get_peft_model(model, peft_config)
    model.print_trainable_parameters()

    # 6. Load Dataset
    print(f"[*] Loading training dataset from: {args.data_path} ...")
    dataset = load_dataset("json", data_files=args.data_path, split="train")

    def format_chat_template(batch):
        formatted_texts = []
        for messages in batch["messages"]:
            text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
            formatted_texts.append(text)
        return {"text": formatted_texts}

    dataset = dataset.map(format_chat_template, batched=True)

    # 7. Training Arguments
    training_args = TrainingArguments(
        output_dir=args.output_dir,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.lr,
        lr_scheduler_type="cosine",
        warmup_ratio=0.03,
        max_grad_norm=0.3,
        fp16=(use_cuda and not torch.cuda.is_bf16_supported()),
        bf16=(use_cuda and torch.cuda.is_bf16_supported()),
        logging_steps=10,
        save_strategy="epoch",
        save_total_limit=2,
        optim="paged_adamw_8bit" if use_cuda else "adamw_torch",
        report_to="none"
    )

    # 8. SFTTrainer Execution
    print("[*] Initializing SFTTrainer...")
    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset,
        peft_config=peft_config,
        dataset_text_field="text",
        max_seq_length=args.max_seq_length,
        tokenizer=tokenizer,
        args=training_args
    )

    print("[*] Starting QLoRA fine-tuning...")
    trainer.train()

    # 9. Save Trained LoRA Adapter
    print(f"[*] Training complete! Saving LoRA adapter to: {args.output_dir}")
    os.makedirs(args.output_dir, exist_ok=True)
    trainer.model.save_pretrained(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    print(f"[✓] Adapter successfully saved at: {args.output_dir}")

if __name__ == "__main__":
    main()

