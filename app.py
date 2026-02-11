import streamlit as st
import random
import hashlib
from datetime import datetime, date
import time
import plotly.graph_objects as go

# --- 1. 頁面與賭城風格設定 ---
st.set_page_config(
    page_title="Tino Lucky Slot", 
    page_icon="🎰", 
    layout="centered"
)

# CSS 賭城黑金風格
st.markdown("""
    <style>
    .stApp { background-color: #121212; color: #f0f0f0; font-family: 'Arial', sans-serif; }
    
    /* 拉霸機大按鈕 */
    .stButton>button { 
        width: 100%; border-radius: 50px; height: 4em; 
        background: linear-gradient(180deg, #ff0000 0%, #990000 100%); 
        color: white; font-size: 1.3em; font-weight: bold; border: 4px solid #ffcc00; 
        box-shadow: 0 5px 0 #660000, 0 10px 10px rgba(0,0,0,0.5);
        text-transform: uppercase; letter-spacing: 2px;
        transition: all 0.1s;
    }
    .stButton>button:active {
        transform: translateY(4px);
        box-shadow: 0 1px 0 #660000, 0 2px 5px rgba(0,0,0,0.5);
    }
    .stButton>button:hover {
        background: linear-gradient(180deg, #ff3333 0%, #cc0000 100%);
        border-color: #ffff00;
    }

    /* 數字球樣式 (Ball Style) */
    .ball-container {
        display: flex; justify-content: center; gap: 10px; flex-wrap: wrap; margin: 15px 0;
    }
    .ball {
        width: 50px; height: 50px; border-radius: 50%;
        background: radial-gradient(circle at 30% 30%, #ffffff, #e0e0e0, #a0a0a0);
        color: #333; font-weight: bold; font-size: 22px;
        display: flex; align-items: center; justify-content: center;
        box-shadow: inset -5px -5px 10px rgba(0,0,0,0.3), 3px 3px 5px rgba(0,0,0,0.5);
        border: 2px solid #fff;
        font-family: 'Courier New', monospace;
    }
    .ball.special {
        background: radial-gradient(circle at 30% 30%, #ff4b4b, #cc0000);
        color: white; border: 2px solid #ffaaaa;
    }
    .ball.blur {
        filter: blur(2px);
        transform: scale(0.9);
        opacity: 0.8;
    }

    /* 儀表板與卡片 */
    .status-container {
        display: flex; justify-content: space-around; background: #000;
        border: 2px solid #333; border-radius: 10px; padding: 10px; margin-bottom: 20px;
        box-shadow: 0 0 15px rgba(0, 229, 255, 0.2);
    }
    .status-item { text-align: center; font-size: 0.8em; color: #888; }
    .status-val { display: block; font-size: 1.1em; font-weight: bold; color: #00e5ff; margin-top: 5px;}

    .slot-frame {
        background: #222; border: 4px solid #444; border-radius: 15px;
        padding: 15px; margin-bottom: 20px; text-align: center;
        box-shadow: inset 0 0 20px #000;
        position: relative;
    }
    .slot-label {
        background: #000; color: #ffd700; padding: 2px 10px; border-radius: 5px;
        font-size: 0.9em; font-weight: bold; display: inline-block; margin-bottom: 10px;
        border: 1px solid #ffd700; box-shadow: 0 0 5px #ffd700;
    }
    
    /* 標題霓虹燈 */
    h1 { text-align: center; color: #ffd700; text-shadow: 0 0 10px #ff0000, 0 0 20px #ff0000; font-style: italic;}
    .subtitle { text-align: center; color: #aaa; font-size: 0.8em; margin-bottom: 20px; letter-spacing: 2px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. TINO 核心邏輯 (不變) ---
def get_zodiac(year):
    zodiacs = ["🐵", "🐔", "🐶", "🐷", "🐭", "🐮", "🐯", "🐰", "🐲", "🐍", "🐴", "🐑"]
    return zodiacs[year % 12]

def get_constellation(month, day):
    dates = (20, 19, 21, 20, 21, 22, 23, 23, 23, 24, 22, 22)
    constellations = ["♑", "♒", "♓", "♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐"]
    if day < dates[month-1]: return constellations[month-1]
    else: return constellations[month]

def get_element_luck(year):
    last_digit = int(str(year)[-1])
    if last_digit in [0, 1]: return "金", [4, 9, 0, 5]
    if last_digit in [2, 3]: return "水", [1, 6, 4, 9]
    if last_digit in [4, 5]: return "木", [3, 8, 1, 6]
    if last_digit in [6, 7]: return "火", [2, 7, 3, 8]
    if last_digit in [8, 9]: return "土", [5, 0, 2, 7]
    return "未知", []

def calculate_dynamic_seed(name, birth_date):
    now = datetime.now()
    # 微秒級擾動，確保每次按都不一樣
    time_str = now.strftime("%Y%m%d%H%M%S%f") 
    raw_str = f"{name}_{birth_date}_{time_str}"
    seed_val = int(hashlib.sha256(raw_str.encode('utf-8')).hexdigest(), 16)
    return seed_val

def calculate_element_distribution(main_element, seed):
    elements = ['金', '木', '水', '火', '土']
    random.seed(seed)
    values = [random.randint(40, 70) for _ in range(5)]
    if main_element in elements:
        idx = elements.index(main_element)
        values[idx] = random.randint(90, 100)
        support_map = {'金': 4, '木': 2, '水': 0, '火': 1, '土': 3}
        support_idx = support_map[main_element]
        values[support_idx] += random.randint(10, 20)
    return elements, values

def run_simulation(name, birth_date, audit_list):
    element_name, lucky_digits = get_element_luck(birth_date.year)
    zodiac = get_zodiac(birth_date.year)
    constellation = get_constellation(birth_date.month, birth_date.day)
    
    dynamic_seed = calculate_dynamic_seed(name, birth_date)
    random.seed(dynamic_seed)
    
    radar_labels, radar_values = calculate_element_distribution(element_name, dynamic_seed)
    
    weights = {i: 1.0 for i in range(1, 50)}
    for i in range(1, 50):
        if i % 10 in lucky_digits[:2]: weights[i] *= 2.5
        if i % 10 in lucky_digits[2:]: weights[i] *= 1.5
        name_hash = (dynamic_seed % 49) + 1
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
    dynamic_lucky = (dynamic_seed % 10)
    final_tails = list(set(base_tails + [dynamic_lucky]))
    while len(final_tails) < 3:
        extra = (dynamic_seed // 10) % 10
        if extra not in final_tails: final_tails.append(extra)
        dynamic_seed //= 10
    final_tails = final_tails[:3]
    random.shuffle(final_tails)
    
    return l_main, l_spec, s_main, s_spec, final_tails, element_name, zodiac, constellation, radar_labels, radar_values

# --- 3. App 介面佈局 ---

st.markdown("<h1>🎰 TINO LUCKY JACKPOT</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>V9.8 CASINO EDITION | PULL THE LEVER</div>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ 系統設定")
    audit_txt = st.text_input("🚫 排除號碼 (逗號隔開)", "")
    audit_list = []
    if audit_txt:
        try: audit_list = [int(x.strip()) for x in audit_txt.split(",")]
        except: pass

col1, col2 = st.columns(2)
with col1:
    u_name = st.text_input("👤 玩家姓名", value="", placeholder="輸入姓名")
with col2:
    u_dob = st.date_input("📅 玩家生日", value=date(2000, 1, 1), min_value=date(1900, 1, 1))

st.write("") 

# --- 拉霸動畫輔助函式 ---
def render_balls(numbers, special=None, is_blur=False):
    html = '<div class="ball-container">'
    blur_class = "blur" if is_blur else ""
    
    # 一般號碼
    for n in numbers:
        html += f'<div class="ball {blur_class}">{n:02d}</div>'
    
    # 特別號 (如果有)
    if special is not None:
        html += f'<div class="ball special {blur_class}">{special:02d}</div>'
        
    html += '</div>'
    return html

# --------------------------

if st.button("🔴 PULL LEVER (啟動拉霸)"):
    if not u_name:
        st.warning("⚠️ 請輸入玩家姓名以開始遊戲！")
    else:
        # 1. 準備版面
        placeholder_status = st.empty()
        placeholder_lotto = st.empty()
        placeholder_super = st.empty()
        placeholder_scratch = st.empty()
        
        # 2. 獲取真實結果
        l, ls, s, ss, t, elem, zod, const, r_labels, r_values = run_simulation(u_name, u_dob, audit_list)
        
        # 3. 顯示儀表板 (靜態)
        placeholder_status.markdown(f"""
        <div class="status-container">
            <div class="status-item">屬性<span class="status-val">{elem}</span></div>
            <div class="status-item">生肖<span class="status-val">{zod}</span></div>
            <div class="status-item">星座<span class="status-val">{const}</span></div>
        </div>
        """, unsafe_allow_html=True)

        # 4. 拉霸動畫 (Rolling Animation)
        # 第一階段：全速轉動 (模糊效果)
        for i in range(8):
            # 隨機生成假號碼
            fake_l = sorted(random.sample(range(1, 50), 6))
            fake_ls = random.randint(1, 49)
            fake_s = sorted(random.sample(range(1, 39), 6))
            fake_ss = random.randint(1, 8)
            fake_t = random.sample(range(0, 10), 3)
            
            placeholder_lotto.markdown(f"""
            <div class="slot-frame" style="border-color: #00e5ff;">
                <div class="slot-label">大樂透 SPINNING...</div>
                {render_balls(fake_l, fake_ls, is_blur=True)}
            </div>
            """, unsafe_allow_html=True)
            
            placeholder_super.markdown(f"""
            <div class="slot-frame" style="border-color: #00ff00;">
                <div class="slot-label">威力彩 SPINNING...</div>
                {render_balls(fake_s, fake_ss, is_blur=True)}
            </div>
            """, unsafe_allow_html=True)
            
            time.sleep(0.1) # 轉動速度
            
        # 第二階段：大樂透 逐個停下 (煞車效果)
        # 這邊簡化為顯示真實結果，去除模糊
        placeholder_lotto.markdown(f"""
        <div class="slot-frame" style="border-color: #00e5ff; box-shadow: 0 0 20px #00e5ff;">
            <div class="slot-label">💎 大樂透 LOTTO 649</div>
            {render_balls(l, ls, is_blur=False)}
        </div>
        """, unsafe_allow_html=True)
        time.sleep(0.5) # 停頓一下
        
        # 第三階段：威力彩 停下
        placeholder_super.markdown(f"""
        <div class="slot-frame" style="border-color: #00ff00; box-shadow: 0 0 20px #00ff00;">
            <div class="slot-label">💵 威力彩 SUPER LOTTO</div>
            {render_balls(s, ss, is_blur=False)}
        </div>
        """, unsafe_allow_html=True)
        time.sleep(0.5) # 停頓一下

        # 第四階段：刮刮樂 & 雷達圖 出現
        r_values.append(r_values[0])
        r_labels.append(r_labels[0])
        fig = go.Figure(data=go.Scatterpolar(
            r=r_values, theta=r_labels, fill='toself',
            line_color='#ffd700', fillcolor='rgba(255, 215, 0, 0.3)',
            marker=dict(color='#fff', size=6)
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=False, range=[0, 100]),
                angularaxis=dict(tickfont=dict(size=14, color='#e0e0e0'), rotation=90, direction='clockwise'),
                bgcolor='#222'
            ),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False, height=250, margin=dict(l=40, r=40, t=20, b=20)
        )
        
        placeholder_scratch.markdown(f"""
        <div class="slot-frame" style="border-color: #ffd700;">
            <div class="slot-label">🧧 刮刮樂尾數</div>
            <div style="font-size: 2em; color: #ffd700; font-weight: bold; letter-spacing: 5px;">
                {t[0]} > {t[1]} > {t[2]}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.plotly_chart(fig, use_container_width=True)
