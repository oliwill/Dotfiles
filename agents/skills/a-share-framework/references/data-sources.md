# 数据环境与获取路径

## 检测决策树（先检测，再选路，绝不假设）

```bash
test -f run_analysis.py && echo REPO_OK        # trader-obsidian 仓库管道
longbridge --version 2>/dev/null               # longbridge CLI
python -c "import yfinance"                    # 全球行情 fallback
python -c "import akshare"                     # A股财报/资金 fallback
```

| 优先级 | 路径 | 适用 |
|---|---|---|
| 1 | `python run_analysis.py <CODE>` | cwd 在 insight 仓库时；产出全量 JSON（行情+财报+技术） |
| 1b | `python one_shot_analysis.py <CODE>` | 需要超时隔离时（默认 30s，超时按部分数据继续并注明） |
| 2 | longbridge CLI | 无 repo 时的实时行情/资金流/财报 |
| 3 | yfinance + akshare | 全球 + A股兜底 |
| 4 | web_search + 用户贴图 | 全部不可用；**必须标注"数据缺失"项** |

## 代码规范

- 仓库内统一：`AAPL.US` / `00700.HK` / `SH600519` / `SZ000001`；Yahoo 边界处 HK 转 4 位（`0700.HK`）。
- A股判断：6 开头=SH，0/3 开头=SZ，4/8 开头=BJ（本框架对 BJ 适用性弱，流动性差，降档处理）。

## 各层所需最小数据集

| 层 | 必需数据 | 来源 |
|---|---|---|
| 世界观 | CPI/基准利率（最近3期）、指数周K（含850日线）、10年国债收益率近4周 | web_search + akshare |
| 选股 | 最近年报审计意见、货币资金/应收/库存/营收/经营现金流/短债，连续3年 | 年报/akshare/longbridge |
| 择时 | 日线6个月+周线2年K线与成交量、当前价格 vs 颈线/均线/缺口 | repo 管道/yfinance |
| 操作 | 现价、ATR或近期波幅、沪深300 PE、下一次财报日期、节气日历 | 计算+web |

## 数据缺口处理规则

- 财报数据拿不到连续 3 年 → Step 3 红线标注"数据缺失"，结论降一级（PASS→观察）。
- K线拿不到周线 → 择时结论标注"仅日线级，置信度降档"。
- **编造数据=框架最大违规**，宁可整节写"数据缺失"。
