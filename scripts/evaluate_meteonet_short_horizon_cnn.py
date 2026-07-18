from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn.functional as F
from sklearn.metrics import mean_absolute_error, mean_squared_error
from torch import nn
from torch.utils.data import DataLoader, Dataset


ROOT = Path(__file__).resolve().parents[1]
METEO_PATH = Path(r"C:\meteo1\reflectivity_new_SE_2018_12.2.npz")


def to_dbz(arr: np.ndarray) -> np.ndarray:
    return arr.astype(np.float32) / 10.0


def norm_dbz(arr: np.ndarray) -> np.ndarray:
    # Keep the range stable for the small CNN.
    return np.clip((arr + 20.0) / 80.0, 0.0, 1.0).astype(np.float32)


def denorm_dbz(arr: np.ndarray) -> np.ndarray:
    return arr * 80.0 - 20.0


@dataclass
class Window:
    start: int
    target: int


def build_windows(n_frames: int, context: int = 4) -> list[Window]:
    return [Window(start=i - context, target=i) for i in range(context, n_frames)]


class MeteoWindowDataset(Dataset):
    def __init__(self, frames: np.ndarray, windows: list[Window]):
        self.frames = frames
        self.windows = windows

    def __len__(self) -> int:
        return len(self.windows)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor]:
        win = self.windows[idx]
        x = self.frames[win.start:win.target]
        y = self.frames[win.target]
        x = torch.tensor(x, dtype=torch.float32)
        y = torch.tensor(y, dtype=torch.float32)
        x = F.interpolate(x.unsqueeze(0), size=(64, 64), mode="bilinear", align_corners=False).squeeze(0)
        y = F.interpolate(y.unsqueeze(0).unsqueeze(0), size=(64, 64), mode="bilinear", align_corners=False).squeeze(0).squeeze(0)
        return x, y


class SmallForecastCNN(nn.Module):
    def __init__(self, in_ch: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(in_ch, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(32, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(32, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(16, 1, kernel_size=1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x).squeeze(1)


def csi(pred: np.ndarray, target: np.ndarray, thr: float) -> float:
    pred_hit = pred >= thr
    target_hit = target >= thr
    tp = float(np.logical_and(pred_hit, target_hit).sum())
    fp = float(np.logical_and(pred_hit, ~target_hit).sum())
    fn = float(np.logical_and(~pred_hit, target_hit).sum())
    denom = tp + fp + fn
    return float(tp / denom) if denom else float("nan")


def eval_metrics(pred: np.ndarray, target: np.ndarray) -> dict[str, float]:
    diff = target.reshape(-1) - pred.reshape(-1)
    return {
        "mae_dbz": float(mean_absolute_error(target.reshape(-1), pred.reshape(-1))),
        "rmse_dbz": float(np.sqrt(np.mean(diff ** 2))),
        "csi_10": csi(pred, target, 10.0),
        "csi_20": csi(pred, target, 20.0),
        "csi_30": csi(pred, target, 30.0),
        "csi_40": csi(pred, target, 40.0),
        "csi_50": csi(pred, target, 50.0),
    }


def main() -> int:
    raw = np.load(METEO_PATH, allow_pickle=True)
    frames = norm_dbz(to_dbz(raw["data"]))
    dates = raw["dates"]

    windows = build_windows(len(frames), context=4)
    train_windows = windows[:14]
    val_windows = windows[14:18]
    test_windows = windows[18:]

    train_ds = MeteoWindowDataset(frames, train_windows)
    val_ds = MeteoWindowDataset(frames, val_windows)
    test_ds = MeteoWindowDataset(frames, test_windows)

    train_loader = DataLoader(train_ds, batch_size=len(train_ds), shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=len(val_ds), shuffle=False)
    test_loader = DataLoader(test_ds, batch_size=len(test_ds), shuffle=False)

    model = SmallForecastCNN(in_ch=4)
    opt = torch.optim.Adam(model.parameters(), lr=2e-3, weight_decay=1e-4)

    best_state = None
    best_val_mae = float("inf")
    for _ in range(80):
        model.train()
        for xb, yb in train_loader:
            opt.zero_grad()
            pred = model(xb)
            loss = F.smooth_l1_loss(pred, yb)
            loss.backward()
            opt.step()

        model.eval()
        with torch.no_grad():
            xb, yb = next(iter(val_loader))
            val_pred = model(xb)
            val_mae = float(F.l1_loss(val_pred, yb).item())
        if val_mae < best_val_mae:
            best_val_mae = val_mae
            best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}

    assert best_state is not None
    model.load_state_dict(best_state)
    model.eval()

    def predict(ds: Dataset) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        loader = DataLoader(ds, batch_size=len(ds), shuffle=False)
        xb, yb = next(iter(loader))
        with torch.no_grad():
            pred = model(xb).cpu().numpy()
        return pred, yb.cpu().numpy(), xb.cpu().numpy()

    train_pred, train_y, train_x = predict(train_ds)
    val_pred, val_y, val_x = predict(val_ds)
    test_pred, test_y, test_x = predict(test_ds)

    # Persistence baseline uses the latest observed frame in the context window.
    train_persist = train_x[:, -1]
    val_persist = val_x[:, -1]
    test_persist = test_x[:, -1]

    # Denormalize back to dBZ for reporting.
    train_pred_dbz = denorm_dbz(train_pred)
    val_pred_dbz = denorm_dbz(val_pred)
    test_pred_dbz = denorm_dbz(test_pred)
    train_y_dbz = denorm_dbz(train_y)
    val_y_dbz = denorm_dbz(val_y)
    test_y_dbz = denorm_dbz(test_y)
    train_persist_dbz = denorm_dbz(train_persist)
    val_persist_dbz = denorm_dbz(val_persist)
    test_persist_dbz = denorm_dbz(test_persist)

    rows = []
    for split, pred, target, persist in [
        ("train", train_pred_dbz, train_y_dbz, train_persist_dbz),
        ("val", val_pred_dbz, val_y_dbz, val_persist_dbz),
        ("test", test_pred_dbz, test_y_dbz, test_persist_dbz),
    ]:
        m = eval_metrics(pred, target)
        p = eval_metrics(persist, target)
        rows.append(
            {
                "split": split,
                "n": int(target.shape[0]),
                "mae_model": m["mae_dbz"],
                "mae_persistence": p["mae_dbz"],
                "rmse_model": m["rmse_dbz"],
                "rmse_persistence": p["rmse_dbz"],
                "csi20_model": m["csi_20"],
                "csi20_persistence": p["csi_20"],
            }
        )

    out_dir = ROOT / "results" / "meteonet_external"
    out_dir.mkdir(parents=True, exist_ok=True)
    log_dir = ROOT / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    fig_dir = ROOT / "figures" / "main"
    fig_dir.mkdir(parents=True, exist_ok=True)

    pd_path = out_dir / "meteonet_short_horizon_cnn_summary.csv"
    import pandas as pd

    pd.DataFrame(rows).to_csv(pd_path, index=False, encoding="utf-8-sig")
    (out_dir / "meteonet_short_horizon_cnn_summary.json").write_text(json.dumps(rows, indent=2), encoding="utf-8-sig")

    lines = [
        "# MeteoNet Short-Horizon CNN Validation",
        "",
        f"- file: {METEO_PATH}",
        f"- sample_count: {len(frames)}",
        f"- context: 4 frames",
        f"- split: train={len(train_ds)} val={len(val_ds)} test={len(test_ds)}",
        f"- best_val_mae(norm): {best_val_mae:.4f}",
        "",
    ]
    for r in rows:
        lines.append(
            f"- {r['split']}: mae_model={r['mae_model']:.4f} mae_persistence={r['mae_persistence']:.4f} "
            f"rmse_model={r['rmse_model']:.4f} rmse_persistence={r['rmse_persistence']:.4f} "
            f"csi20_model={r['csi20_model']:.4f} csi20_persistence={r['csi20_persistence']:.4f}"
        )
    (log_dir / "meteonet_short_horizon_cnn_validation_20260713.md").write_text("\n".join(lines), encoding="utf-8-sig")

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(test_y_dbz[0].ravel()[:1200], label="target", alpha=0.7)
    ax.plot(test_persist_dbz[0].ravel()[:1200], label="persistence", alpha=0.7)
    ax.plot(test_pred_dbz[0].ravel()[:1200], label="model", alpha=0.7)
    ax.set_title("MeteoNet short-horizon sample trace")
    ax.legend()
    fig.tight_layout()
    fig.savefig(fig_dir / "figure8_meteonet_short_horizon_cnn.svg", dpi=160)
    plt.close(fig)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
