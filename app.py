# 🚀 TINO Cosmic Destiny Engine V14
# 五行 × 紫微敘事 × 今日偏財雷達 × 公平隨機模型

import streamlit as st
import random
import hashlib
from datetime import datetime, date
import math

# ==========================================
# 🎨 頁面設定（真正響應式）
# ==========================================

st.set_page_config(page_title="TINO Cosmic Engine", layout="centered")

st.markdown("""
<style>
.block-container {
    padding-top: 1rem;
    padding-bottom: 4rem;
    max-width: 900px;
}
@media only screen and (max-width: 900px) {
    .block-container { max-width: 700px; }
}
@media only screen and (max-width: 480px) {
    .block-container {
        max-width: 100% !important;
        padding-left: 0.5rem;
        padding-right: 0.5rem;
    }
}
</style>
""", unsafe_allow_html=True)

st.title("🌌 TINO Cosmic Destiny Engine")
st.caption("五行 × 紫微敘事 × 今日偏財雷達")

# ==========================================
# 🧬 五行判定
# ==========================================

def get_element(year):
    last = year % 10
    if last in [0,1]:
        return "金"
    elif last in [2,3]:
        return "水"
    elif last in [4,5]:
        return "木"
    elif last in [6,7]:
        return "火"
    else:
        return "土"

element_tail = {
    "金":[4,9],
    "木":[3,8],
    "水":[1,6],
    "火":[2,7],
    "土":[0,5]
}

# ==========================================
# 🌠 今日偏財雷達
# ==========================================

def wealth_radar_score(name, birth):
    today = datetime.now().strftime("%Y%m%d")
    raw = name + str(birth) + today
    h = int(hashlib.sha256(raw.encode()).hexdigest(), 16)
    score = (h % 100) + 1   # 1~100

    if score > 80:
        level = "🔥 偏財高波動區"
    elif score > 60:
        level = "⚡ 偏財活躍區"
    elif score > 40:
        level = "🌊 平穩機率區"
    else:
        level = "🪨 建議娛樂小額"

    return score, level

# ==========================================
# 🔮 紫微敘事層
# ==========================================

def generate_story(name, element, seed):
    random.seed(seed)

    stars = [
        "紫微入命，主星微動",
        "破軍震盪，偏財翻湧",
        "武曲守財，金流匯聚",
        "天府照耀，資源浮現",
        "貪狼流轉，機會啟動"
    ]

    quantum = [
        "量子場正在重組",
        "平行宇宙微幅偏移",
        "機率雲產生坍縮",
        "時間軸出現共振",
        "未來財富態正在疊加"
    ]

    return f"""
    🌠 宇宙報告

    玩家：{name}
    本命五行：{element}

    ✦ 星曜動態：
    {random.choice(stars)}

    ✦ 量子狀態：
    {random.choice(quantum)}

    ※ 本結果屬隨機宇宙演化的一部分
    """

# ==========================================
# 🎲 核心號碼生成（保持公平）
# ==========================================

def generate_numbers(name, birth):

    base_seed = int(hashlib.sha256(
        (name + str(birth)).encode()
    ).hexdigest(), 16) % (10**8)

    random.seed(base_seed + int(datetime.now().timestamp()))

    element = get_element(birth.year)
    tails = element_tail[element]

    numbers = set()

    # 50% 五行尾數
    while len(numbers) < 3:
        n = random.randint(1,49)
        if n % 10 in tails:
            numbers.add(n)

    # 50% 隨機
    while len(numbers) < 6:
        numbers.add(random.randint(1,49))

    numbers = sorted(list(numbers))
    special = random.choice([x for x in range(1,49) if x not in numbers])

    story = generate_story(name, element, base_seed)

    return numbers, special, story, element

# ==========================================
# 🧑 使用者輸入
# ==========================================

name = st.text_input("👤 姓名", value="鄭廷暘")
birth = st.date_input("📅 出生日期", value=date(1983,7,15))

if st.button("🚀 啟動宇宙演算"):

    nums, spec, story, element = generate_numbers(name, birth)
    score, level = wealth_radar_score(name, birth)

    st.success("量子坍縮完成")

    # 🎯 今日偏財雷達
    st.markdown("## 📡 今日偏財雷達")
    st.progress(score)
    st.markdown(f"**能量指數：{score}/100**")
    st.markdown(f"**狀態判定：{level}**")

    st.markdown("---")

    # 🎲 樂透組合
    st.markdown("## 🔮 大樂透建議組合")
    st.markdown(
        f"<h2 style='text-align:center;'>"
        f"{' '.join([f'{x:02d}' for x in nums])} "
        f"<span style='color:red'>[{spec:02d}]</span>"
        f"</h2>",
        unsafe_allow_html=True
    )

    with st.expander("🌌 宇宙敘事報告"):
        st.markdown(story)

    st.caption("⚠ 本系統為娛樂儀式引擎，號碼仍屬隨機機率。理性投注。")
