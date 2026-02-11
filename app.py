import streamlit as st
import random
import hashlib
from datetime import datetime, date

# --- 1. 頁面與 Cyberpunk 風格設定 ---
st.set_page_config(page_title="TINO 4D 決策終端", page_icon="🧬", layout="centered")

# CSS 黑科技風格 (TINO V9.0)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    .stButton>button { 
        width: 100%; border-radius: 8px; height: 3.5em; 
        background: linear-gradient(90deg, #ff4b4b 0%, #ff9068 100%); 
        color: white; font-weight: bold; border: none; letter-spacing: 1px;
    }
    .result-box { 
        background: #1f2937; padding: 20px; border-radius: 10px; 
        margin-bottom: 15px; border-left: 5px solid; text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .lotto { border-color: #00e5ff; }
    .super { border-color: #00ff00; }
    .scratch { border-color: #ffd700; }
    .title-text { font-size: 1.1em; font-weight: bold; margin-bottom: 10px; display: block;}
    .nums { font-size: 1.8em; font-weight: bold; font-family: 'Courier New', monospace; letter-spacing: 2px; }
    .spec { color: #ff4b4b; margin-left: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. TINO 演化核心邏輯 ---
def calculate_personal_weight(name, birth_date, audit_list):
    weights = {i: 1.0 for i in range(1, 50)}
    
    # [時間] 生日權重 (判斷 1983 癸亥水命)
    year_char = str(birth_date.year)[-1]
    is_water_year = year_char in ['2', '3'] # 壬、癸屬水
    
    # [空間] 姓名 Hash 共振
    name_hash = int(hashlib.sha256(name.encode('utf-8')).hexdigest(), 16) % 49 + 1
    
    # [權重注入]
    for i in range(1, 49 + 1):
        # A. 水命強化 1, 6
        if is_water_year:
            if i % 10 in [1, 6]: weights[i] *= 2.5
            if i % 10 in [0, 9]: weights[i] *= 1.5
        
        # B. 姓名本命
        if i == name_hash: weights[i] *= 3.0
        
        # C. 反向審計 (懲罰上次失敗號碼)
        if i in audit_list: weights[i] *= 0.1 # 大幅降權

    return weights, is_water_year

def run_simulation(name, birth_date, audit_list):
    weights, is_water = calculate_personal_weight(name, birth_date, audit_list)
    
    # 建立加權池
    pool = []
    for num, w in weights.items():
        pool.extend([num] * int(w * 10))
    
    # 1. 大樂透 (1-49)
    unique_pool = list(set(pool))
    if len(unique_pool) < 6: unique_pool = list(range(1, 50))
    l_main = sorted(random.sample(unique_pool, 6))
    l_spec = random.choice([x for x in range(1, 50) if x not in l_main])
    
    # 2. 威力彩 (1-38)
    s_pool = [x for x in pool if x <= 38]
    unique_s = list(set(s_pool))
    if len(unique_s) < 6: unique_s = list(range(1, 39))
    s_main = sorted(random.sample(unique_s, 6))
    s_spec = random.randint(1, 8)
    
    # 3. 刮刮樂 (水命鎖定 1, 6, 0)
    if is_water:
        tails = [1, 6, 0]
    else:
        tails = [2, 7, 5]
    random.shuffle(tails) # 動態擾動
    
    return l_main, l_spec, s_main, s_spec, tails, is_water

# --- 3. App 介面佈局 ---
st.title("🧬 TINO 4D 決策終端")
st.caption("Survival > Prediction | Time Reverse Audit")

# [側邊欄] 反向審計
with st.sidebar:
    st.header("🛡️ 時間反向審計")
    st.info("輸入上次『誤判』的號碼進行懲罰，修正未來路徑。")
    audit_txt = st.text_input("輸入號碼 (逗號隔開)", "")
    audit_list = []
    if audit_txt:
        try:
            audit_list = [int(x.strip()) for x in audit_txt.split(",")]
            st.success(f"已鎖定噪音: {audit_list}")
        except:
            pass

# [輸入區]
col1, col2 = st.columns(2)
with col1:
    u_name = st.text_input("👤 姓名", value="鄭廷暘")
with col2:
    u_dob = st.date_input("📅 生日", value=date(1983, 7, 15), min_value=date(1900, 1, 1))

st.write("---")

# [執行按鈕]
if st.button("🚀 啟動量子演算 (INITIATE)"):
    with st.spinner("正在進行維度折疊..."):
        l, ls, s, ss, t, is_water = run_simulation(u_name, u_dob, audit_list)
        
        # 顯示屬性
        elem = "水 (Water)" if is_water else "非水系"
        st.success(f"✅ 屬性偵測：{elem} | 已啟動本命防護罩")

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
            <span class="title-text" style="color:#ffd700;">🧧 刮刮樂 (Survival Tails)</span>
            <div class="nums">
                {t[0]} > {t[1]} > {t[2]}
            </div>
            <div style="font-size:0.8em; color:#aaa; margin-top:5px;">*依據本命水氣 (1, 6) 動態演算</div>
        </div>
        """, unsafe_allow_html=True)
