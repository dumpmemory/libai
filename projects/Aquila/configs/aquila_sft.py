import os
from omegaconf import OmegaConf

from libai.config import LazyCall
from libai.evaluation import PPLEvaluator
from libai.scheduler import WarmupExponentialLR
from libai.data.build import build_nlp_train_loader, build_nlp_test_loader

from configs.common.train import train
from configs.common.models.graph import graph
from configs.common.optim import optim

from projects.Aquila.aquila import AquilaForCausalLM
from projects.Aquila.tokenizer import AquilaTokenizer
from projects.Aquila.configs.aquila_config import cfg
from projects.Aquila.aquila_dataset import AquilaDataset


# Hyperparameters
weight_decay = 0.1
learning_rate = 5e-5
dataset_path = "./alpaca_data"
pretrained_model_path = "/root/models/Aquila-7B"

# graph & optim
graph["enabled"] = False
optim.update(
    dict(
        lr=learning_rate,
        weight_decay=weight_decay,
    )
)

# tokenize
tokenization = OmegaConf.create()
tokenization.make_vocab_size_divisible_by = 1
tokenization.tokenizer = LazyCall(AquilaTokenizer)(
    vocab_file=pretrained_model_path + "/vocab.json",
    merges_file=pretrained_model_path + "/merges.txt",
)


# model
cfg.pretrained_model_path = pretrained_model_path
model = LazyCall(AquilaForCausalLM)(cfg=cfg)

# datasets
dataloader = OmegaConf.create()
dataloader.train = LazyCall(build_nlp_train_loader)(
    dataset=[
        LazyCall(AquilaDataset)(
            path=os.path.join(dataset_path, "train"), tokenizer=tokenization.tokenizer
        )
    ],
)
dataloader.test = [
    LazyCall(build_nlp_test_loader)(
        dataset=LazyCall(AquilaDataset)(
            path=os.path.join(dataset_path, "test"), tokenizer=tokenization.tokenizer
        ),
    ),
]

train.update(
    dict(
        output_dir="./sft_result",
        train_micro_batch_size=4,
        test_micro_batch_size=1,
        train_epoch=5,
        train_iter=1,
        log_period=1,
        warmup_ratio=1 / 3,
        num_accumulation_steps=8,
        rdma_enabled=False,
        train_with_fp16=True,
        amp=dict(enabled=True),
        activation_checkpoint=dict(enabled=True),
        input_placement_device="cuda",
        checkpointer=dict(
            period=100,
            max_to_keep=20,
        ),
        dist=dict(
            data_parallel_size=1,
            tensor_parallel_size=1,
            pipeline_parallel_size=1,
            pipeline_num_layers=cfg.hidden_layers,
            device_type="cuda",
        ),
        evaluation=dict(
            enabled=False,
            evaluator=LazyCall(PPLEvaluator)(),
            eval_period=1000,
            eval_iter=1e5,
        ),
        scheduler=LazyCall(WarmupExponentialLR)(
            warmup_factor=0.0,
            gamma=1.0,
            warmup_method="linear",
        ),
    )
)
