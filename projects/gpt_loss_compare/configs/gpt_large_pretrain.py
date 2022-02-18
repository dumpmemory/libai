from libai.config import LazyCall, get_config

from libai.scheduler import WarmupMultiStepLR

model = get_config("common/models/gpt.py").pretrain_model
graph = get_config("common/models/graph.py").graph
train = get_config("common/train.py").train
optim = get_config("common/optim.py").optim

# from .projects.gpt_loss_compare.configs.gpt_dataset import dataloader, tokenization
from .gpt_dataset import dataloader, tokenization

# Bert-large model config
model.cfg.embedding_dropout_prob = 0.1
model.cfg.attention_dropout_prob = 0.1
model.cfg.num_attention_heads = 16
model.cfg.hidden_size = 384
model.cfg.ffn_hidden_size = 1536
model.cfg.num_layers = 6
model.cfg.max_seq_length = 256

dataloader.train.train_val_test_datasets.seq_length = model.cfg.max_seq_length

optim.lr = 1.5e-4

train.train_micro_batch_size = 4
train.recompute_grad.enabled = True
train.output_dir = "./demo_output"
train.recompute_grad=dict(enabled=True)