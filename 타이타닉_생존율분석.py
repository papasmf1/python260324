import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import numpy as np

# ─────────────────────────────────────────
# 1. 데이터 로드 (seaborn 내장 타이타닉 데이터셋)
# ─────────────────────────────────────────
df = sns.load_dataset('titanic')
print("=" * 50)
print("[원본 데이터 정보]")
print(f"행: {df.shape[0]}, 열: {df.shape[1]}")
print(df.info())
print("\n[결측치 현황]")
print(df.isnull().sum())

# ─────────────────────────────────────────
# 2. 데이터 클렌징
# ─────────────────────────────────────────

# (1) age: 결측값을 성별·객실등급 그룹 중앙값으로 채우기
df['age'] = df.groupby(['sex', 'pclass'])['age'].transform(
    lambda x: x.fillna(x.median())
)

# (2) embarked: 결측값을 최빈값으로 채우기
df['embarked'] = df['embarked'].fillna(df['embarked'].mode()[0])

# (3) deck: 결측값 비율이 높아 분석에서 제외
df.drop(columns=['deck'], inplace=True)

# (4) embark_town / alive / class / who / adult_male / alone
#     seaborn 데이터셋의 중복 파생 컬럼 제거
df.drop(columns=['embark_town', 'alive', 'class', 'who',
                 'adult_male', 'alone'], inplace=True)

# (5) 나머지 결측값 포함 행 제거
df.dropna(inplace=True)

# (6) 이상값 제거: age 0 이하, fare 음수
df = df[(df['age'] > 0) & (df['fare'] >= 0)]

# (7) 중복 행 제거
df.drop_duplicates(inplace=True)

print("\n[클렌징 후 데이터 정보]")
print(f"행: {df.shape[0]}, 열: {df.shape[1]}")
print(df.isnull().sum())

# ─────────────────────────────────────────
# 3. 남성 / 여성 생존율 계산
# ─────────────────────────────────────────
survival_by_sex = df.groupby('sex')['survived'].agg(
    전체인원='count',
    생존인원='sum'
)
survival_by_sex['생존율(%)'] = (
    survival_by_sex['생존인원'] / survival_by_sex['전체인원'] * 100
).round(2)

print("\n[성별 생존율]")
print(survival_by_sex)

# 객실등급별 성별 생존율
survival_by_sex_pclass = df.groupby(['sex', 'pclass'])['survived'].mean() * 100
survival_by_sex_pclass = survival_by_sex_pclass.reset_index()
survival_by_sex_pclass.columns = ['sex', 'pclass', '생존율(%)']
survival_by_sex_pclass['생존율(%)'] = survival_by_sex_pclass['생존율(%)'].round(2)

# ─────────────────────────────────────────
# 4. 한글 폰트 설정 (Windows 맑은 고딕)
# ─────────────────────────────────────────
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# ─────────────────────────────────────────
# 5. 시각화
# ─────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(16, 6))
fig.suptitle('타이타닉 생존율 분석 (성별)', fontsize=16, fontweight='bold', y=1.02)

colors_sex   = {'male': '#4A90D9', 'female': '#E87070'}
labels_ko    = {'male': '남성', 'female': '여성'}

# ── 차트 1: 성별 생존율 막대 그래프 ──
ax1 = axes[0]
sexes      = survival_by_sex.index.tolist()
rates      = survival_by_sex['생존율(%)'].values
bar_colors = [colors_sex[s] for s in sexes]
bars = ax1.bar(
    [labels_ko[s] for s in sexes], rates,
    color=bar_colors, edgecolor='white', linewidth=1.5, width=0.5
)
for bar, rate in zip(bars, rates):
    ax1.text(bar.get_x() + bar.get_width() / 2,
             bar.get_height() + 1,
             f'{rate:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=12)
ax1.set_title('성별 생존율', fontsize=13, fontweight='bold')
ax1.set_ylabel('생존율 (%)')
ax1.set_ylim(0, 105)
ax1.grid(axis='y', alpha=0.3)
ax1.spines[['top', 'right']].set_visible(False)

# ── 차트 2: 성별 생존/사망 인원 누적 막대 ──
ax2 = axes[1]
for i, sex in enumerate(sexes):
    total    = survival_by_sex.loc[sex, '전체인원']
    survived = survival_by_sex.loc[sex, '생존인원']
    dead     = total - survived
    label    = labels_ko[sex]
    ax2.bar(label, survived, color=colors_sex[sex], alpha=0.9,
            edgecolor='white', linewidth=1.5, label='생존' if i == 0 else '')
    ax2.bar(label, dead, bottom=survived, color=colors_sex[sex], alpha=0.35,
            edgecolor='white', linewidth=1.5, label='사망' if i == 0 else '')
    ax2.text(i, survived / 2, f'생존\n{survived}명',
             ha='center', va='center', fontweight='bold', fontsize=10, color='white')
    ax2.text(i, survived + dead / 2, f'사망\n{dead}명',
             ha='center', va='center', fontweight='bold', fontsize=10, color='white')
ax2.set_title('성별 생존/사망 인원', fontsize=13, fontweight='bold')
ax2.set_ylabel('인원 수')
ax2.grid(axis='y', alpha=0.3)
ax2.spines[['top', 'right']].set_visible(False)

# ── 차트 3: 객실등급별 성별 생존율 ──
ax3 = axes[2]
pclasses  = [1, 2, 3]
x         = np.arange(len(pclasses))
width     = 0.35

for j, sex in enumerate(sexes):
    data = survival_by_sex_pclass[survival_by_sex_pclass['sex'] == sex]
    vals = [data[data['pclass'] == p]['생존율(%)'].values[0]
            if len(data[data['pclass'] == p]) > 0 else 0
            for p in pclasses]
    offset = (j - 0.5) * width
    bars2 = ax3.bar(x + offset, vals, width,
                    label=labels_ko[sex], color=colors_sex[sex],
                    edgecolor='white', linewidth=1.5, alpha=0.9)
    for bar, v in zip(bars2, vals):
        ax3.text(bar.get_x() + bar.get_width() / 2,
                 bar.get_height() + 1,
                 f'{v:.0f}%', ha='center', va='bottom', fontsize=9)

ax3.set_title('객실등급별 성별 생존율', fontsize=13, fontweight='bold')
ax3.set_ylabel('생존율 (%)')
ax3.set_xticks(x)
ax3.set_xticklabels(['1등석', '2등석', '3등석'])
ax3.set_ylim(0, 115)
ax3.legend()
ax3.grid(axis='y', alpha=0.3)
ax3.spines[['top', 'right']].set_visible(False)

plt.tight_layout()
plt.savefig('타이타닉_생존율분석.png', dpi=150, bbox_inches='tight')
print("\n그래프를 '타이타닉_생존율분석.png' 로 저장했습니다.")
plt.show()
