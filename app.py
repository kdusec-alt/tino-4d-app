import streamlit as st
import random
import hashlib
from datetime import datetime
import math

st.set_page_config(page_title="TINO Quantum Fortune Engine", layout="centered")

# ==============================
# 五行
# ==============================

element_map = {
    "金": [4,9],
    "木": [3,8],
    "水": [1,6],
    "火": [2,7],
    "土": [0,5]
}

def get_element(year):
    last = year % 10
    if last in [0,1]: return "金"
    if last in [2,3]: return "水"
    if last in [4,5]: return "木"
    if last in [6,7]: return "火"
    return "土"

# ==============================
# 偏財雷達
# ==============================

def lucky_radar(seed):
    random.seed(seed + int(datetime.now().strftime("%Y%m%d")))
    score = random.randint(40,95)
    return score

# ==============================
# 核心產生器
# ==============================

def generate_all(name, birth):

    seed = int(hashlib.sha256(
        (name + str(birth)).encode()
    ).hexdigest(),16) % (10**8)

    random.seed(seed + int(datetime.now().timestamp()))

    element = get_element(birth.year)
    tails = element_map[element]

    # -------- 大樂透 49 --------
    lotto = set()
    while len(lotto) < 6:
        n = random.randint(1,49)
        if random.random() < 0.5:
            if n % 10 in tails:
                lotto.add(n)
        else:
            lotto.add(n)
    lotto = sorted(list(lotto))
    lotto_spec = random.randint(1,49)

    # -------- 威力彩 --------
    power_main = sorted(random.sample(range(1,39),6))
    power_spec = random.randint(1,8)

    # -------- 刮刮樂 --------
    scratch_level = random.choice(["低波動","中波動","高波動"])
    scratch_lucky = random.sample(range(1,100),3)

    # -------- 偏財雷達 --------
    radar = lucky_radar(seed)

    # -------- 紫微敘事 --------
    story = f"""
    本命五行：{element}

    今日量子震幅：{radar}%

    星曜微動，財氣波動屬於隨機坍縮態。
    """

    return {
        "lotto": lotto,
        "lotto_spec": lotto_spec,
        "power_main": power_main,
        "power_spec": power_spec,
        "scratch_level": scratch_level,
        "scratch_lucky": scratch_lucky,
        "radar": radar,
        "story": story
    }

# ==============================
# UI
# ==============================

st.title("🌌 TINO Quantum Fortune Engine")

name = st.text_input("姓名")
birth = st.date_input("生日")

if st.button("SPIN"):

    res = generate_all(name, birth)

    st.success("量子坍縮完成")

    # 大樂透
    st.subheader("🎯 大樂透")
    st.write(res["lotto"], " 特別號:", res["lotto_spec"])

    # 威力彩
    st.subheader("⚡ 威力彩")
    st.write(res["power_main"], " 第二區:", res["power_spec"])

    # 刮刮樂
    st.subheader("🎟 刮刮樂")
    st.write("波動等級:", res["scratch_level"])
    st.write("幸運號:", res["scratch_lucky"])

    # 偏財雷達
    st.subheader("📡 今日偏財雷達")
    st.progress(res["radar"]/100)
    st.write(f"財運指數: {res['radar']}%")

    # 紫微敘事
    with st.expander("🔮 宇宙敘事"):
        st.write(res["story"])
