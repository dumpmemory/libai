# coding=utf-8
# Copyright 2021 The OneFlow Authors. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from pathlib import Path
from typing import Union

import click

from libai.config import try_get_key
from libai.engine import DefaultTrainer
from libai.inference.basic import BasePipeline
from libai.utils import distributed as dist


class TextGenerationPipeline(BasePipeline):
    def load_pretrain_weight(self, libai_cfg_model, model_path, mode="huggingface"):
        """load pretrained model.

        Args:
            libai_cfg_model (libai.models): Lazy config Model in Libai, you can import it
                by `from libai.config.configs.common.models.bert
                    import pretrain_model as libai_cfg_model`
            model_path (str): The directory path of pretrained model,
        """
        if mode == "huggingface":
            from projects.ChatGLM.utils.chatglm_loader import (
                ChatGLMLoaderHuggerFace,
                ChatGLMLoraLoaderHuggerFace,
            )

            if libai_cfg_model.cfg.lora_enable:
                libai_cfg_model.cfg.lora_cfg.inference_mode = True
                model_loader = ChatGLMLoraLoaderHuggerFace(
                    libai_cfg_model,
                    libai_cfg_model.cfg,
                    libai_cfg_model.cfg.pretrained_model_path,
                    lora_cfg=libai_cfg_model.cfg.lora_cfg,
                    # lora_pretrained_model_path = libai_cfg_model.cfg.lora_pretrained_model_path
                    lora_pretrained_model_path=model_path,
                )
            else:
                model_loader = ChatGLMLoaderHuggerFace(
                    libai_cfg_model,
                    libai_cfg_model.cfg,
                    model_path,
                )
            model = model_loader.load()
            model.eval()
            return model

        elif mode == "libai":
            from projects.ChatGLM.utils.chatglm_loader import (
                ChatGLMLoaderLiBai,
                ChatGLMLoraLoaderLiBai,
            )

            if libai_cfg_model.cfg.lora_enable:
                libai_cfg_model.cfg.lora_cfg.inference_mode = True
                model_loader = ChatGLMLoraLoaderLiBai(
                    libai_cfg_model,
                    libai_cfg_model.cfg,
                    libai_cfg_model.cfg.pretrained_model_path,
                    lora_cfg=libai_cfg_model.cfg.lora_cfg,
                    # lora_pretrained_model_path = libai_cfg_model.cfg.lora_pretrained_model_path
                    lora_pretrained_model_path=model_path,
                )
            else:
                model_loader = ChatGLMLoaderLiBai(
                    libai_cfg_model,
                    libai_cfg_model.cfg,
                    model_path,
                )
            model = model_loader.load()
            model.eval()
            return model

        elif mode == "random":
            # from libai.engine import DefaultTrainer

            return DefaultTrainer.build_model(self.cfg)
        else:
            raise NotImplementedError

    def _parse_parameters(self, **pipeline_parameters):
        preprocess_params = {}
        forward_params = {**pipeline_parameters}
        postprocess_params = {}

        return preprocess_params, forward_params, postprocess_params

    def preprocess(self, sentence: Union[str, list], **kwargs) -> dict:
        #
        if type(sentence) is str:
            inputs = {
                "inputs": sentence,
            }
        else:
            inputs = self.tokenizer.encode(
                sentence, return_tensors="of", is_global=True, device=self.device
            )
            inputs = {
                "input_ids": inputs,
            }
        return inputs

    def build_tokenizer(self, cfg):
        tokenizer = None
        if try_get_key(cfg, "tokenization") is not None:
            tokenizer_cfg = cfg.tokenization.tokenizer
            if "vocab_file" not in tokenizer_cfg:
                # If "vocab_file" does not exist in the tokenizer's config,
                # set it to default as f"{model_path}/tokenizer.model"
                tokenizer_cfg.vocab_file = str(Path(self.model_path).joinpath("tokenizer.model"))
            tokenizer = DefaultTrainer.build_tokenizer(cfg)
        return tokenizer

    def forward(self, inputs, **kwargs) -> dict:
        if "input_ids" not in inputs:
            if "history" in kwargs:
                history = kwargs.pop("history")
            else:
                if not hasattr(self, "history"):
                    self.history = []
                history = self.history

            response, history = self.model.chat(
                self.tokenizer, inputs["inputs"], history=history, **kwargs
            )
            self.history = history
            return {"response": response, "history": history}
        else:
            outputs = self.model.generate(inputs["input_ids"], **kwargs)[
                :, inputs["input_ids"].size(1) : -1
            ]
            return {"return_ids": outputs}

    def postprocess(self, model_output_dict, **kwargs) -> dict:
        if "response" in model_output_dict:
            records = [{"generated_text": model_output_dict["response"]}]
            return records
        else:
            return_ids = model_output_dict["return_ids"]
            records = [
                {"generated_text": self.tokenizer.decode(return_ids[i])}
                for i in range(return_ids.size(0))
            ]
            return records

    def reset_conversation(self):
        self.history = []


@click.command()
@click.option(
    "--config_file",
    default="projects/ChatGLM/configs/chatglm_config.py",
    help="Path to the configuration file.",
)
@click.option("--model_path", default=None, help="Path to the model checkpoint.")
@click.option(
    "--mode",
    default="libai",
    help="Mode for the dataloader pipeline, e.g., 'libai' or 'huggingface'.",
)
@click.option(
    "--device", default="cuda", help="Device to run the model on, e.g., 'cuda', 'xpu', 'npu'."
)
def main(config_file, model_path, mode, device):
    text = "浏览器输入www.baidu.com 并且显示网页，从计算机网络的角度说明实现的全过程"
    text2 = (
        "5600分为A、B、C三部分，如果A比C的比例是1/7:1/7:1/14，那么A比C多多少？\n"
        "选项：\n(A) 300\n(B) 992 \n(C) 1120\n(D) 552\n(E) 312 让我们先想想。一些随机推理："
    )
    texts = [
        text,
        text2,
        "a dog is flying on the sky",
        "Wikipedia is a free online",
        "what is beam search?",
        "what is beam search?",
    ]
    pipeline = TextGenerationPipeline(
        config_file,
        data_parallel=1,
        tensor_parallel=1,
        pipeline_parallel=1,
        pipeline_num_layers=28,
        model_path=model_path,
        mode=mode,
        device=device,
    )
    pipeline.model = pipeline.model.half()

    if isinstance(texts, list):
        output = pipeline(inputs=texts, do_sample=False, max_length=400)
        if dist.is_main_process():
            for text, record in zip(texts, output):
                print(f"Q:{text}||A:{record}")


if __name__ == "__main__":
    main()
