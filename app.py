import streamlit as st
import random
import hashlib
from datetime import datetime, date
import time
import plotly.graph_objects as go # 引入畫圖模組

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
    
    /* 狀態顯示區 */
    .status-container {
        display: flex; justify-content: space-around; background: #111;
        border: 1px solid #333; border-radius: 8px; padding: 10px; margin-bottom: 20px;
    }
    .status-item { text-align: center; font-size: 0.9em; color: #aaa; }
    .status-val { display: block; font-size: 1.2em; font-weight: bold; color: #00e5ff; margin-top: 5px;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. TINO 五行與星宿邏輯 ---

def get_zodiac(year):
    zodiacs = ["🐵 猴 (Monkey)", "🐔 雞 (Rooster)", "🐶 狗 (Dog)", "🐷 豬 (Pig)", 
               "🐭 鼠 (Rat)", "🐮 牛 (Ox)", "🐯 虎 (Tiger)", "🐰 兔 (Rabbit)", 
               "🐲 龍 (Dragon)", "🐍 蛇 (Snake)", "🐴 馬 (Horse)", "🐑 羊 (Goat)"]
    return zodiacs[year % 12]

def get_constellation(month, day):
    dates = (20, 19, 21, 20, 21, 22, 23, 23, 23, 24, 22, 22)
    constellations = ["♑ 魔羯 (Cap)", "♒ 水瓶 (Aq)", "♓ 雙魚 (Pis)", "♈ 牡羊 (Ari)", 
                      "♉ 金牛 (Tau)", "♊ 雙子 (Gem)", "♋ 巨蟹 (Can)", "♌ 獅子 (Leo)", 
                      "♍ 處女 (Vir)", "♎ 天秤 (Lib)", "♏ 天蠍 (Sco)", "♐ 射手 (Sag)"]
    if day < dates[month-1]:
        return constellations[month-1]
    else:
        return constellations[month]

def get_element_luck(year):
    last_digit = int(str(year)[-1])
    if last_digit in [0, 1]: return "金", [4, 9, 0, 5]
    if last_digit in [2, 3]: return "水", [1, 6, 4, 9]
    if last_digit in [4, 5]: return "木", [3, 8, 1, 6]
    if last_digit in [6, 7]: return "火", [2, 7, 3, 8]
    if last_digit in [8, 9]: return "土", [5, 0, 2, 7]
    return "未知", []

def calculate_daily_seed(name, birth_date):
    today_str = datetime.now().strftime("%Y%m%d")
    raw_str = f"{name}_{birth_date}_{today_str}"
    seed_val = int(hashlib.sha256(raw_str.encode('utf-8')).hexdigest(), 16)
    return seed_val, today_str

# 新增：計算五行能量分佈 (用於畫圖)
def calculate_element_distribution(main_element, seed):
    # 初始化五行能量 (金, 木, 水, 火, 土)
    elements = ['金', '木', '水', '火', '土']
    # 利用種子產生隨機基礎值 (40-80之間)
    random.seed(seed)
    values = [random.randint(40, 70) for _ in range(5)]
    
    # 強化本命屬性 (讓它突出)
    if main_element in elements:
        idx = elements.index(main_element)
        values[idx] = random.randint(90, 100) # 本命衝高
        
        # 強化相生屬性 (例如金生水，若主是水，金也要高)
        support_map = {'金': 4, '木': 2, '水': 0, '火': 1, '土': 3} # 誰生它
        support_idx = support_map[main_element]
        values[support_idx] += random.randint(10, 20)
        
    return elements, values

def run_simulation(name, birth_date, audit_list):
    element_name, lucky_digits = get_element_luck(birth_date.year)
    zodiac = get_zodiac(birth_date.year)
    constellation = get_constellation(birth_date.month, birth_date.day)
    
    daily_seed, date_str = calculate_daily_seed(name, birth_date)
    random.seed(daily_seed)
    
    # 計算圖表數據
    radar_labels, radar_values = calculate_element_distribution(element_name, daily_seed)
    
    weights = {i: 1.0 for i in range(1, 50)}
    for i in range(1, 50):
        if i % 10 in lucky_digits[:2]: weights[i] *= 2.5
        if i % 10 in lucky_digits[2:]: weights[i] *= 1.5
        name_hash = (daily_seed % 49) + 1
        if i == name_hash: weights[i] *= 3.0
        if i == birth_date.day: weights[i] *= 2.0
        if i in audit_list: weights[i] *= 0.1

    pool = []
    for num, w in weights.items():
        pool.extend([num] * int(w * 10))
    
    unique_pool = list(set(pool))
    if len(unique_pool) < 6: unique_pool = list(range(1, 50))
    l_main = sorted(random.sample(unique_pool, 6))
    l_spec = random.choice([x for x in range(1, 50) if x not in l_main])
    
    s_pool = [x for x in pool if x <= 38]
    unique_s = list(set(s_pool))
    if len(unique_s) < 6: unique_s = list(range(1, 39))
    s_main = sorted(random.sample(unique_s, 6))
    s_spec = random.randint(1, 8)
    
    base_tails = lucky_digits[:2] 
    daily_lucky = (daily_seed % 10)
    final_tails = list(set(base_tails + [daily_lucky]))
    while len(final_tails) < 3:
        extra = (daily_seed // 10) % 10
        if extra not in final_tails: final_tails.append(extra)
        daily_seed //= 10
    final_tails = final_tails[:3]
    random.shuffle(final_tails)
    
    return l_main, l_spec, s_main, s_spec, final_tails, element_name, zodiac, constellation, radar_labels, radar_values

# --- 3. App 介面佈局 ---

st.markdown("<h1>🎱 Tino Lucky Ball</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>QUANTUM RESONANCE | CORE V9.5</div>", unsafe_allow_html=True)

with st.sidebar:
    st.header("🛡️ 系統校正")
    audit_txt = st.text_input("輸入排除號碼 (逗號隔開)", "")
    audit_list = []
    if audit_txt:
        try:
            audit_list = [int(x.strip()) for x in audit_txt.split(",")]
            st.success(f"⚠️ 已排除: {audit_list}")
        except: pass

col1, col2 = st.columns(2)
with col1:
    u_name = st.text_input("👤 姓名", value="鄭廷暘")
with col2:
    u_dob = st.date_input("📅 生日", value=date(1983, 7, 15), min_value=date(1900, 1, 1))

st.write("") 

if st.button("🚀 啟動量子演算 (DAILY SPIN)"):
    with st.spinner("正在解析五行能量場..."):
        time.sleep(0.5)
        
    l, ls, s, ss, t, elem, zod, const, r_labels, r_values = run_simulation(u_name, u_dob, audit_list)
    
    l_str = ' '.join([f'{x:02d}' for x in l])
    ls_str = f'{ls:02d}'
    s_str = ' '.join([f'{x:02d}' for x in s])
    ss_str = f'{ss:02d}'
    
    # 儀表板
    st.markdown(f"""
    <div class="status-container">
        <div class="status-item">五行<span class="status-val" style="color:#ffd700;">{elem}</span></div>
        <div class="status-item">生肖<span class="status-val">{zod.split(' ')[0]}</span></div>
        <div class="status-item">星座<span class="status-val">{const.split(' ')[0]}</span></div>
    </div>
    """, unsafe_allow_html=True)

    # --- 新增：五行雷達圖 (Plotly High-Tech Style) ---
    # 為了讓圖表閉合，把第一個數據加到最後
    r_values.append(r_values[0])
    r_labels.append(r_labels[0])

    fig = go.Figure(data=go.Scatterpolar(
        r=r_values,
        theta=r_labels,
        fill='toself',
        line_color='#00e5ff',
        fillcolor='rgba(0, 229, 255, 0.3)',
        marker=dict(color='#fff', size=6)
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=False, range=[0, 100]),
            angularaxis=dict(
                tickfont=dict(size=14, color='#e0e0e0'),
                rotation=90,
                direction='clockwise'
            ),
            bgcolor='#1f2937'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        height=300,
        margin=dict(l=40, r=40, t=20, b=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    # ----------------------------------------------

    # 結果卡片
    st.markdown(f"""
    <div class="result-box lotto">
        <span class="title-text" style="color:#00e5ff;">🔮 大樂透</span>
        <div class="nums">{l_str} <span class="spec">[{ls_str}]</span></div>
    </div>
    
    <div class="result-box super">
        <span class="title-text" style="color:#00ff00;">💰 威力彩</span>
        <div class="nums">{s_str} <span class="spec">[{ss_str}]</span></div>
    </div>
    
    <div class="result-box scratch">
        <span class="title-text" style="color:#ffd700;">🧧 刮刮樂</span>
        <div class="nums">{t[0]} > {t[1]} > {t[2]}</div>
    </div>
    """, unsafe_allow_html=True)
