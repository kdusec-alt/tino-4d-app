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

# CSS 黑科技風格 (TINO V9.2)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; }
    
    /* 按鈕樣式：動態流光 */
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
    
    .status-bar {
        background-color: #111; border: 1px solid #333; color: #00ff00;
        padding: 8px; border-radius: 5px; font-family: monospace; font-size: 0.8em;
        text-align: center; margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. TINO 五行通用演化邏輯 (V9.2) ---

def get_element_luck(year):
    """
    根據出生年尾數判斷五行屬性與幸運數
    """
    last_digit = int(str(year)[-1])
    
    # 河圖洛書五行數理
    if last_digit in [0, 1]: return "金 (Metal)", [4, 9, 0, 5] # 金生水
    if last_digit in [2, 3]: return "水 (Water)", [1, 6, 4, 9] # 水生木 (Tino本命)
    if last_digit in [4, 5]: return "木 (Wood)",  [3, 8, 1, 6] # 木生火
    if last_digit in [6, 7]: return "火 (Fire)",  [2, 7, 3, 8] # 火生土
    if last_digit in [8, 9]: return "土 (Earth)", [5, 0, 2, 7] # 土生金
    return "未知", []

def calculate_daily_seed(name, birth_date):
    """
    產生「時空雜湊種子」：結合 姓名 + 生日 + 今天日期
    """
    today_str = datetime.now().strftime("%Y%m%d") # 獲取今天日期 (例如 20260217)
    raw_str = f"{name}_{birth_date}_{today_str}"
    # 轉成一個巨大的整數種子
    seed_val = int(hashlib.sha256(raw_str.encode('utf-8')).hexdigest(), 16)
    return seed_val, today_str

def run_simulation(name, birth_date, audit_list):
    # 1. 獲取五行屬性
    element_name, lucky_digits = get_element_luck(birth_date.year)
    
    # 2. 獲取今日時空種子
    daily_seed, date_str = calculate_daily_seed(name, birth_date)
    random.seed(daily_seed) # 關鍵：鎖定隨機數種子，確保同一天算結果一致
    
    # --- A. 權重池建立 ---
    weights = {i: 1.0 for i in range(1, 50)}
    
    # 五行加權 (所有人通用)
    for i in range(1, 50):
        # 尾數符合五行幸運數 (例如水命強化 1, 6)
        if i % 10 in lucky_digits[:2]: weights[i] *= 2.5
        # 五行相生數 (輔助)
        if i % 10 in lucky_digits[2:]: weights[i] *= 1.5
        
        # 姓名共振 (雜湊)
        name_hash = (daily_seed % 49) + 1
        if i == name_hash: weights[i] *= 3.0
        
        # 日期共振
        if i == birth_date.day: weights[i] *= 2.0
        
        # 懲罰 (審計)
        if i in audit_list: weights[i] *= 0.1

    pool = []
    for num, w in weights.items():
        pool.extend([num] * int(w * 10))
    
    # --- B. 生成大樂透/威力彩 ---
    # 大樂透
    unique_pool = list(set(pool))
    if len(unique_pool) < 6: unique_pool = list(range(1, 50))
    l_main = sorted(random.sample(unique_pool, 6))
    l_spec = random.choice([x for x in range(1, 50) if x not in l_main])
    
    # 威力彩
    s_pool = [x for x in pool if x <= 38]
    unique_s = list(set(s_pool))
    if len(unique_s) < 6: unique_s = list(range(1, 39))
    s_main = sorted(random.sample(unique_s, 6))
    s_spec = random.randint(1, 8)
    
    # --- C. 生成刮刮樂 (完全動態化) ---
    # 邏輯：從大雜湊值中提取數字，並結合五行
    
    # 1. 先拿本命五行數 (例如水命拿 1, 6)
    base_tails = lucky_digits[:2] 
    
    # 2. 從今日運勢中算出一個「流日財數」
    # 利用 daily_seed 的後幾位來算
    daily_lucky = (daily_seed % 10)
    
    # 3. 組合並洗牌
    final_tails = list(set(base_tails + [daily_lucky]))
    
    # 如果湊不滿 3 個，補其他數字
    while len(final_tails) < 3:
        extra = (daily_seed // 10) % 10
        if extra not in final_tails:
            final_tails.append(extra)
        daily_seed //= 10
        
    final_tails = final_tails[:3]
    random.shuffle(final_tails) # 根據今天的 Seed 洗牌
    
    return l_main, l_spec, s_main, s_spec, final_tails, element_name, date_str

# --- 3. App 介面佈局 ---

st.markdown("<h1>🎱 Tino Lucky Ball</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>QUANTUM RESONANCE | CORE V9.2</div>", unsafe_allow_html=True)

# [側邊欄]
with st.sidebar:
    st.header("🛡️ 系統校正 (Audit)")
    st.info("輸入偏差數值以修正路徑。")
    audit_txt = st.text_input("排除號碼 (逗號隔開)", "")
    audit_list = []
    if audit_txt:
        try:
            audit_list = [int(x.strip()) for x in audit_txt.split(",")]
            st.success(f"⚠️ 已排除: {audit_list}")
        except:
            pass

# [輸入區]
col1, col2 = st.columns(2)
with col1:
    u_name = st.text_input("👤 姓名 (Name)", value="鄭廷暘")
with col2:
    u_dob = st.date_input("📅 生日 (Birthday)", value=date(1983, 7, 15), min_value=date(1900, 1, 1))

st.write("") 

# [啟動按鈕]
if st.button("🚀 啟動今日量子演算 (DAILY SPIN)"):
    with st.spinner("正在連結時空雜湊場..."):
        time.sleep(0.5)
        
    l, ls, s, ss, t, elem, d_str = run_simulation(u_name, u_dob, audit_list)
    
    # 顯示高科技狀態條 (包含今日日期)
    st.markdown(f"""
    <div class="status-bar">
        USER: {u_name} | ELEMENT: {elem} | DATE HASH: {d_str}
    </div>
    """, unsafe_allow_html=True)

    # 結果卡片
    st.markdown(f"""
    <div class="result-box lotto">
        <span class="title-text" style="color:#00e5ff;">🔮 大樂透 (Lotto 649)</span>
        <div class="nums">
            {' '.join([f'{x:02d}' for x in l])} <span class="spec">[{ls:02d}]</span>
        </div>
    </div>
    
    <div class="result-box super">
        <span class="title-text" style="color:#00ff00;">💰 威力彩 (Super Lotto)</span>
        <div class="nums">
            {' '.join([f'{x:02d}' for x in s])} <span class="spec">[{ss:02d}]</span>
        </div>
    </div>
    
    <div class="result-box scratch">
        <span class="title-text" style="color:#ffd700;">🧧 刮刮樂 (Daily Tails)</span>
        <div class="nums">
            {t[0]} > {t[1]} > {t[2]}
        </div>
        <div style="font-size:0.9em; color:#aaa; margin-top:10px; border-top:
