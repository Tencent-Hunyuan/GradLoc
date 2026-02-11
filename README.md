# 🚀 GradLoc

[![Blog](https://img.shields.io/badge/Blog-green.svg?style=for-the-badge)](https://hy.tencent.com/research/100015?langVersion=en)

Implementation patch for **GradLoc**, built on top of a fixed `verl` commit.

![From black-box heuristics to white-box diagnostics](./assets/intro.png)
*Figure 1: From black-box heuristics to white-box diagnostics for RLVR training collapse.*

## 🔍 Introduction

This repository implements the **GradLoc** part from our blog on RLVR training collapse diagnosis and stabilization.

The current release focuses on the **GradLoc** demo patch:
- **GradLoc**: localizes gradient spikes to exact culprit tokens with distributed binary search (`O(log N)`).

![GradLoc framework](./assets/framework.png)
*Figure 2: GradLoc framework. Localization proceeds from global -> micro-batch -> rank -> token with adaptive thresholds.*

This repo is intentionally lightweight and patch-oriented, so you can directly apply changes to upstream `verl` and reproduce experiments.
We plan to further package GradLoc as a cleaner, configurable feature with better veRL integration and upstream-merge readiness in future releases.

The following arguments in `run_experiment.sh` are the core runtime knobs for GradLoc.
They control trigger sensitivity, search budget, and dump path.

```bash
actor_rollout_ref.actor.grad_norm_threshold=640.0 \          # Spike trigger threshold for token-level grad norm
actor_rollout_ref.actor.bisect_budget_steps=128 \            # Max binary-search budget (forward/backward probes)
actor_rollout_ref.actor.bisect_dump_dir="${CKPTS_DIR}/bisect_dump" \  # Output dir for localization artifacts
```

## 🧩 Base commit
- Upstream: `verl`
- Commit: `f9c855f7cf04d603c9546bc01776c74806a879c1`

## 📦 Files changed by this patch
- `verl/trainer/ppo/ray_trainer.py`
- `verl/utils/reward_score/__init__.py`
- `verl/utils/reward_score/math_verify.py`
- `verl/workers/actor/dp_actor.py`

## ⚡ Quick start (online patch)
1) Clone upstream `verl` and checkout the base commit:
   - `git clone https://github.com/volcengine/verl.git`
   - `cd verl && git checkout f9c855f7cf04d603c9546bc01776c74806a879c1`
2) Apply patch from URL:
   - `python /path/to/GradLoc-Patch/apply_patch.py --repo /path/to/verl --patch-url <PATCH_URL> --sha256-file <SHA256_URL>`

## 💾 Local patch (offline)
If `patches/gradloc.patch` is already available locally:
- `python /path/to/GradLoc-Patch/apply_patch.py --repo /path/to/verl --patch-file /path/to/GradLoc-Patch/patches/gradloc.patch`

## 🧪 Run experiment
- `bash /path/to/GradLoc-Patch/run_experiment.sh`

## 🛠️ Regenerate patch after development
When code is modified on top of the base commit:
- `bash /path/to/GradLoc-Patch/make_patch.sh --repo /path/to/verl`

This rewrites `patches/gradloc.patch` from:
`git diff <base_commit> <current_head>`

## 📬 Contact Us

- Guanhua Huang: `TBD`
- Tingqiang Xu: `xtq23@mails.tsinghua.edu.cn`
- Jinbo Wang: `TBD`

## 📚 Citation

If you find this project useful, please cite:

```bibtex
@misc{huang-xu-wang-2026-gradloc,
  title = {Stabilizing RLVR via Token-level Gradient Diagnosis and Layerwise Clipping},
  author = {Huang, Guanhua and Xu, Tingqiang and Wang, Jinbo and Sheng, Guangming and Li, Siheng and Yang, Evander and Li, Kejiao and Li, Yunxiang and Xu, Zenan and Yi, Qi and Gong, Xue and Nan, Ziyuan and Jiang, Yuhao and Zhang, Chenchen and Wu, Taiqiang and Zhang, Feiyuan and Wang, Junhao and Zhou, Bo and Chen, Alex and Wang, Di and Yao, Shunyu},
  year = {2026},
  url = {https://hy.tencent.com/research/100015}
}
```
