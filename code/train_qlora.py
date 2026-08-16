"""Single-GPU QLoRA SFT for Qwen/Qwen3.5-4B with factual corpus gates."""
from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

import torch
from datasets import load_dataset
from peft import LoraConfig
from transformers import AutoProcessor, AutoModelForImageTextToText, BitsAndBytesConfig
from trl import SFTConfig, SFTTrainer


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", required=True)
    parser.add_argument("--eval", required=True)
    parser.add_argument("--data-report", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--hub-model-id", default=None)
    parser.add_argument("--telemetry-dir", default=None, help="Persistent TensorBoard metrics directory")
    parser.add_argument("--allow-synthetic-prompt-augmentation", action="store_true")
    parser.add_argument("--max-steps", type=int, default=-1, help="Positive value for a bounded smoke run")
    parser.add_argument("--epochs", type=float, default=1.0)
    parser.add_argument("--per-device-train-batch-size", type=int, default=1)
    parser.add_argument("--gradient-accumulation-steps", type=int, default=16)
    parser.add_argument("--max-length", type=int, default=2048)
    parser.add_argument("--packing", action="store_true", help="Pack short, EOS-delimited examples into max-length sequences")
    parser.add_argument("--resume-from-checkpoint", default=None)
    parser.add_argument("--push-to-hub", action="store_true", help="Require an authenticated write credential")
    args = parser.parse_args()
    report = json.loads(Path(args.data_report).read_text())
    synthetic = report.get("status") in {"synthetic_augmentation_ready", "procedural_synthetic_ready"}
    if synthetic and not args.allow_synthetic_prompt_augmentation:
        raise RuntimeError("Synthetic prompt augmentation requires explicit --allow-synthetic-prompt-augmentation")
    if not synthetic and (report.get("status") != "ready" or report.get("synthetic_targets") != 0):
        raise RuntimeError("Corpus is not a verified ready corpus")
    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16, bnb_4bit_use_double_quant=True)
    processor = AutoProcessor.from_pretrained("Qwen/Qwen3.5-4B")
    model = AutoModelForImageTextToText.from_pretrained("Qwen/Qwen3.5-4B", quantization_config=bnb, torch_dtype=torch.bfloat16, device_map="auto")
    telemetry_dir = args.telemetry_dir or str(Path(args.output) / "telemetry" / "tensorboard")
    Path(telemetry_dir).mkdir(parents=True, exist_ok=True)
    if args.push_to_hub and not args.hub_model_id:
        raise RuntimeError("--hub-model-id is required with --push-to-hub")
    config = SFTConfig(output_dir=args.output, num_train_epochs=args.epochs, max_steps=args.max_steps, per_device_train_batch_size=args.per_device_train_batch_size, gradient_accumulation_steps=args.gradient_accumulation_steps, learning_rate=1e-4, lr_scheduler_type="cosine", warmup_steps=1000, max_length=args.max_length, packing=args.packing, bf16=True, gradient_checkpointing=True, logging_steps=10, save_strategy="steps", save_steps=250, eval_strategy="steps", eval_steps=250, report_to=["tensorboard"], push_to_hub=args.push_to_hub, hub_model_id=args.hub_model_id, hub_private_repo=True)
    train_files = glob.glob(args.train) or [args.train]
    eval_files = glob.glob(args.eval) or [args.eval]
    trainer = SFTTrainer(model=model, args=config, train_dataset=load_dataset("json", data_files=train_files, split="train"), eval_dataset=load_dataset("json", data_files=eval_files, split="train"), processing_class=processor, peft_config=LoraConfig(r=32, lora_alpha=64, lora_dropout=0.05, target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"], task_type="CAUSAL_LM"))
    trainer.train(resume_from_checkpoint=args.resume_from_checkpoint)
    trainer.save_model(args.output)
    if args.push_to_hub:
        trainer.push_to_hub()


if __name__ == "__main__":
    main()
