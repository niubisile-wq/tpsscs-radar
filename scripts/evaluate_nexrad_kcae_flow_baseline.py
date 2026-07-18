from __future__ import annotations

import evaluate_nexrad_kvwx_flow_baseline as base


base.PREFIX = "2019/06/26/KCAE/"
base.RUN_NAME = "nexrad_kcae"
base.KEYS = [
    "2019/06/26/KCAE/KCAE20190626_000715_V06",
    "2019/06/26/KCAE/KCAE20190626_001656_V06",
    "2019/06/26/KCAE/KCAE20190626_002637_V06",
    "2019/06/26/KCAE/KCAE20190626_003617_V06",
    "2019/06/26/KCAE/KCAE20190626_004558_V06",
]


if __name__ == "__main__":
    raise SystemExit(base.main())
