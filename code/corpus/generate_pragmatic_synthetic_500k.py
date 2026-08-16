#!/usr/bin/env python3
"""Generate five declared procedural-synthetic SFT shards (100k each).

The examples are structurally diverse and uniquely indexed, but they are not
teacher-generated conversations and must never be represented as human data.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

SHARDS = {
 "pragmatic_systems": ("pragmatic systems design", ["RAG incident triage", "agent workflow", "model serving", "training pipeline", "developer tool"], ["latency", "cost", "reliability", "privacy", "operator time"]),
 "first_principles": ("first-principles reasoning", ["AI product", "research plan", "infrastructure decision", "personal learning system", "safety boundary"], ["physics", "information", "incentives", "compute", "verification"]),
 "second_order_inversion": ("second-order and inversion analysis", ["automation rollout", "open-source strategy", "data flywheel", "deployment choice", "career investment"], ["lock-in", "tail risk", "perverse incentives", "maintenance debt", "false confidence"]),
 "systems_thinking": ("systems thinking with feedback loops, delays, and leverage points", ["AI operations platform", "learning ecosystem", "research organization", "model deployment fleet", "human-AI institution"], ["local optimization", "hidden feedback loops", "delayed failures", "bottleneck migration", "metric gaming"]),
 "game_theory": ("game-theoretic strategy", ["multi-agent market", "developer platform", "open model community", "AI safety protocol", "research collaboration"], ["credible commitment", "adverse selection", "coordination", "defection", "information asymmetry"]),
 "speculative_transhumanism": ("pragmatic speculative and transhumanist analysis", ["brain-computer interface", "AI copilot", "longevity platform", "autonomous lab", "human-AI institution"], ["consent", "reversibility", "power concentration", "identity continuity", "access inequality"]),
}
STEPS = ["measure the baseline", "write the smallest falsifiable hypothesis", "build a reversible prototype", "instrument the failure modes", "promote only after a predeclared gate"]

def text_for(i: int, lens: str, subjects: list[str], risks: list[str]) -> tuple[str, str]:
    subject, risk = subjects[i % len(subjects)], risks[(i // len(subjects)) % len(risks)]
    horizon = ["this week", "this quarter", "over three years", "under adversarial pressure", "at civilization scale"][i % 5]
    prompt = f"Analyze a {subject} using {lens}. The dominant concern is {risk}; make a decision for {horizon}. Scenario #{i:06d}. Give an actionable answer, not generic motivation."
    answer = (f"Decision: treat the {subject} as a constrained experiment, not a narrative.\n\n"
      f"First principles: the scarce resource is trustworthy feedback. Optimize the system for observable outcomes, while treating {risk} as a hard design constraint.\n\n"
      f"Plan: 1) {STEPS[i % 5]}; 2) {STEPS[(i+1) % 5]}; 3) {STEPS[(i+2) % 5]}.\n\n"
      f"Second-order check: success can amplify {risk} through scale, incentives, and path dependence. Keep an exit path, publish the operating assumptions, and stop if the measured downside crosses the precommitted threshold.\n\n"
      f"Evidence gate: record latency/cost/error data, an operator review, and a counterfactual comparison before expanding scope. Scenario #{i:06d} is synthetic; it is a reasoning drill, not a claim about the world.")
    return prompt, answer

def main() -> None:
 p=argparse.ArgumentParser(); p.add_argument("--out-dir",type=Path,required=True); p.add_argument("--per-shard",type=int,default=100_000); args=p.parse_args(); args.out_dir.mkdir(parents=True,exist_ok=True)
 manifest=[]
 for shard,(lens,subjects,risks) in SHARDS.items():
  path=args.out_dir/f"{shard}.jsonl"; digest=hashlib.sha256()
  with path.open("w",encoding="utf-8") as f:
   for i in range(args.per_shard):
    prompt,answer=text_for(i,lens,subjects,risks)
    row={"messages":[{"role":"system","content":"Be pragmatic, logically explicit, evidence-aware, and willing to reason about ambitious futures without pretending speculation is fact."},{"role":"user","content":prompt},{"role":"assistant","content":answer}],"provenance":{"kind":"procedural_synthetic","shard":shard,"id":i,"human_authored":False}}
    line=json.dumps(row,ensure_ascii=False)+"\n"; f.write(line); digest.update(line.encode())
  manifest.append({"shard":shard,"examples":args.per_shard,"sha256":digest.hexdigest(),"kind":"procedural_synthetic"})
 report={"total_examples":args.per_shard*len(SHARDS),"shards":manifest,"human_authored_examples":0,"status":"procedural_synthetic_ready"}; (args.out_dir/"manifest.json").write_text(json.dumps(report,indent=2)+"\n"); print(json.dumps(report))
if __name__=="__main__": main()
