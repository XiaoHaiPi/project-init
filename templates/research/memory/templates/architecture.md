# Architecture: <config-name>

模型结构记录应从数据输入开始，按实际前向流程记录。没有使用的结构保留标题并写 N/A。（此句为提醒）

撰写正式模型结构记录时，删除模板内所有提醒句。（此句为提醒）

所有表格列名保留字段的自然大小写，不要写成全大写；已有缩写或代码名除外。（此句为提醒）

## Overview

- Config:
- Code file:
- Main class/function:
- Parent/base config:
- Task type:

## Input

输入数据形状、模态、关键字段和进入模型前的张量格式。（此句为提醒）

| Item | Description | Code Location |
|---|---|---|

## Preprocess / Embedding

记录输入归一化、patch embedding、tokenization、positional encoding 等进入主干网络前的处理。（此句为提醒）

| Module | Structure | Purpose | Code Location |
|---|---|---|---|

## Backbone

记录 CNN、Transformer、Mamba、RNN 或其他主干特征提取结构。（此句为提醒）

| Module | Structure | Purpose | Code Location |
|---|---|---|---|

## Encoder

| Module | Structure | Purpose | Code Location |
|---|---|---|---|

## Neck / Feature Aggregation

记录 FPN、ASPP、feature pyramid、multi-scale aggregation、projection 等中间特征整合结构；没有则写 N/A。（此句为提醒）

| Module | Structure | Purpose | Code Location |
|---|---|---|---|

## Fusion

记录多模态、多分支或多尺度融合方式；没有则写 N/A。（此句为提醒）

| Module | Structure | Purpose | Code Location |
|---|---|---|---|

## Decoder

| Module | Structure | Purpose | Code Location |
|---|---|---|---|

## Head

记录 classification head、segmentation head、detection head、regression head 或 task-specific predictor；没有则写 N/A。（此句为提醒）

| Module | Structure | Purpose | Code Location |
|---|---|---|---|

## Auxiliary Branches

记录 auxiliary head、deep supervision branch、contrastive branch、regularization branch 等辅助结构；没有则写 N/A。（此句为提醒）

| Module | Structure | Purpose | Code Location |
|---|---|---|---|

## Loss

| Component | Purpose | Code Location |
|---|---|---|

## Postprocess / Inference

记录 threshold、NMS、CRF、resize、argmax、ensemble 或其他推理后处理；没有则写 N/A。（此句为提醒）

| Step | Purpose | Code Location |
|---|---|---|

## Output

记录模型输出张量、预测格式、保存格式或评估入口。（此句为提醒）

| Output | Shape / Format | Purpose | Code Location |
|---|---|---|---|

## Notes

关键设计原因，不超过 5 条。（此句为提醒）
