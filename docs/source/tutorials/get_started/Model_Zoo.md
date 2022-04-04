# LiBai Model Zoo
To date, LiBai implements the following models:
- [Vision Transformer](https://arxiv.org/abs/2010.11929)
- [Swin Transformer](https://arxiv.org/abs/2103.14030)
- [BERT](https://arxiv.org/abs/1810.04805)
- [T5](https://arxiv.org/abs/1910.10683)
- [GPT-2](https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf)


## Parallelism Mode in LiBai
A collection of parallel training strategies is supported in LiBai:
- **Data Parallel Training**
- **Tensor Parallel Training**
- **Pipeline Parallel Training**

You can refer to oneflow official [tutorial](https://docs.oneflow.org/en/master/parallelism/01_introduction.html) for a better understanding of the basic conception of parallelization techniques.


## Supported Model in LiBai

For more details about the supported parallelism training on different models, please refer the following tables:

<table class="docutils">
  <tbody>
    <tr>
      <th width="80"> Model </th>
      <th valign="bottom" align="left" width="120">Data Parallel</th>
      <th valign="bottom" align="left" width="120">Tensor Parallel</th>
      <th valign="bottom" align="left" width="120">Pipeline Parallel</th>
    </tr>
    <tr>
      <td align="left"> <b> Vision Transformer </b> </td>
      <td align="left">&#10004;</td>
      <td align="left">&#10004;</td>
      <td align="left">&#10004;</td>
    </tr>
    <tr>
      <td align="left"> <b> Swin Transformer </b> </td>
      <td align="left">&#10004;</td>
      <td align="left">-</td>
      <td align="left">-</td>
    <tr>
      <td align="left"> <b> BERT </b> </td>
      <td align="left">&#10004;</td>
      <td align="left">&#10004;</td>
      <td align="left">&#10004;</td>
    </tr>
    <tr>
      <td align="left"> <b> T5 </b> </td>
      <td align="left">&#10004;</td>
      <td align="left">&#10004;</td>
      <td align="left">&#10004;</td>
    </tr>
    <tr>
      <td align="left"> <b> GPT-2 </b> </td>
      <td align="left">&#10004;</td>
      <td align="left">&#10004;</td>
      <td align="left">&#10004;</td>
    </tr>
    </tr>
  </tbody>
</table>

**Additions:**
&#10004; means you can train this model under specific parallelism techniques or combine two or three of them with &#10004; for 2D or 3D paralleism training.

## Benchmarks (coming soon)
Here we provided our benchmark test results of the supported models in LiBai. Due to our resource constraints, we will gradually release the training results in the future.

### Main Results on ImageNet with Pretrained Models

**ImageNet-1K Pretrained Models**
<table class="docutils">
  <tbody>
    <tr>
      <th width="80"> Model </th>
      <th valign="bottom" align="center" width="120">Pretrain</th>
      <th valign="bottom" align="center" width="120">Resolution</th>
      <th valign="bottom" align="center" width="120">Acc@1</th>
      <th valign="bottom" align="center" width="120">Acc@5</th>
      <th valign="bottom" align="center" width="120">Download</th>
    </tr>
    <tr>
      <td align="center"> ViT-Tiny </td>
      <td align="center"> ImageNet-1K </td>
      <td align="center"> 224x224 </td>
      <td align="center"> 72.7 </td>
      <td align="center"> 91.0 </td>
      <td align="center"> <a href="https://oneflow-public.oss-cn-beijing.aliyuncs.com/model_zoo/LiBai/ImageNet/vit_tiny_patch16_224/config.yaml">Config</a> | <a href="https://oneflow-public.oss-cn-beijing.aliyuncs.com/model_zoo/LiBai/ImageNet/vit_tiny_patch16_224/model_best.zip">Checkpoint</a> </td>
    </tr>
    </tr>
  </tbody>
</table>