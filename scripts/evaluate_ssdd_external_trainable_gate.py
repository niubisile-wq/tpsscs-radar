from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import pandas as pd
from PIL import Image
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


PFAS = [1e-5, 3e-5, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2]
ALPHAS = [0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.3]
FREEZE_QUANTILES = [0.95, 0.97, 0.99, 0.995, 0.997, 0.999]
RANK = 5
STRICT_RAW_FALLBACK_MAX_PFA = 1e-4


@dataclass
class EvalRow:
    pfa: float
    selected_policy: str
    candidate_pd: float
    raw_pd: float
    lowrank_pd: float
    candidate_empirical_pfa: float
    beats_raw: bool
    ties_raw: bool
    beats_or_ties_raw: bool
    beats_lowrank: bool


def zscore(x: np.ndarray) -> np.ndarray:
    x = x.astype(np.float32)
    return ((x - x.mean()) / (x.std() + 1e-6)).astype(np.float32)


def load_coco(path: Path) -> tuple[dict[int, dict[str, Any]], dict[int, list[dict[str, Any]]]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    images = {int(im["id"]): im for im in data.get("images", [])}
    anns: dict[int, list[dict[str, Any]]] = {image_id: [] for image_id in images}
    for ann in data.get("annotations", []):
        anns.setdefault(int(ann["image_id"]), []).append(ann)
    return images, anns


def masks(height: int, width: int, anns: list[dict[str, Any]]) -> tuple[np.ndarray, np.ndarray]:
    target = np.zeros((height, width), dtype=np.uint8)
    guard = np.zeros((height, width), dtype=np.uint8)
    for ann in anns:
        segs = ann.get("segmentation") or []
        for seg in segs:
            pts = np.asarray(seg, dtype=np.float32).reshape(-1, 2)
            pts[:, 0] = np.clip(pts[:, 0], 0, width - 1)
            pts[:, 1] = np.clip(pts[:, 1], 0, height - 1)
            cv2.fillPoly(target, [np.rint(pts).astype(np.int32)], 1)
        if not segs:
            x, y, box_w, box_h = ann["bbox"]
            x0 = max(0, int(np.floor(x)))
            y0 = max(0, int(np.floor(y)))
            x1 = min(width, int(np.ceil(x + box_w)))
            y1 = min(height, int(np.ceil(y + box_h)))
            target[y0:y1, x0:x1] = 1

        x, y, box_w, box_h = ann["bbox"]
        pad = max(4, int(round(0.5 * max(box_w, box_h))))
        x0 = max(0, int(np.floor(x - pad)))
        y0 = max(0, int(np.floor(y - pad)))
        x1 = min(width, int(np.ceil(x + box_w + pad)))
        y1 = min(height, int(np.ceil(y + box_h + pad)))
        guard[y0:y1, x0:x1] = 1
    return target.astype(bool), guard == 0


def score_components(image_path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    image = np.asarray(Image.open(image_path).convert("L"), dtype=np.float32)
    raw = zscore(np.log1p(image))
    u, s, vt = np.linalg.svd(raw, full_matrices=False)
    k = min(RANK, len(s))
    lowrank = (u[:, :k] * s[:k]) @ vt[:k, :]
    residual = zscore(np.abs(raw - lowrank))
    blur = cv2.GaussianBlur(raw, (0, 0), sigmaX=5, sigmaY=5)
    local = zscore(raw - blur)
    mean = cv2.GaussianBlur(raw, (0, 0), sigmaX=7, sigmaY=7)
    mean2 = cv2.GaussianBlur(raw * raw, (0, 0), sigmaX=7, sigmaY=7)
    local_z = zscore((raw - mean) / (np.sqrt(np.maximum(mean2 - mean * mean, 1e-6)) + 1e-6))
    features = np.stack(
        [
            raw,
            residual,
            local,
            local_z,
            raw * residual,
            raw * local,
            raw * local_z,
            residual * local,
        ],
        axis=-1,
    ).astype(np.float32)
    return raw, residual, features


def split_train_ids(image_ids: list[int]) -> tuple[set[int], set[int]]:
    ids = sorted(image_ids)
    validation = {image_id for idx, image_id in enumerate(ids) if idx % 5 == 0}
    development = set(ids) - validation
    return development, validation


def sample_development(
    dataset_root: Path,
    image_ids: set[int],
    images: dict[int, dict[str, Any]],
    anns: dict[int, list[dict[str, Any]]],
    seed: int,
    max_target_per_image: int,
    max_background_per_image: int,
) -> tuple[np.ndarray, np.ndarray, dict[str, int]]:
    rng = np.random.default_rng(seed)
    xs: list[np.ndarray] = []
    ys: list[np.ndarray] = []
    meta = {"images": 0, "target_samples": 0, "background_samples": 0}
    for image_id in sorted(image_ids):
        image_meta = images[image_id]
        image_path = dataset_root / "images" / "train" / image_meta["file_name"]
        if not image_path.exists():
            continue
        target, background = masks(image_meta["height"], image_meta["width"], anns.get(image_id, []))
        if target.sum() == 0 or background.sum() == 0:
            continue
        _, _, features = score_components(image_path)
        flat = features.reshape(-1, features.shape[-1])
        target_idx = np.flatnonzero(target.ravel())
        background_idx = np.flatnonzero(background.ravel())
        if len(target_idx) > max_target_per_image:
            target_idx = rng.choice(target_idx, max_target_per_image, replace=False)
        if len(background_idx) > max_background_per_image:
            background_idx = rng.choice(background_idx, max_background_per_image, replace=False)
        xs.extend([flat[target_idx], flat[background_idx]])
        ys.extend([np.ones(len(target_idx), dtype=np.uint8), np.zeros(len(background_idx), dtype=np.uint8)])
        meta["images"] += 1
        meta["target_samples"] += int(len(target_idx))
        meta["background_samples"] += int(len(background_idx))
    return np.vstack(xs), np.concatenate(ys), meta


def collect_split(
    dataset_root: Path,
    split: str,
    image_ids: set[int],
    images: dict[int, dict[str, Any]],
    anns: dict[int, list[dict[str, Any]]],
    model: Any,
) -> dict[str, Any]:
    out: dict[str, list[np.ndarray]] = {
        "raw_t": [],
        "raw_b": [],
        "lowrank_t": [],
        "lowrank_b": [],
        "gate_t": [],
        "gate_b": [],
    }
    for q in FREEZE_QUANTILES:
        out[f"freeze_{q}_t"] = []
        out[f"freeze_{q}_b"] = []

    meta = {"images": 0, "annotations": 0, "target_pixels": 0, "background_pixels": 0}
    for image_id in sorted(image_ids):
        image_meta = images[image_id]
        image_path = dataset_root / "images" / split / image_meta["file_name"]
        if not image_path.exists():
            continue
        target, background = masks(image_meta["height"], image_meta["width"], anns.get(image_id, []))
        if target.sum() == 0 or background.sum() == 0:
            continue
        raw, lowrank, features = score_components(image_path)
        gate = model.decision_function(features.reshape(-1, features.shape[-1])).reshape(raw.shape)
        gate = zscore(gate)
        positive_gate = np.maximum(gate, 0.0)

        out["raw_t"].append(raw[target])
        out["raw_b"].append(raw[background])
        out["lowrank_t"].append(lowrank[target])
        out["lowrank_b"].append(lowrank[background])
        out["gate_t"].append(gate[target])
        out["gate_b"].append(gate[background])
        for q in FREEZE_QUANTILES:
            boost_mask = raw <= np.quantile(raw, q)
            boost = positive_gate * boost_mask
            out[f"freeze_{q}_t"].append(boost[target])
            out[f"freeze_{q}_b"].append(boost[background])

        meta["images"] += 1
        meta["annotations"] += len(anns.get(image_id, []))
        meta["target_pixels"] += int(target.sum())
        meta["background_pixels"] += int(background.sum())

    collected: dict[str, Any] = {}
    for key, values in out.items():
        collected[key] = np.concatenate(values) if values else np.asarray([], dtype=np.float32)
    collected["meta"] = meta
    return collected


def eval_curve(target_scores: np.ndarray, background_scores: np.ndarray) -> list[dict[str, float]]:
    order = np.sort(background_scores)
    n_background = len(order)
    rows: list[dict[str, float]] = []
    for pfa in PFAS:
        false_cap = int(np.floor(pfa * n_background))
        if false_cap <= 0:
            threshold = np.nextafter(order[-1], np.inf)
        else:
            threshold = order[max(0, n_background - false_cap)]
        rows.append(
            {
                "pfa": pfa,
                "pd": float(np.mean(target_scores > threshold)),
                "empirical_pfa": float(np.mean(background_scores > threshold)),
            }
        )
    return rows


def policy_scores(pack: dict[str, Any], policy: str) -> tuple[np.ndarray, np.ndarray]:
    if policy == "raw":
        return pack["raw_t"], pack["raw_b"]
    if policy == "gate":
        return pack["gate_t"], pack["gate_b"]
    if policy.startswith("raw_plus_gate_alpha_"):
        alpha = float(policy.rsplit("_", 1)[-1])
        return pack["raw_t"] + alpha * pack["gate_t"], pack["raw_b"] + alpha * pack["gate_b"]
    if policy.startswith("raw_plus_freeze_q_"):
        parts = policy.split("_")
        q = float(parts[4])
        alpha = float(parts[6])
        return pack["raw_t"] + alpha * pack[f"freeze_{q}_t"], pack["raw_b"] + alpha * pack[f"freeze_{q}_b"]
    raise ValueError(f"unknown policy: {policy}")


def candidate_policy_names() -> list[str]:
    names = ["raw", "gate"]
    names.extend(f"raw_plus_gate_alpha_{alpha}" for alpha in ALPHAS)
    for q in FREEZE_QUANTILES:
        names.extend(f"raw_plus_freeze_q_{q}_alpha_{alpha}" for alpha in ALPHAS)
    return names


def select_policies(validation_pack: dict[str, Any]) -> dict[float, str]:
    policies = candidate_policy_names()
    raw_curve = eval_curve(validation_pack["raw_t"], validation_pack["raw_b"])
    selected: dict[float, str] = {}
    policy_curves: dict[str, list[dict[str, float]]] = {}
    for policy in policies:
        t, b = policy_scores(validation_pack, policy)
        policy_curves[policy] = eval_curve(t, b)
    for idx, pfa in enumerate(PFAS):
        # SSDD is used as a cross-modality SAR source. At extreme low-Pfa
        # operating points, preserve the raw detector ordering rather than
        # allowing a learned gate to perturb a tiny background tail.
        if pfa <= STRICT_RAW_FALLBACK_MAX_PFA:
            selected[pfa] = "raw"
            continue
        raw_pd = raw_curve[idx]["pd"]
        eligible: list[tuple[float, int, str]] = []
        for policy in policies:
            pd_value = policy_curves[policy][idx]["pd"]
            no_val_regression = pd_value >= raw_pd
            eligible.append((pd_value, int(no_val_regression), policy))
        eligible.sort(key=lambda row: (row[1], row[0], row[2]), reverse=True)
        selected[pfa] = eligible[0][2]
    return selected


def evaluate_selected(test_pack: dict[str, Any], selected: dict[float, str]) -> tuple[list[EvalRow], dict[str, int | float | bool]]:
    raw_curve = eval_curve(test_pack["raw_t"], test_pack["raw_b"])
    lowrank_curve = eval_curve(test_pack["lowrank_t"], test_pack["lowrank_b"])
    rows: list[EvalRow] = []
    for idx, pfa in enumerate(PFAS):
        policy = selected[pfa]
        t, b = policy_scores(test_pack, policy)
        candidate_row = eval_curve(t, b)[idx]
        raw_pd = raw_curve[idx]["pd"]
        lowrank_pd = lowrank_curve[idx]["pd"]
        beats_raw = candidate_row["pd"] > raw_pd
        ties_raw = abs(candidate_row["pd"] - raw_pd) <= 1e-12
        rows.append(
            EvalRow(
                pfa=pfa,
                selected_policy=policy,
                candidate_pd=candidate_row["pd"],
                raw_pd=raw_pd,
                lowrank_pd=lowrank_pd,
                candidate_empirical_pfa=candidate_row["empirical_pfa"],
                beats_raw=beats_raw,
                ties_raw=ties_raw,
                beats_or_ties_raw=beats_raw or ties_raw,
                beats_lowrank=candidate_row["pd"] > lowrank_pd,
            )
        )
    stats = {
        "wins_raw": sum(row.beats_raw for row in rows),
        "ties_raw": sum(row.ties_raw for row in rows),
        "losses_raw": sum(not row.beats_or_ties_raw for row in rows),
        "wins_or_ties_raw": sum(row.beats_or_ties_raw for row in rows),
        "wins_lowrank": sum(row.beats_lowrank for row in rows),
        "comparisons": len(rows),
        "mean_delta_vs_raw": float(np.mean([row.candidate_pd - row.raw_pd for row in rows])),
    }
    return rows, stats


def write_outputs(
    root: Path,
    date_tag: str,
    payload: dict[str, Any],
    rows: list[EvalRow],
) -> tuple[Path, Path, Path]:
    result_dir = root / "results" / "ssdd_external"
    log_dir = root / "logs"
    result_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    json_path = result_dir / f"ssdd_external_trainable_gate_{date_tag}.json"
    csv_path = result_dir / f"ssdd_external_trainable_gate_{date_tag}.csv"
    md_path = log_dir / f"ssdd_external_trainable_gate_{date_tag}.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    pd.DataFrame([asdict(row) for row in rows]).to_csv(csv_path, index=False)

    stats = payload["test_stats"]
    meta = payload["test_meta"]
    lines = [
        "# SSDD External Trainable-Gate Validation",
        "",
        f"Date: {date_tag}",
        "",
        "## Setup",
        "",
        "- Source: Official SSDD SAR Ship Detection Dataset.",
        "- Split: official train images are split deterministically into development/validation; official test images are held out.",
        "- Candidate: TP-SSCS-style trainable pixel gate over raw SAR intensity and low-rank/local residual features.",
        f"- Policy selection: `Pfa <= {STRICT_RAW_FALLBACK_MAX_PFA:.0e}` uses raw fallback; validation split selects the conservative operating policy for higher Pfa points.",
        "- Test calibration: empirical Pfa threshold is calibrated only on official-test background pixels outside dilated ship boxes.",
        "",
        "## Verdict",
        "",
        f"- Passed: `{str(payload['passed']).lower()}`",
        f"- Official-test images: `{meta['images']}`",
        f"- Official-test annotations: `{meta['annotations']}`",
        f"- Test wins vs raw: `{stats['wins_raw']}/{stats['comparisons']}`",
        f"- Test ties vs raw: `{stats['ties_raw']}/{stats['comparisons']}`",
        f"- Test losses vs raw: `{stats['losses_raw']}/{stats['comparisons']}`",
        f"- Test wins vs low-rank: `{stats['wins_lowrank']}/{stats['comparisons']}`",
        f"- Mean Pd delta vs raw: `{stats['mean_delta_vs_raw']:.6f}`",
        "",
        "## Test Comparisons",
        "",
        "| Pfa | Policy | Candidate Pd | Raw Pd | Low-rank Pd | Candidate empirical Pfa | Beats/ties raw | Beats low-rank |",
        "|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row.pfa:.0e} | `{row.selected_policy}` | {row.candidate_pd:.4f} | "
            f"{row.raw_pd:.4f} | {row.lowrank_pd:.4f} | {row.candidate_empirical_pfa:.6g} | "
            f"`{str(row.beats_or_ties_raw).lower()}` | `{str(row.beats_lowrank).lower()}` |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This is a second independent radar dataset family, but it is SAR ship imagery rather than AISTAP range-Doppler simulation or IPIX sea-clutter time series.",
            "- The result validates external trainable-gate adaptation, not zero-shot transfer of the AISTAP-SIM saved state.",
            "- The protocol is acceptable as breadth evidence only when interpreted together with the IPIX held-out validation and the official AISTAP-SIM full-asset tests.",
        ]
    )
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, csv_path, md_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(Path.home() / "Desktop" / "绗笁鎵?"))
    parser.add_argument("--date", default=datetime.now().strftime("%Y%m%d"))
    parser.add_argument("--seed", type=int, default=20260715)
    parser.add_argument("--max-target-per-image", type=int, default=800)
    parser.add_argument("--max-background-per-image", type=int, default=2400)
    args = parser.parse_args()

    root = Path(args.root)
    dataset_root = (
        root
        / "data"
        / "downloads"
        / "ssdd"
        / "extracted"
        / "Official-SSDD-OPEN"
        / "BBox_RBox_PSeg_SSDD"
        / "coco_style"
    )
    train_images, train_anns = load_coco(dataset_root / "annotations" / "train.json")
    test_images, test_anns = load_coco(dataset_root / "annotations" / "test.json")
    dev_ids, val_ids = split_train_ids(list(train_images))

    x_dev, y_dev, dev_meta = sample_development(
        dataset_root,
        dev_ids,
        train_images,
        train_anns,
        args.seed,
        args.max_target_per_image,
        args.max_background_per_image,
    )
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, class_weight="balanced"))
    model.fit(x_dev, y_dev)
    train_auc = float(roc_auc_score(y_dev, model.decision_function(x_dev)))

    validation_pack = collect_split(dataset_root, "train", val_ids, train_images, train_anns, model)
    selected = select_policies(validation_pack)
    test_pack = collect_split(dataset_root, "test", set(test_images), test_images, test_anns, model)
    rows, stats = evaluate_selected(test_pack, selected)
    passed = (
        test_pack["meta"]["images"] >= 200
        and test_pack["meta"]["annotations"] >= 500
        and stats["losses_raw"] == 0
        and stats["wins_raw"] >= 3
        and stats["wins_lowrank"] == stats["comparisons"]
        and stats["mean_delta_vs_raw"] > 0
    )
    payload: dict[str, Any] = {
        "date": args.date,
        "source": "Official SSDD SAR Ship Detection Dataset",
        "dataset_root": str(dataset_root),
        "development_meta": dev_meta,
        "validation_meta": validation_pack["meta"],
        "test_meta": test_pack["meta"],
        "train_auc_on_sample": train_auc,
        "selected_policies": {str(k): v for k, v in selected.items()},
        "test_stats": stats,
        "test_rows": [asdict(row) for row in rows],
        "criteria": {
            "min_test_images": 200,
            "min_test_annotations": 500,
            "required_losses_vs_raw": 0,
            "required_wins_vs_raw": 3,
            "required_wins_vs_lowrank": len(PFAS),
            "requires_positive_mean_delta_vs_raw": True,
        },
        "passed": bool(passed),
        "boundary": (
            "External supervised trainable-gate adaptation on official SSDD train/test split; "
            "not zero-shot transfer of the AISTAP-SIM saved state."
        ),
    }
    json_path, csv_path, md_path = write_outputs(root, args.date, payload, rows)
    print(json_path)
    print(csv_path)
    print(md_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

