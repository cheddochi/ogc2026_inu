import argparse
import json
import math
import random
from pathlib import Path


BAYS = [
    {"width": 125, "height": 15},
    {"width": 71, "height": 18},
    {"width": 140, "height": 25},
]


PROFILES = {
    "tight": {
        "area_target": (0.90, 0.92),
        "big_prob": 0.35,
        "early_prob": 0.75,
        "early_release": (0, 10),
        "late_release": (10, 25),
        "layer_overhang": True,
    },
    "realistic": {
        "area_target": (0.75, 0.85),
        "big_prob": 0.25,
        "early_prob": 0.45,
        "early_release": (0, 15),
        "late_release": (15, 60),
        "layer_overhang": False,
    },
    "contest": {
        "area_target": (0.84, 0.89),
        "big_prob": 0.30,
        "early_prob": 0.60,
        "early_release": (0, 14),
        "late_release": (14, 45),
        "layer_overhang": False,
    },
}


def polygon_area(poly):
    area = 0.0
    for i, (x1, y1) in enumerate(poly):
        x2, y2 = poly[(i + 1) % len(poly)]
        area += x1 * y2 - x2 * y1
    return abs(area) * 0.5


def convex_hull(points):
    points = sorted(set(points))
    if len(points) <= 1:
        return points

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower = []
    for p in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)

    upper = []
    for p in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)

    return lower[:-1] + upper[:-1]


def translate_first_to_origin(poly):
    ox, oy = poly[0]
    return [[round(x - ox, 4), round(y - oy, 4)] for x, y in poly]


def make_base_polygon(rng, width, height):
    n = rng.randint(6, 8)
    points = []
    for t in range(n):
        angle = 2.0 * math.pi * t / n + rng.uniform(-0.2, 0.2) * (2.0 * math.pi / n)
        rx = width * 0.5 * rng.uniform(0.85, 1.15)
        ry = height * 0.5 * rng.uniform(0.85, 1.15)
        points.append((math.cos(angle) * rx + width * 0.5, math.sin(angle) * ry + height * 0.5))

    hull = convex_hull(points)
    if polygon_area(hull) < 1e-6:
        hull = [(0, 0), (width, 0), (width, height), (0, height)]
    return translate_first_to_origin(hull)


def transform_point(x, y, orient):
    reflected = orient >= 4
    rot = orient % 4
    if reflected:
        x = -x
    if rot == 0:
        return x, y
    if rot == 1:
        return -y, x
    if rot == 2:
        return -x, -y
    return y, -x


def transform_poly(poly, orient):
    ref_x, ref_y = transform_point(poly[0][0], poly[0][1], orient)
    return [[round(transform_point(x, y, orient)[0] - ref_x, 4),
             round(transform_point(x, y, orient)[1] - ref_y, 4)] for x, y in poly]


def scale_poly(poly, factor):
    return [[round(x * factor, 4), round(y * factor, 4)] for x, y in poly]


def make_layers(layer0, layers, rng, layer_overhang):
    if layers == 1:
        return [layer0]
    xs = [x for x, _ in layer0]
    width = max(xs) - min(xs)
    if layer_overhang:
        layer1 = [[round(x * 1.35 + width * 0.05, 4), round(y * 0.7, 4)] for x, y in layer0]
    else:
        x_scale = rng.uniform(0.75, 1.10)
        y_scale = rng.uniform(0.75, 1.05)
        x_shift = width * rng.uniform(-0.04, 0.08)
        layer1 = [[round(x * x_scale + x_shift, 4), round(y * y_scale, 4)] for x, y in layer0]
    return [layer0, layer1]


def make_shape(rng, width, height, layers, layer_overhang):
    base = make_base_polygon(rng, width, height)
    shape = []
    for orient in range(8):
        layer0 = transform_poly(base, orient)
        shape.append({"orientation": orient, "layers": make_layers(layer0, layers, rng, layer_overhang)})
    return shape


def make_prefs(rng, profile):
    r = rng.random()
    if profile == "realistic":
        if r < 0.30:
            hi = rng.randint(65, 85)
            rest = 100 - hi
            bay1 = rng.randint(5, min(25, rest))
            return [hi, bay1, rest - bay1]
        if r < 0.60:
            hi = rng.randint(65, 85)
            rest = 100 - hi
            bay1 = rng.randint(5, min(25, rest))
            return [rest - bay1, bay1, hi]
        a = rng.randint(25, 45)
        b = rng.randint(20, 40)
        return [a, b, 100 - a - b]

    if r < 0.40:
        hi = rng.randint(85, 95)
        rest = 100 - hi
        bay1 = rng.randint(0, min(5, rest))
        return [hi, bay1, rest - bay1]
    if r < 0.80:
        hi = rng.randint(85, 95)
        rest = 100 - hi
        bay1 = rng.randint(0, min(5, rest))
        return [rest - bay1, bay1, hi]
    a = rng.randint(20, 45)
    b = rng.randint(10, 30)
    return [a, b, 100 - a - b]


def make_release(rng, cfg):
    if rng.random() < cfg["early_prob"]:
        lo, hi = cfg["early_release"]
    else:
        lo, hi = cfg["late_release"]
    return rng.randint(lo, hi)


def make_slack(rng, profile):
    if profile == "tight":
        return 0 if rng.random() < 0.80 else 1

    if profile == "contest":
        r = rng.random()
        if r < 0.35:
            return 0
        if r < 0.70:
            return rng.randint(1, 2)
        if r < 0.92:
            return rng.randint(3, 5)
        return rng.randint(6, 8)

    r = rng.random()
    if r < 0.20:
        return 0
    if r < 0.50:
        return rng.randint(1, 2)
    if r < 0.85:
        return rng.randint(3, 5)
    return rng.randint(6, 10)


def block_area(block):
    return polygon_area(block["shape"][0]["layers"][0])


def rescale_block(block, factor):
    for orient in block["shape"]:
        orient["layers"] = [scale_poly(layer, factor) for layer in orient["layers"]]


def generate_problem(seed=42, blocks=100, profile="realistic"):
    if profile not in PROFILES:
        raise ValueError(f"unknown profile: {profile}")
    cfg = PROFILES[profile]
    rng = random.Random(seed)
    problem = {
        "name": f"{profile}_B3_b{blocks}_seed{seed}",
        "bays": BAYS,
        "blocks": [],
        "weights": {"w1": 26667, "w2": 10, "w3": 300},
    }

    for i in range(blocks):
        big = rng.random() < cfg["big_prob"]
        width = rng.uniform(10, 18) if big else rng.uniform(4, 13)
        height = rng.uniform(5, 10) if big else rng.uniform(3, 9)
        layers = 2 if rng.random() < 0.70 else 1

        release = make_release(rng, cfg)
        proc = rng.randint(5, 15)
        slack = make_slack(rng, profile)

        problem["blocks"].append({
            "release_time": release,
            "due_date": release + proc + slack,
            "processing_time": proc,
            "workload": rng.randint(10, 80),
            "bay_preferences": make_prefs(rng, profile),
            "shape": make_shape(rng, width, height, layers, cfg["layer_overhang"]),
        })

    bay_area = sum(b["width"] * b["height"] for b in BAYS)
    target_ratio = rng.uniform(*cfg["area_target"])
    current_area = sum(block_area(b) for b in problem["blocks"])
    scale = math.sqrt((bay_area * target_ratio) / current_area)
    for block in problem["blocks"]:
        rescale_block(block, scale)

    return problem


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--blocks", type=int, default=100)
    parser.add_argument("--profile", choices=sorted(PROFILES), default="realistic")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    problem = generate_problem(seed=args.seed, blocks=args.blocks, profile=args.profile)
    out = Path(args.out or f"alg_tester/example/{problem['name']}.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(problem, indent=2), encoding="utf-8")

    bay_area = sum(b["width"] * b["height"] for b in problem["bays"])
    total_area = sum(block_area(b) for b in problem["blocks"])
    early = sum(1 for b in problem["blocks"] if b["release_time"] <= 10)
    slacks = [b["due_date"] - b["release_time"] - b["processing_time"] for b in problem["blocks"]]
    tight = sum(1 for s in slacks if s == 0)
    print(f"wrote {out}")
    print(f"profile={args.profile} bays={len(problem['bays'])} blocks={len(problem['blocks'])}")
    print(f"area_ratio={total_area / bay_area:.3f} early_release={early} slack0={tight} avg_slack={sum(slacks)/len(slacks):.2f}")


if __name__ == "__main__":
    main()
