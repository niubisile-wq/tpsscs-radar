# Baseline Card

## 传统雷达方法

- MTI
- DPCA
- CA-CFAR
- OS-CFAR
- GO-CFAR
- SMI-STAP
- diagonal loading STAP
- reduced-rank STAP
- AMF
- NAMF
- ACE

## 低秩与稀疏方法

- SVD clutter cancellation
- PCA clutter suppression
- RPCA
- GoDec
- SSA
- low-rank plus sparse decomposition

## 时频与经验分解

- wavelet denoising
- EMD
- VMD
- notch filtering

## 深度学习方法

- real-valued U-Net
- complex U-Net
- DnCNN-style denoiser
- VAE
- complex VAE
- self-supervised blind-spot variant

## 冻结原则

- Baseline 定义先冻结，再做 TP-SSCS。
- 所有 baseline 使用同一套 split 和 target injection protocol。
- 所有阈值只能在 validation 上调，不可碰 test。

