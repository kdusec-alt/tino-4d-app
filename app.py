import streamlit as st
import random
import hashlib
from datetime import datetime, date
import time

# --- 1. 頁面與 Cyberpunk 風格設定 ---
st.set_page_config(
    page_title="Tino Lucky Ball", 
    page_icon="🎱", 
    layout="centered"
)

# CSS 黑科技風格
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; }
    
    /* 按鈕樣式 */
    .stButton>button { 
        width: 100%; border-radius: 12px; height: 3.5em; 
        background: linear-gradient(90deg, #00c6ff 0%, #0072ff 100%); 
        color: white; font-size: 1.1em; font-weight: bold; border: none; letter-spacing: 1px;
        box-shadow: 0 0 15px rgba(0, 114, 255, 0.4);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 25px rgba(0, 114, 255, 0.6);
    }

    /* 結果卡片 */
    .result-box { 
        background: #1f2937; padding: 20px; border-radius: 15px; 
        margin-bottom: 20px; border-left: 6px solid; text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    }
    .lotto { border-color: #00e5ff; } 
    .super { border-color: #00ff00; } 
    .scratch { border-color: #ffd700; } 
    
    .title-text { font-size: 1.2em; font-weight: bold; margin-bottom: 10px; display: block; text-transform: uppercase; letter-spacing: 1px;}
    .nums { font-size: 2em; font-weight: bold; font-family: 'Courier New', monospace; letter-spacing: 2px; text-shadow: 0 0 5px rgba(255,255,255,0.3); }
    .spec { color: #ff4b4b; margin-left: 10px; font-size: 1.1em; }
    
    h1 { text-align: center; color: #00e5ff; text-shadow: 0 0 15px rgba(0, 229, 255, 0.6); margin-bottom: 0px;}
    .subtitle { text-align: center; color: #888; font-size: 0.9em; margin-bottom: 30px; letter-spacing: 1.5px; }
    
    /* 狀態顯示區 (新增生肖星座) */
    .status-container {
        display: flex; justify-content: space-around; background: #111;
        border: 1px solid #333; border-radius: 8px; padding: 10px; margin-bottom: 20px;
    }
    .status-item { text-align: center; font-size: 0.9em; color: #aaa; }
    .status-val { display: block; font-size: 1.2em; font-weight: bold; color: #00e5ff; margin-top: 5px;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. TINO 五行與星宿邏輯 (V9.4) ---

def get_zodiac(year):
    """計算 12 生肖"""
    zodiacs = ["🐵 猴 (Monkey)", "🐔 雞 (Rooster)", "🐶 狗 (Dog)", "🐷 豬 (Pig)", 
               "🐭 鼠 (Rat)", "🐮 牛 (Ox)", "🐯 虎 (Tiger)", "🐰 兔 (Rabbit)", 
               "🐲 龍 (Dragon)", "🐍 蛇 (Snake)", "🐴 馬 (Horse)", "🐑 羊 (Goat)"]
    return zodiacs[year % 12]

def get_constellation(month, day):
    """計算 12 星座"""
    dates = (20, 19, 21, 20, 21, 22, 23, 23, 23, 24, 22, 22)
    constellations = ["♑ 魔羯 (Cap)", "♒ 水瓶 (Aq)", "♓ 雙魚 (Pis)", "♈ 牡羊 (Ari)", 
                      "♉ 金牛 (Tau)", "♊ 雙子 (Gem)", "♋ 巨蟹 (Can)", "♌ 獅子 (Leo)", 
                      "♍ 處女 (Vir)", "♎ 天秤 (Lib)", "♏ 天蠍 (Sco)", "♐ 射手 (Sag)"]
    if day < dates[month-1]:
        return constellations[month-1]
    else:
        return constellations[month]

def get_element_luck(year):
    """五行屬性"""
    last_digit = int(str(year)[-1])
    if last_digit in [0, 1]: return "金 (Metal)", [4, 9, 0, 5]
    if last_digit in [2, 3]: return "水 (Water)", [1, 6, 4, 9]
    if last_digit in [4, 5]: return "木 (Wood)",  [3, 8, 1, 6]
    if last_digit in [6, 7]: return "火 (Fire)",  [2, 7, 3, 8]
    if last_digit in [8, 9]: return "土 (Earth)", [5, 0, 2, 7]
    return "未知", []

def calculate_daily_seed(name, birth_date):
    """時空雜湊種子"""
    today_str = datetime.now().strftime("%Y%m%d")
    raw_str = f"{name}_{birth_date}_{today_str}"
    seed_val = int(hashlib.sha256(raw_str.encode('utf-8')).hexdigest(), 16)
    return seed_val, today_str

def run_simulation(name, birth_date, audit_list):
    # 1. 計算生物特徵
    element_name, lucky_digits = get_element_luck(birth_date.year)
    zodiac = get_zodiac(birth_date.year)
    constellation = get_constellation(birth_date.month, birth_date.day)
    
    # 2. 計算亂數種子
    daily_seed, date_str = calculate_daily_seed(name, birth_date)
    random.seed(daily_seed)
    
    # 建立權重池
    weights = {i: 1.0 for i in range(1, 50)}
    for i in range(1, 50):
        # 五行加權
        if i % 10 in lucky_digits[:2]: weights[i] *= 2.5
        if i % 10 in lucky_digits[2:]: weights[i] *= 1.5
        # 姓名雜湊加權
        name_hash = (daily_seed % 49) + 1
        if i == name_hash: weights[i] *= 3.0
        # 日期加權
        if i == birth_date.day: weights[i] *= 2.0
        # 審計懲罰
        if i in audit_list: weights[i] *= 0.1

    pool = []
    for num, w in weights.items():
        pool.extend([num] * int(w * 10))
    
    # 生成號碼
    unique_pool = list(set(pool))
    if len(unique_pool) < 6: unique_pool = list(range(1, 50))
    l_main = sorted(random.sample(unique_pool, 6))
    l_spec = random.choice([x for x in range(1, 50) if x not in l_main])
    
    s_pool = [x for x in pool if x <= 38]
    unique_s = list(set(s_pool))
    if len(unique_s) < 6: unique_s = list(range(1, 39))
    s_main = sorted(random.sample(unique_s, 6))
    s_spec = random.randint(1, 8)
    
    # 生成刮刮樂
    base_tails = lucky_digits[:2] 
    daily_lucky = (daily_seed % 10)
    final_tails = list(set(base_tails + [daily_lucky]))
    while len(final_tails) < 3:
        extra = (daily_seed // 10) % 10
        if extra not in final_tails: final_tails.append(extra)
        daily_seed //= 10
    final_tails = final_tails[:3]
    random.shuffle(final_tails)
    
    return l_main, l_spec, s_main, s_spec, final_tails, element_name, zodiac, constellation, date_str

# --- 3. App 介面佈局 ---

st.markdown("<h1>🎱 Tino Lucky Ball</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>QUANTUM RESONANCE | CORE V9.4</div>", unsafe_allow_html=True)

# [側邊欄]
with st.sidebar:
    st.header("🛡️ 系統校正")
    audit_txt = st.text_input("輸入排除號碼 (逗號隔開)", "")
    audit_list = []
    if audit_txt:
        try:
            audit_list = [int(x.strip()) for x in audit_txt.split(",")]
            st.success(f"⚠️ 已排除: {audit_list}")
        except: pass

# [輸入區]
col1, col2 = st.columns(2)
with col1:
    u_name = st.text_input("👤 姓名", value="鄭廷暘")
with col2:
    u_dob = st.date_input("📅 生日", value=date(1983, 7, 15), min_value=date(1900, 1, 1))

st.write("") 

# [啟動按鈕]
if st.button("🚀 啟動量子演算 (DAILY SPIN)"):
    with st.spinner("正在解析星宿座標..."):
        time.sleep(0.5)
        
    l, ls, s, ss, t, elem, zod, const, d_str = run_simulation(u_name, u_dob, audit_list)
    
    # 格式化數字字串
    l_str = ' '.join([f'{x:02d}' for x in l])
    ls_str = f'{ls:02d}'
    s_str = ' '.join([f'{x:02d}' for x in s])
    ss_str = f'{ss:02d}'
    
    # --- 全新設計：個人特徵儀表板 ---
    st.markdown(f"""
    <div class="status-container">
        <div class="status-item">五行屬性<span class="status-val" style="color:#ffd700;">{elem}</span></div>
        <div class="status-item">生肖<span class="status-val">{zod}</span></div>
        <div class="status-item">星座<span class="status-val">{const}</span></div>
    </div>
    """, unsafe_allow_html=True)

    # 結果卡片
    st.markdown(f"""
    <div class="result-box lotto">
        <span class="title-text" style="color:#00e5ff;">🔮 大樂透 (Lotto 649)</span>
        <div class="nums">
            {l_str} <span class="spec">[{ls_str}]</span>
        </div>
    </div>
    
    <div class="result-box super">
        <span class="title-text" style="color:#00ff00;">💰 威力彩 (Super Lotto)</span>
        <div class="nums">
            {s_str} <span class="spec">[{ss_str}]</span>
        </div>
    </div>
    
    <div class="result-box scratch">
        <span class="title-text" style="color:#ffd700;">🧧 刮刮樂 (Daily Tails)</span>
        <div class="nums">
            {t[0]} > {t[1]} > {t[2]}
        </div>
        <div style="font-size:0.9em; color:#aaa; margin-top:10px; border-top: 1px solid #444; padding-top:5px;">
            *演算因子：{u_name} + {zod.split(' ')[0]} + {const.split(' ')[0]}
        </div>
    </div>
    """, unsafe_allow_html=True)
