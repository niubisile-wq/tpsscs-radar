from __future__ import annotations

import torch
from torch import nn


class ComplexLowRankBlock(nn.Module):
    def __init__(self, rank: int = 5):
        super().__init__()
        self.rank = rank

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        if x.ndim != 3:
            raise ValueError(f"Expected (C, D, R) tensor, got {tuple(x.shape)}")
        c, d, r = x.shape
        mat = x.reshape(c * d, r)
        u, s, vh = torch.linalg.svd(mat, full_matrices=False)
        k = min(self.rank, s.shape[0])
        approx = (u[:, :k] * s[:k]) @ vh[:k, :]
        residual = mat - approx
        return residual.reshape(c, d, r), approx.reshape(c, d, r)


class TPSSCSPrototype(nn.Module):
    def __init__(self, rank: int = 5):
        super().__init__()
        self.low_rank = ComplexLowRankBlock(rank=rank)
        self.target_gate = nn.Parameter(torch.tensor(1.0, dtype=torch.float64))

    def forward(self, x: torch.Tensor) -> dict[str, torch.Tensor]:
        if x.dtype != torch.complex128:
            x = x.to(torch.complex128)
        residual, clutter = self.low_rank(x)
        gated = residual * torch.sigmoid(self.target_gate)
        score = torch.sum(torch.abs(gated) ** 2, dim=0)
        return {
            "suppressed": gated,
            "residual": residual,
            "clutter": clutter,
            "score": score,
        }

