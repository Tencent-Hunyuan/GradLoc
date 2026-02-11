#!/usr/bin/env bash
set -x

project_name="spike_detection"
exp_name="qwen3_4b_ins_spike_detection_test/$(date +%Y%m%d_%H%M%S)"

TRAIN_FILE_DIR="/your_path/data/qwen3-4b-s1.parquet"
VAL_FILE_DIR="/your_path/data/testset.parquet"
MODEL_PATH="/your_path/checkpoints/Qwen3-4B-Instruct-2507"
CKPTS_DIR="/your_path/spike_detection/$project_name/$exp_name"

python3 -m GradLoc.verl.trainer.main_ppo \
    algorithm.adv_estimator=grpo \
    data.train_files=${TRAIN_FILE_DIR} \
    data.val_files=${VAL_FILE_DIR} \
    data.train_batch_size=64 \
    data.max_prompt_length=2048 \
    data.max_response_length=16384 \
    data.filter_overlong_prompts=True \
    data.truncation='left' \
    actor_rollout_ref.model.path=${MODEL_PATH} \
    actor_rollout_ref.actor.strategy=fsdp \
    actor_rollout_ref.actor.optim.lr=3e-6 \
    actor_rollout_ref.model.use_remove_padding=True \
    actor_rollout_ref.actor.ppo_mini_batch_size=8 \
    actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu=1 \
    actor_rollout_ref.actor.use_kl_loss=True \
    actor_rollout_ref.actor.kl_loss_coef=0.000 \
    actor_rollout_ref.actor.kl_loss_type=low_var_kl \
    actor_rollout_ref.actor.entropy_coeff=0 \
    actor_rollout_ref.actor.spike_detection=True \
    actor_rollout_ref.actor.grad_norm_threshold=640.0 \
    actor_rollout_ref.actor.bisect_budget_steps=128 \
    actor_rollout_ref.actor.bisect_dump_dir="${CKPTS_DIR}/bisect_dump" \
    actor_rollout_ref.model.enable_gradient_checkpointing=True \
    actor_rollout_ref.actor.fsdp_config.param_offload=False \
    actor_rollout_ref.actor.fsdp_config.optimizer_offload=False \
    actor_rollout_ref.rollout.log_prob_micro_batch_size_per_gpu=1 \
    actor_rollout_ref.rollout.tensor_model_parallel_size=4 \
    actor_rollout_ref.rollout.name=vllm \
    actor_rollout_ref.rollout.gpu_memory_utilization=0.85 \
    actor_rollout_ref.rollout.n=8 \
    actor_rollout_ref.ref.log_prob_micro_batch_size_per_gpu=1 \
    actor_rollout_ref.ref.fsdp_config.param_offload=True \
    algorithm.use_kl_in_reward=False \
    trainer.critic_warmup=0 \
    trainer.logger='["console","tensorboard","wandb"]' \
    trainer.project_name="${project_name}" \
    trainer.experiment_name="${exp_name}" \
    trainer.n_gpus_per_node=8 \
    trainer.nnodes=8 \
    trainer.default_local_dir="${CKPTS_DIR}" \
    trainer.save_freq=16 \
    trainer.test_freq=128 \
    trainer.val_before_train=False \
    trainer.total_epochs=1 $@
