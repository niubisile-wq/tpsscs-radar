from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch
from netCDF4 import Dataset

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from evaluate_aistap_target_preservation_ablation import load_trainable_model
from evaluate_aistap_full_asset_candidate import conservative_cfar_threshold


def score_map(x: np.ndarray) -> np.ndarray:
    return np.sum(np.abs(x) ** 2, axis=0)


def low_rank_residual(x: np.ndarray, rank: int) -> np.ndarray:
    cdr = x.reshape(x.shape[0] * x.shape[1], x.shape[2])
    u, s, vh = np.linalg.svd(cdr, full_matrices=False)
    k = min(rank, s.shape[0])
    approx = (u[:, :k] * s[:k]) @ vh[:k, :]
    return (cdr - approx).reshape(x.shape)


def summarize_score(
    score: np.ndarray,
    target_mask: np.ndarray,
    background_mask: np.ndarray,
    pfas: list[float],
    policy: str,
) -> list[dict[str, Any]]:
    bg = score[background_mask]
    tgt = score[target_mask]
    rows: list[dict[str, Any]] = []
    for pfa in pfas:
        threshold, max_false_alarms = conservative_cfar_threshold(bg, pfa)
        det = score > threshold
        false_alarms = int(det[background_mask].sum()) if bg.size else 0
        rows.append(
            {
                "pfa_target": float(pfa),
                "threshold": threshold,
                "pd": float(det[target_mask].mean()) if tgt.size else float("nan"),
                "empirical_pfa": float(det[background_mask].mean()) if bg.size else float("nan"),
                "target_count": int(tgt.size),
                "background_count": int(bg.size),
                "max_false_alarms": int(max_false_alarms),
                "false_alarms": false_alarms,
                "detections": int(det.sum()),
                "threshold_policy": policy,
            }
        )
    return rows


def summarize_finished_detector(
    residual_score: np.ndarray,
    gate_score: np.ndarray,
    target_mask: np.ndarray,
    background_mask: np.ndarray,
    pfas: list[float],
) -> list[dict[str, Any]]:
    residual_bg = residual_score[background_mask]
    gate_bg = gate_score[background_mask]
    tgt = residual_score[target_mask]
    rows: list[dict[str, Any]] = []
    gate_threshold, gate_max_false_alarms = conservative_cfar_threshold(gate_bg, 0.0)
    gate_det = gate_score > gate_threshold
    for pfa in pfas:
        residual_threshold, residual_max_false_alarms = conservative_cfar_threshold(residual_bg, pfa)
        residual_det = residual_score > residual_threshold
        det = residual_det | gate_det
        false_alarms = int(det[background_mask].sum()) if residual_bg.size else 0
        rows.append(
            {
                "pfa_target": float(pfa),
                "threshold": float("nan"),
                "residual_threshold": residual_threshold,
                "gate_threshold": gate_threshold,
                "pd": float(det[target_mask].mean()) if tgt.size else float("nan"),
                "empirical_pfa": float(det[background_mask].mean()) if residual_bg.size else float("nan"),
                "target_count": int(tgt.size),
                "background_count": int(residual_bg.size),
                "max_false_alarms": int(residual_max_false_alarms + gate_max_false_alarms),
                "false_alarms": false_alarms,
                "detections": int(det.sum()),
                "threshold_policy": "residual_cfar_plus_zero_false_gate_union",
            }
        )
    return rows


def read_ipix_windows(
    cdf_path: Path,
    window: int,
    stride: int,
    max_windows: int | None,
) -> tuple[list[np.ndarray], dict[str, Any]]:
    windows: list[np.ndarray] = []
    open_path = cdf_path
    if cdf_path.is_absolute():
        try:
            open_path = cdf_path.relative_to(ROOT)
        except ValueError:
            open_path = cdf_path
    with Dataset(open_path) as ds:
        adc = ds.variables["adc_data"]
        like_i = int(ds.variables["adc_like_I"].getValue())
        like_q = int(ds.variables["adc_like_Q"].getValue())
        cross_i = int(ds.variables["adc_cross_I"].getValue())
        cross_q = int(ds.variables["adc_cross_Q"].getValue())
        nsweep = int(len(ds.dimensions["nsweep"]))
        nrange = int(len(ds.dimensions["nrange"]))
        ntxpol = int(len(ds.dimensions["ntxpol"]))
        prf = float(ds.variables["PRF"].getValue())
        ranges = np.asarray(ds.variables["range"][:], dtype=float).tolist()
        hann = np.hanning(window).astype(np.float64)
        for start in range(0, nsweep - window + 1, stride):
            if max_windows is not None and len(windows) >= max_windows:
                break
            block = np.asarray(adc[start : start + window, :, :, :], dtype=np.float64)
            channels: list[np.ndarray] = []
            for tx in range(ntxpol):
                like = block[:, tx, :, like_i] + 1j * block[:, tx, :, like_q]
                cross = block[:, tx, :, cross_i] + 1j * block[:, tx, :, cross_q]
                for signal in [like, cross]:
                    signal = signal - signal.mean(axis=0, keepdims=True)
                    rd = np.fft.fftshift(np.fft.fft(signal * hann[:, None], axis=0), axes=0)
                    channels.append(rd.T)
            windows.append(np.stack(channels, axis=0).astype(np.complex128))
    info = {
        "cdf_path": str(cdf_path),
        "window": window,
        "stride": stride,
        "windows": len(windows),
        "nrange": nrange,
        "ntxpol": ntxpol,
        "prf": prf,
        "ranges_m": ranges,
    }
    return windows, info


def evaluate(
    cdf_path: Path,
    state_path: Path,
    pfas: list[float],
    primary_bin: int,
    guard_bins: list[int],
    window: int,
    stride: int,
    max_windows: int | None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    model = load_trainable_model(state_path)
    model.eval()
    windows, info = read_ipix_windows(cdf_path, window=window, stride=stride, max_windows=max_windows)
    rows: list[dict[str, Any]] = []
    primary_idx = primary_bin - 1
    guard_idx = {b - 1 for b in guard_bins}

    with torch.no_grad():
        for window_index, x_np in enumerate(windows):
            if not (0 <= primary_idx < x_np.shape[1]):
                continue
            target_mask = np.zeros(x_np.shape[1:], dtype=bool)
            target_mask[primary_idx, :] = True
            background_mask = np.ones(x_np.shape[1:], dtype=bool)
            for idx in guard_idx:
                if 0 <= idx < background_mask.shape[0]:
                    background_mask[idx, :] = False
            x = torch.from_numpy(x_np).to(torch.complex128)
            out = model(x)
            raw_score = score_map(x_np)
            low_score = score_map(low_rank_residual(x_np, model.rank))
            model_residual_score = score_map(out["residual"].detach().cpu().numpy())
            gate_score = out["score"].detach().cpu().numpy()
            method_rows: list[tuple[str, list[dict[str, Any]]]] = [
                (
                    "raw",
                    summarize_score(raw_score, target_mask, background_mask, pfas, "conservative_topk_strict_gt"),
                ),
                (
                    f"low_rank_residual_k{model.rank}",
                    summarize_score(low_score, target_mask, background_mask, pfas, "conservative_topk_strict_gt"),
                ),
                (
                    "tpsscs_trainable_gate",
                    summarize_score(gate_score, target_mask, background_mask, pfas, "conservative_topk_strict_gt"),
                ),
                (
                    "tpsscs_finished_detector",
                    summarize_finished_detector(model_residual_score, gate_score, target_mask, background_mask, pfas),
                ),
            ]
            for method, summaries in method_rows:
                for row in summaries:
                    row.update(
                        {
                            "dataset": "IPIX_Dartmouth",
                            "file": cdf_path.name,
                            "window_index": window_index,
                            "item_id": f"{cdf_path.name}#{window_index}",
                            "method": method,
                            "primary_target_bin_1indexed": primary_bin,
                            "guard_bins_1indexed": ",".join(str(b) for b in guard_bins),
                        }
                    )
                    rows.append(row)

    info.update(
        {
            "state": str(state_path),
            "primary_target_bin_1indexed": primary_bin,
            "guard_bins_1indexed": guard_bins,
            "pfas": pfas,
        }
    )
    return pd.DataFrame(rows), info


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(Path.home() / "Desktop" / "第三批3"))
    parser.add_argument("--cdf", default="data/downloads/ipix/19931107_135603_starea.cdf")
    parser.add_argument("--state", default="results/aistap_sample/tpsscs_minimal_train_state_rank30_hidden16_steps150_lr0p02_seed7.pt")
    parser.add_argument("--primary-bin", type=int, default=9)
    parser.add_argument("--guard-bins", default="8,9,10,11")
    parser.add_argument("--window", type=int, default=1024)
    parser.add_argument("--stride", type=int, default=1024)
    parser.add_argument("--max-windows", type=int, default=128)
    parser.add_argument("--pfas", default="1e-5,3e-5,1e-4,3e-4,1e-3,3e-3,1e-2")
    parser.add_argument("--date", default=datetime.now().strftime("%Y%m%d"))
    args = parser.parse_args()

    root = Path(args.root)
    cdf_path = Path(args.cdf)
    if not cdf_path.is_absolute():
        cdf_path = root / cdf_path
    state_path = Path(args.state)
    if not state_path.is_absolute():
        state_path = root / state_path
    pfas = [float(x) for x in args.pfas.split(",") if x.strip()]
    guard_bins = [int(x) for x in args.guard_bins.split(",") if x.strip()]
    max_windows = None if args.max_windows <= 0 else args.max_windows

    df, info = evaluate(
        cdf_path=cdf_path,
        state_path=state_path,
        pfas=pfas,
        primary_bin=args.primary_bin,
        guard_bins=guard_bins,
        window=args.window,
        stride=args.stride,
        max_windows=max_windows,
    )

    result_dir = root / "results" / "ipix_external"
    log_dir = root / "logs"
    result_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    stem = cdf_path.stem
    csv_path = result_dir / f"ipix_external_detector_transfer_{stem}_{args.date}.csv"
    json_path = result_dir / f"ipix_external_detector_transfer_{stem}_{args.date}.json"
    md_path = log_dir / f"ipix_external_detector_transfer_{stem}_{args.date}.md"
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")

    summary = (
        df.groupby(["method", "pfa_target"])
        .agg(
            pd_mean=("pd", "mean"),
            pd_std=("pd", "std"),
            empirical_pfa_mean=("empirical_pfa", "mean"),
            n_windows=("item_id", "nunique"),
        )
        .reset_index()
        if not df.empty
        else pd.DataFrame()
    )
    json_path.write_text(
        json.dumps({**info, "summary": summary.to_dict(orient="records")}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines = [
        "# IPIX External Detector Transfer",
        "",
        f"Date: {args.date}",
        "",
        "## Setup",
        "",
        f"- CDF: `{cdf_path}`",
        f"- State: `{state_path}`",
        f"- Windows: `{info['windows']}`",
        f"- Window/stride: `{args.window}` / `{args.stride}` sweeps",
        f"- Primary target bin: `{args.primary_bin}` (1-indexed)",
        f"- Guard bins excluded from background: `{','.join(str(b) for b in guard_bins)}` (1-indexed)",
        "- Transform: per-channel mean removal, Hann window, FFT-shift along sweep time, range-Doppler scoring.",
        "",
        "## Detection Summary",
        "",
        "| Method | Pfa | Pd mean | Pd std | Empirical Pfa mean | Windows |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for _, row in summary.sort_values(["method", "pfa_target"]).iterrows():
        lines.append(
            f"| {row['method']} | {row['pfa_target']:.0e} | {row['pd_mean']:.4f} | {row['pd_std']:.4f} | {row['empirical_pfa_mean']:.6g} | {int(row['n_windows'])} |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This is independent non-AISTAP IPIX Dartmouth sea-clutter evidence using the published target-bin annotation for file #17.",
            "- It is a zero-shot transfer smoke test from the AISTAP-SIM-trained saved state, not an IPIX-trained detector.",
            "- It should not be used as a top-readiness pass unless the method beats raw and low-rank baselines under the same Pfa protocol.",
        ]
    )
    md_path.write_text("\n".join(lines), encoding="utf-8")

    print(csv_path)
    print(json_path)
    print(md_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
