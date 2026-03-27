from __future__ import annotations

import re
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager, rcParams


INPUT_FILE = Path("출생아수__합계출산율__자연증가_등_20260327151823.xlsx")
OUTPUT_CLEAN_CSV = Path("출생아_합계출산율_정제데이터.csv")
OUTPUT_REPORT = Path("출생아_합계출산율_분석리포트.txt")
OUTPUT_PLOT = Path("출생아수_년도별_라인그래프.png")


def configure_korean_output() -> None:
    # Force UTF-8 stdout/stderr in Windows terminal to avoid mojibake.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")


def configure_korean_font() -> None:
    # Pick the first installed Korean-capable font.
    preferred_fonts = ["Malgun Gothic", "AppleGothic", "NanumGothic", "Noto Sans CJK KR"]
    installed_names = {f.name for f in font_manager.fontManager.ttflist}
    selected = next((name for name in preferred_fonts if name in installed_names), None)

    if selected:
        rcParams["font.family"] = selected
    rcParams["axes.unicode_minus"] = False


def pick_indicator_columns(indicators: list[str], pivot: pd.DataFrame) -> tuple[str, str]:
    births_keywords = ["출생아수", "출생아"]
    tfr_keywords = ["합계출산율"]

    births_col = next(
        (
            c
            for c in indicators
            if any(k in c for k in births_keywords)
            and "률" not in c
            and "천명" not in c
        ),
        None,
    )
    tfr_col = next((c for c in indicators if any(k in c for k in tfr_keywords)), None)

    # Fallback when indicator names are not decoded as expected.
    if births_col is None:
        candidates = [c for c in indicators if pivot[c].dropna().max() > 100000]
        births_col = candidates[0] if candidates else indicators[0]

    if tfr_col is None:
        candidates = [
            c
            for c in indicators
            if pivot[c].dropna().between(0, 10, inclusive="both").mean() > 0.95
            and pivot[c].dropna().max() < 10
        ]
        tfr_col = candidates[0] if candidates else indicators[min(1, len(indicators) - 1)]

    return births_col, tfr_col


def analyze_births_and_tfr(df_long: pd.DataFrame) -> str:
    pivot = df_long.pivot_table(index="year", columns="indicator", values="value", aggfunc="mean").sort_index()
    indicators = pivot.columns.tolist()
    births_col, tfr_col = pick_indicator_columns(indicators, pivot)

    births = pivot[births_col].dropna()
    tfr = pivot[tfr_col].dropna()

    common = pivot[[births_col, tfr_col]].dropna()
    corr = common[births_col].corr(common[tfr_col])

    births_change = births.pct_change() * 100
    top_drop = births_change.nsmallest(5)

    decade_avg = births.groupby((births.index // 10) * 10).mean()

    years_births = births.index.to_numpy(dtype=float)
    years_tfr = tfr.index.to_numpy(dtype=float)
    slope_births = np.polyfit(years_births, births.values, 1)[0]
    slope_tfr = np.polyfit(years_tfr, tfr.values, 1)[0]

    start_year, end_year = int(births.index.min()), int(births.index.max())
    start_value, end_value = float(births.loc[start_year]), float(births.loc[end_year])
    years_span = max(end_year - start_year, 1)
    cagr = (end_value / start_value) ** (1 / years_span) - 1

    lines: list[str] = []
    lines.append("[데이터 개요]")
    lines.append(f"- 분석 대상 연도: {pivot.index.min()} ~ {pivot.index.max()}")
    lines.append(f"- 지표 수: {len(indicators)}")
    lines.append(f"- 출생아수 지표로 사용된 컬럼: {births_col}")
    lines.append(f"- 합계출산율 지표로 사용된 컬럼: {tfr_col}")
    lines.append("")

    lines.append("[핵심 추세]")
    lines.append(f"- 출생아수 시작/종료: {start_year}년 {start_value:,.0f}명 -> {end_year}년 {end_value:,.0f}명")
    lines.append(f"- 장기 연평균 변화율(CAGR): {cagr * 100:.2f}%")
    lines.append(f"- 출생아수 최대: {int(births.idxmax())}년 {births.max():,.0f}명")
    lines.append(f"- 출생아수 최소: {int(births.idxmin())}년 {births.min():,.0f}명")
    lines.append(f"- 합계출산율 최대: {int(tfr.idxmax())}년 {tfr.max():.3f}")
    lines.append(f"- 합계출산율 최소: {int(tfr.idxmin())}년 {tfr.min():.3f}")
    lines.append("")

    lines.append("[관계 및 변동성]")
    lines.append(f"- 출생아수와 합계출산율 상관계수: {corr:.4f}")
    lines.append(f"- 출생아수 선형추세 기울기(명/년): {slope_births:,.1f}")
    lines.append(f"- 합계출산율 선형추세 기울기(포인트/년): {slope_tfr:.4f}")
    lines.append("- 출생아수 전년 대비 감소율 상위 5개 연도:")
    for year, pct in top_drop.items():
        lines.append(f"  * {int(year)}년: {pct:.2f}%")
    lines.append("")

    lines.append("[10년 단위 평균 출생아수]")
    for decade, value in decade_avg.items():
        lines.append(f"- {int(decade)}s: {value:,.0f}명")

    return "\n".join(lines), births_col


def main() -> None:
    configure_korean_output()
    configure_korean_font()

    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    raw = pd.read_excel(INPUT_FILE, sheet_name=0)
    first_col = raw.columns[0]

    df = raw.rename(columns={first_col: "indicator"}).copy()

    year_cols = [c for c in df.columns if re.search(r"\d{4}", str(c))]
    long_df = df.melt(id_vars="indicator", value_vars=year_cols, var_name="year_raw", value_name="value")

    long_df["indicator"] = long_df["indicator"].astype(str).str.strip()
    long_df["year"] = long_df["year_raw"].astype(str).str.extract(r"(\d{4})").astype(float)
    long_df["value"] = pd.to_numeric(long_df["value"], errors="coerce")

    clean_df = (
        long_df.dropna(subset=["indicator", "year", "value"])
        .assign(year=lambda d: d["year"].astype(int))
        .drop_duplicates(subset=["indicator", "year"])
        .sort_values(["indicator", "year"])
        .reset_index(drop=True)
    )

    clean_df.to_csv(OUTPUT_CLEAN_CSV, index=False, encoding="utf-8-sig")

    report, births_col = analyze_births_and_tfr(clean_df)
    OUTPUT_REPORT.write_text(report, encoding="utf-8-sig")

    births_series = (
        clean_df[clean_df["indicator"] == births_col]
        .set_index("year")["value"]
        .sort_index()
    )

    plt.style.use("seaborn-v0_8-whitegrid")
    configure_korean_font()
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(births_series.index, births_series.values, marker="o", linewidth=2)
    ax.set_title("대한민국 연도별 출생아수")
    ax.set_xlabel("연도")
    ax.set_ylabel("출생아수(명)")
    ax.ticklabel_format(style="plain", axis="y")
    plt.tight_layout()
    fig.savefig(OUTPUT_PLOT, dpi=160)
    plt.close(fig)

    print("완료:")
    print(f"- 정제 데이터: {OUTPUT_CLEAN_CSV}")
    print(f"- 분석 리포트: {OUTPUT_REPORT}")
    print(f"- 라인그래프: {OUTPUT_PLOT}")


if __name__ == "__main__":
    main()