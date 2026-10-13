"""Digitize Jeong-Elnashai MAE 04-03 Fig. 2.8 from a raster image.

The source image must be a crop/scan of Fig. 2.8. The script extracts the
colored pushover curves and maps pixels to engineering coordinates using the
visible plot frame:

- x = -200 mm at the left frame, x = +200 mm at the right frame
- y = 0 kN at the bottom frame, y = 500 kN at the top frame

This is a reference-digitization aid, not a substitute for the published load
patterns xp100, xn100, yp100 and yn100.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

from PIL import Image


PLOT_LEFT = 306
PLOT_RIGHT = 926
PLOT_TOP = 50
PLOT_BOTTOM = 474
SCAN_TOP = 82


def px_to_data(x_px: float, y_px: float) -> tuple[float, float]:
    x_mm = -200.0 + (x_px - PLOT_LEFT) * 400.0 / (PLOT_RIGHT - PLOT_LEFT)
    y_kn = (PLOT_BOTTOM - y_px) * 500.0 / (PLOT_BOTTOM - PLOT_TOP)
    return x_mm, y_kn


def classify(r: int, g: int, b: int) -> str | None:
    if b > 145 and r < 90 and g < 120:
        return "blue"
    if r > 145 and g < 100 and b < 100:
        return "red"
    return None


def extract_points(image_path: Path) -> dict[str, list[tuple[float, float]]]:
    image = Image.open(image_path).convert("RGB")
    points = {
        "xn100": [],
        "yn100": [],
        "xp100": [],
        "yp100": [],
    }

    # Restrict extraction to the plotting frame and separate solid/dashed curves
    # by their displacement domains and approximate vertical bands.
    for x_px in range(PLOT_LEFT, PLOT_RIGHT + 1):
        red_ys: list[int] = []
        blue_ys: list[int] = []
        for y_px in range(SCAN_TOP, PLOT_BOTTOM + 1):
            curve = classify(*image.getpixel((x_px, y_px)))
            if curve == "blue":
                blue_ys.append(y_px)
            elif curve == "red":
                red_ys.append(y_px)

        if blue_ys:
            x_mm, _ = px_to_data(x_px, sum(blue_ys) / len(blue_ys))
            if x_mm < -1:
                ys_sorted = sorted(blue_ys)
                groups = _split_vertical_groups(ys_sorted)
                if len(groups) > 1:
                    upper = min(groups, key=lambda g: sum(g) / len(g))
                    lower = max(groups, key=lambda g: sum(g) / len(g))
                    points["yn100"].append(px_to_data(x_px, sum(upper) / len(upper)))
                    points["xn100"].append(px_to_data(x_px, sum(lower) / len(lower)))
                else:
                    y_mean = sum(groups[0]) / len(groups[0])
                    x_val, y_val = px_to_data(x_px, y_mean)
                    if y_val > 390:
                        points["yn100"].append((x_val, y_val))
                    else:
                        points["xn100"].append((x_val, y_val))

        if red_ys:
            x_mm, _ = px_to_data(x_px, sum(red_ys) / len(red_ys))
            if x_mm > 1:
                ys_sorted = sorted(red_ys)
                groups = _split_vertical_groups(ys_sorted)
                if len(groups) > 1:
                    upper = min(groups, key=lambda g: sum(g) / len(g))
                    lower = max(groups, key=lambda g: sum(g) / len(g))
                    points["yp100"].append(px_to_data(x_px, sum(upper) / len(upper)))
                    points["xp100"].append(px_to_data(x_px, sum(lower) / len(lower)))
                else:
                    y_mean = sum(groups[0]) / len(groups[0])
                    x_val, y_val = px_to_data(x_px, y_mean)
                    if y_val > 365 and x_val > 45:
                        points["yp100"].append((x_val, y_val))
                    else:
                        points["xp100"].append((x_val, y_val))
    return points


def _split_vertical_groups(ys: list[int]) -> list[list[int]]:
    groups: list[list[int]] = []
    current: list[int] = []
    for y in ys:
        if current and y - current[-1] > 4:
            groups.append(current)
            current = []
        current.append(y)
    if current:
        groups.append(current)
    return groups


def write_csv(points: dict[str, list[tuple[float, float]]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["curve", "top_displacement_mm", "base_shear_kN"])
        for curve in ("xn100", "yn100", "xp100", "yp100"):
            for x_mm, y_kn in points[curve]:
                writer.writerow([curve, f"{x_mm:.3f}", f"{y_kn:.3f}"])


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: digitize_jeong_elnashai_fig_2_8.py image.png output.csv", file=sys.stderr)
        return 2
    points = extract_points(Path(sys.argv[1]))
    write_csv(points, Path(sys.argv[2]))
    for name, rows in points.items():
        if rows:
            peak = max(rows, key=lambda item: item[1])
            print(f"{name}: {len(rows)} pts, peak {peak[1]:.1f} kN at {peak[0]:.1f} mm")
        else:
            print(f"{name}: 0 pts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
