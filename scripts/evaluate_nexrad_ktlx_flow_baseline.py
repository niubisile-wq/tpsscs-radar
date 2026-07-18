from __future__ import annotations

import evaluate_nexrad_kvwx_flow_baseline as base


base.PREFIX = "2019/05/23/KTLX/"
base.RUN_NAME = "nexrad_ktlx"
base.KEYS = [
    "2019/05/23/KTLX/KTLX20190523_000408_V06",
    "2019/05/23/KTLX/KTLX20190523_000907_V06",
    "2019/05/23/KTLX/KTLX20190523_001354_V06",
    "2019/05/23/KTLX/KTLX20190523_001907_V06",
    "2019/05/23/KTLX/KTLX20190523_002352_V06",
]


if __name__ == "__main__":
    raise SystemExit(base.main())
