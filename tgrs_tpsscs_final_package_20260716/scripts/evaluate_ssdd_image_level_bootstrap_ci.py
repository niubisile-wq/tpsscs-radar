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
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

import evaluate_ssdd_external_trainable_gate as ssdd


@dataclass
class ThresholdRow:
    pfa: float
    selected_policy: str
    candidate_threshold: float
    raw_threshold: float
    lowrank_threshold: float


def threshold_for_pfa(background_scores: np.ndarray, pfa: float) -> float:
    order = np.sort(np.asarray(background_scores, dtype=np.float32))
    n_background = len(order)
    false_cap = int(np.floor(pfa * n_background))
    if false_cap <= 0:
        return float(np.nextafter(order[-1], np.inf))
    return float(order[max(0, n_background - false_cap)])


def one_annotation_mask(height: int, width: int, ann: dict[str, Any]) -> np.ndarray:
    target = np.zeros((height, width), dtype=np.uint8)
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
    return target.astype(bool)


def image_policy_score(raw: np.ndarray, gate: np.ndarray, policy: str) -> np.ndarray:
    if policy == "raw":
        return raw
    if policy == "gate":
        return gate
    if policy.startswith("raw_plus_gate_alpha_"):
        alpha = float(policy.rsplit("_", 1)[-1])
        return raw + alpha * gate
    if policy.startswith("raw_plus_freeze_q_"):
        parts = policy.split("_")
        q = float(parts[4])
        alpha = float(parts[6])
        positive_gate = np.maximum(gate, 0.0)
        boost_mask = raw <= np.quantile(raw, q)
        return raw + alpha * positive_gate * boost_mask
    raise ValueError(f"unknown policy: {policy}")


def bootstrap_ci(values: np.ndarray, rng: np.random.Generator, n_boot: int) -> dict[str, float]:
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if values.size == 0:
        return {"mean": float("nan"), "ci_low": float("nan"), "ci_high": float("nan")}
    if values.size == 1:
        value = float(values[0])
        return {"mean": value, "ci_low": value, "ci_high": value}
    idx = rng.integers(0, values.size, size=(n_boot, values.size))
    boot = values[idx].mean(axis=1)
    return {
        "mean": float(values.mean()),
        "ci_low": float(np.quantile(boot, 0.025)),
        "ci_high": float(np.quantile(boot, 0.975)),
    }


def build_model(
    dataset_root: Path,
    train_images: dict[int, dict[str, Any]],
    train_anns: dict[int, list[dict[str, Any]]],
    seed: int,
    max_target_per_image: int,
    max_background_per_image: int,
) -> tuple[Any, dict[str, Any], float]:
    dev_ids, val_ids = ssdd.split_train_ids(list(train_images))
    x_dev, y_dev, dev_meta = ssdd.sample_development(
        dataset_root,
        dev_ids,
        train_images,
        train_anns,
        seed,
        max_target_per_image,
        max_background_per_image,
    )
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, class_weight="balanced"))
    model.fit(x_dev, y_dev)
    train_auc = float(roc_auc_score(y_dev, model.decision_function(x_dev)))
    validation_pack = ssdd.collect_split(dataset_root, "train", val_ids, train_images, train_anns, model)
    selected = ssdd.select_policies(validation_pack)
    meta = {
        "development_meta": dev_meta,
        "validation_meta": validation_pack["meta"],
        "selected_policies": {str(k): v for k, v in selected.items()},
    }
    return model, meta, train_auc


def thresholds_from_pack(test_pack: dict[str, Any], selected: dict[float, str]) -> list[ThresholdRow]:
    rows: list[ThresholdRow] = []
    for pfa in ssdd.PFAS:
        candidate_t, candidate_b = ssdd.policy_scores(test_pack, selected[pfa])
        _ = candidate_t
        rows.append(
            ThresholdRow(
                pfa=pfa,
                selected_policy=selected[pfa],
                candidate_threshold=threshold_for_pfa(candidate_b, pfa),
                raw_threshold=threshold_for_pfa(test_pack["raw_b"], pfa),
                lowrank_threshold=threshold_for_pfa(test_pack["lowrank_b"], pfa),
            )
        )
    return rows


def evaluate_test_images(
    dataset_root: Path,
    test_images: dict[int, dict[str, Any]],
    test_anns: dict[int, list[dict[str, Any]]],
    model: Any,
    threshold_rows: list[ThresholdRow],
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, int]]:
    image_rows: list[dict[str, Any]] = []
    annotation_rows: list[dict[str, Any]] = []
    meta = {"images": 0, "annotations": 0, "target_pixels": 0, "background_pixels": 0}
    for image_id in sorted(test_images):
        image_meta = test_images[image_id]
        image_path = dataset_root / "images" / "test" / image_meta["file_name"]
        if not image_path.exists():
            continue
        anns = test_anns.get(image_id, [])
        target, background = ssdd.masks(image_meta["height"], image_meta["width"], anns)
        if target.sum() == 0 or background.sum() == 0:
            continue
        raw, lowrank, features = ssdd.score_components(image_path)
        gate = model.decision_function(features.reshape(-1, features.shape[-1])).reshape(raw.shape)
        gate = ssdd.zscore(gate)

        meta["images"] += 1
        meta["annotations"] += len(anns)
        meta["target_pixels"] += int(target.sum())
        meta["background_pixels"] += int(background.sum())

        for threshold_row in threshold_rows:
            candidate = image_policy_score(raw, gate, threshold_row.selected_policy)
            candidate_pd = float(np.mean(candidate[target] > threshold_row.candidate_threshold))
            raw_pd = float(np.mean(raw[target] > threshold_row.raw_threshold))
            lowrank_pd = float(np.mean(lowrank[target] > threshold_row.lowrank_threshold))
            candidate_pfa = float(np.mean(candidate[background] > threshold_row.candidate_threshold))
            raw_pfa = float(np.mean(raw[background] > threshold_row.raw_threshold))
            lowrank_pfa = float(np.mean(lowrank[background] > threshold_row.lowrank_threshold))
            image_rows.append(
                {
                    "image_id": int(image_id),
                    "file_name": image_meta["file_name"],
                    "pfa": threshold_row.pfa,
                    "selected_policy": threshold_row.selected_policy,
                    "annotations": len(anns),
                    "target_pixels": int(target.sum()),
                    "background_pixels": int(background.sum()),
                    "candidate_pd": candidate_pd,
                    "raw_pd": raw_pd,
                    "lowrank_pd": lowrank_pd,
                    "candidate_empirical_pfa": candidate_pfa,
                    "raw_empirical_pfa": raw_pfa,
                    "lowrank_empirical_pfa": lowrank_pfa,
                    "delta_vs_raw": candidate_pd - raw_pd,
                    "delta_vs_lowrank": candidate_pd - lowrank_pd,
                }
            )

            for ann in anns:
                ann_mask = one_annotation_mask(image_meta["height"], image_meta["width"], ann)
                if ann_mask.sum() == 0:
                    continue
                candidate_ann_pd = float(np.mean(candidate[ann_mask] > threshold_row.candidate_threshold))
                raw_ann_pd = float(np.mean(raw[ann_mask] > threshold_row.raw_threshold))
                lowrank_ann_pd = float(np.mean(lowrank[ann_mask] > threshold_row.lowrank_threshold))
                annotation_rows.append(
                    {
                        "annotation_id": int(ann.get("id", -1)),
                        "image_id": int(image_id),
                        "file_name": image_meta["file_name"],
                        "pfa": threshold_row.pfa,
                        "selected_policy": threshold_row.selected_policy,
                        "target_pixels": int(ann_mask.sum()),
                        "candidate_pd": candidate_ann_pd,
                        "raw_pd": raw_ann_pd,
                        "lowrank_pd": lowrank_ann_pd,
                        "delta_vs_raw": candidate_ann_pd - raw_ann_pd,
                        "delta_vs_lowrank": candidate_ann_pd - lowrank_ann_pd,
                    }
                )
    return pd.DataFrame(image_rows), pd.DataFrame(annotation_rows), meta


def summarize_ci(df: pd.DataFrame, level: str, rng: np.random.Generator, n_boot: int) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for pfa in ssdd.PFAS:
        sub = df[np.isclose(df["pfa"].astype(float), pfa)]
        if sub.empty:
            continue
        for comparator, col in [("raw", "delta_vs_raw"), ("lowrank", "delta_vs_lowrank")]:
            values = sub[col].astype(float).to_numpy()
            ci = bootstrap_ci(values, rng, n_boot)
            rows.append(
                {
                    "level": level,
                    "pfa": pfa,
                    "comparator": comparator,
                    "n_units": int(len(values)),
                    "mean_delta_pd": ci["mean"],
                    "ci95_low": ci["ci_low"],
                    "ci95_high": ci["ci_high"],
                    "positive_fraction": float(np.mean(values > 0)),
                    "nonnegative_fraction": float(np.mean(values >= 0)),
                    "negative_fraction": float(np.mean(values < 0)),
                }
            )
    return pd.DataFrame(rows)


def write_markdown(
    path: Path,
    date_tag: str,
    payload: dict[str, Any],
    ci_df: pd.DataFrame,
) -> None:
    lines = [
        "# SSDD Image-Level Bootstrap CI",
        "",
        f"Date: {date_tag}",
        "",
        "## Verdict",
        "",
        f"- Passed: `{str(payload['passed']).lower()}`",
        f"- Official-test images: `{payload['test_meta']['images']}`",
        f"- Official-test annotations: `{payload['test_meta']['annotations']}`",
        "- Unit-level robustness is now measured at both image and annotation levels.",
        "- This supplements the aggregate SSDD result; it does not change the boundary that SSDD is supervised external trainable-gate adaptation rather than zero-shot transfer.",
        "",
        "## CI Summary",
        "",
        "| Level | Pfa | Comparator | n | Mean Delta Pd | 95% CI | Positive fraction | Negative fraction |",
        "|---|---:|---|---:|---:|---:|---:|---:|",
    ]
    for _, row in ci_df.iterrows():
        lines.append(
            f"| `{row['level']}` | {row['pfa']:.0e} | `{row['comparator']}` | {int(row['n_units'])} | "
            f"{row['mean_delta_pd']:.4f} | [{row['ci95_low']:.4f}, {row['ci95_high']:.4f}] | "
            f"{row['positive_fraction']:.3f} | {row['negative_fraction']:.3f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- A positive image-level CI against raw at higher Pfa points supports broad SSDD gains rather than only aggregate pixel-pool gains.",
            "- Low-Pfa raw fallback points are expected to tie raw by design; they should be described as no-regression operating points.",
            "- Annotation-level rows measure target-region robustness across ship instances; they are supplementary because overlapping or polygon-level mask details can affect exact per-annotation counts.",
            "",
            "## Boundary",
            "",
            "- Thresholds are calibrated globally on official-test background pixels, matching the aggregate SSDD protocol.",
            "- Image-level and annotation-level statistics reuse those fixed thresholds and therefore test distribution of gains, not a separately tuned per-image detector.",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--date", default=datetime.now().strftime("%Y%m%d"))
    parser.add_argument("--seed", type=int, default=20260715)
    parser.add_argument("--boot", type=int, default=2000)
    parser.add_argument("--max-target-per-image", type=int, default=800)
    parser.add_argument("--max-background-per-image", type=int, default=2400)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    rng = np.random.default_rng(args.seed)
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
    train_images, train_anns = ssdd.load_coco(dataset_root / "annotations" / "train.json")
    test_images, test_anns = ssdd.load_coco(dataset_root / "annotations" / "test.json")

    model, train_meta, train_auc = build_model(
        dataset_root,
        train_images,
        train_anns,
        args.seed,
        args.max_target_per_image,
        args.max_background_per_image,
    )
    _, val_ids = ssdd.split_train_ids(list(train_images))
    validation_pack = ssdd.collect_split(dataset_root, "train", val_ids, train_images, train_anns, model)
    selected = ssdd.select_policies(validation_pack)
    test_pack = ssdd.collect_split(dataset_root, "test", set(test_images), test_images, test_anns, model)
    threshold_rows = thresholds_from_pack(test_pack, selected)
    image_df, ann_df, test_meta = evaluate_test_images(dataset_root, test_images, test_anns, model, threshold_rows)
    image_ci = summarize_ci(image_df, "image", rng, args.boot)
    annotation_ci = summarize_ci(ann_df, "annotation", rng, args.boot)
    ci_df = pd.concat([image_ci, annotation_ci], ignore_index=True)

    image_raw_high = image_ci[(image_ci["comparator"] == "raw") & (image_ci["pfa"] > ssdd.STRICT_RAW_FALLBACK_MAX_PFA)]
    lowrank_all = image_ci[image_ci["comparator"] == "lowrank"]
    passed = (
        test_meta["images"] >= 200
        and test_meta["annotations"] >= 500
        and bool((image_raw_high["ci95_low"] > 0).all())
        and bool((lowrank_all["ci95_low"] > 0).all())
    )

    result_dir = root / "results" / "ssdd_external"
    log_dir = root / "logs"
    result_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    image_csv = result_dir / f"ssdd_image_level_robustness_{args.date}.csv"
    ann_csv = result_dir / f"ssdd_annotation_level_robustness_{args.date}.csv"
    ci_csv = result_dir / f"ssdd_image_annotation_bootstrap_ci_{args.date}.csv"
    threshold_csv = result_dir / f"ssdd_global_thresholds_{args.date}.csv"
    json_path = result_dir / f"ssdd_image_level_bootstrap_ci_{args.date}.json"
    md_path = log_dir / f"ssdd_image_level_bootstrap_ci_{args.date}.md"

    image_df.to_csv(image_csv, index=False)
    ann_df.to_csv(ann_csv, index=False)
    ci_df.to_csv(ci_csv, index=False)
    pd.DataFrame([asdict(row) for row in threshold_rows]).to_csv(threshold_csv, index=False)

    payload = {
        "date": args.date,
        "source": "Official SSDD SAR Ship Detection Dataset",
        "train_auc_on_sample": train_auc,
        "training": train_meta,
        "test_meta": test_meta,
        "bootstrap_replicates": args.boot,
        "seed": args.seed,
        "passed": bool(passed),
        "criteria": {
            "min_images": 200,
            "min_annotations": 500,
            "requires_image_level_raw_ci_positive_for_non_fallback_pfas": True,
            "requires_image_level_lowrank_ci_positive_for_all_pfas": True,
        },
        "artifacts": {
            "image_csv": str(image_csv),
            "annotation_csv": str(ann_csv),
            "ci_csv": str(ci_csv),
            "threshold_csv": str(threshold_csv),
            "markdown_log": str(md_path),
        },
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(md_path, args.date, payload, ci_df)

    print(json_path)
    print(image_csv)
    print(ann_csv)
    print(ci_csv)
    print(md_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
