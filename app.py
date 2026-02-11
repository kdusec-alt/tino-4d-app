import streamlit as st
import random
import hashlib
from datetime import datetime, date
import time
import plotly.graph_objects as go

# --- 1. 頁面與 iPhone 適配設定 ---
st.set_page_config(
    page_title="Tino Lucky Slot", 
    page_icon="🎰", 
    layout="wide", # 改為 wide 以便在寬螢幕並排，手機會自動適配
    initial_sidebar_state="collapsed"
)

# 初始化 Session State 用於截圖模式
if 'screenshot_mode' not in st.session_state:
    st.session_state['screenshot_mode'] = False
if 'last_result' not in st.session_state:
    st.session_state['last_result'] = None

# CSS 黑金賭城風格 (針對 iPhone 優化)
st.markdown("""
    <style>
    /* 全局設定 */
    .stApp { background-color: #121212; color: #f0f0f0; font-family: -apple-system, BlinkMacSystemFont, sans-serif; }
    
    /* 去除上方多餘空白，讓手機畫面更緊湊 */
    .block-container { padding-top: 1rem; padding-bottom: 5rem; }

    /* 拉霸機拉桿按鈕 (Lever Button) */
    .stButton>button { 
        width: 100%; border-radius: 15px; height: 50px; 
        background: linear-gradient(180deg, #ff3333 0%, #990000 100%); 
        color: white; font-size: 1.2em; font-weight: 800; border: 3px solid #ffd700; 
        box-shadow: 0 4px 0 #660000, 0 5px 10px rgba(0,0,0,0.5);
        text-transform: uppercase; letter-spacing: 1px;
        transition: all 0.1s;
        display: flex; align-items: center; justify-content: center;
    }
    .stButton>button:active {
        transform: translateY(4px);
        box-shadow: 0 0 0 #660000, 0 2px 2px rgba(0,0,0,0.5);
        background: linear-gradient(180deg, #cc0000 0%, #660000 100%);
    }
    
    /* 截圖模式按鈕 (特別樣式) */
    .screenshot-btn button {
        background: transparent !important;
        border: 1px solid #444 !important;
        color: #888 !important;
        box-shadow: none !important;
        height: 35px !important;
        font-size: 0.9em !important;
    }

    /* 數字球樣式 (iPhone 適配版：縮小尺寸以防換行) */
    .ball-container {
        display: flex; justify-content: center; gap: 6px; flex-wrap: nowrap; margin: 10px 0; overflow-x: auto;
    }
    .ball {
        min-width: 40px; width: 40px; height: 40px; border-radius: 50%;
        background: radial-gradient(circle at 30% 30%, #ffffff, #d0d0d0, #909090);
        color: #222; font-weight: 900; font-size: 18px;
        display: flex; align-items: center; justify-content: center;
        box-shadow: inset -3px -3px 5px rgba(0,0,0,0.3), 2px 2px 4px rgba(0,0,0,0.5);
        border: 2px solid #fff;
        font-family: 'Helvetica Neue', Arial, sans-serif;
    }
    .ball.special {
        background: radial-gradient(circle at 30% 30%, #ff4b4b, #cc0000);
        color: white; border: 2px solid #ffaaaa;
    }
    .ball.blur { filter: blur(2px); transform: scale(0.9); opacity: 0.8; }

    /* 儀表板 */
    .status-container {
        display: flex; justify-content: space-between; background: #1a1a1a;
        border: 1px solid #333; border-radius: 12px; padding: 10px 15px; margin-bottom: 15px;
    }
    .status-item { text-align: center; font-size: 0.75em; color: #888; }
    .status-val { display: block; font-size: 1.2em; font-weight: bold; color: #00e5ff; margin-top: 2px;}

    /* 卡片容器 */
    .slot-frame {
        background: #1e1e1e; border: 2px solid #333; border-radius: 12px;
        padding: 10px; margin-bottom: 12px; text-align: center;
        position: relative;
    }
    .slot-label {
        color: #ffd700; font-size: 0.8em; font-weight: bold; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 1px;
    }
    
    /* 標題 */
    h1 { text-align: center; color: #ffd700; text-shadow: 0 0 15px rgba(255, 215, 0, 0.5); margin: 0; padding: 0; font-size: 1.8em; font-style: italic;}
    .subtitle { text-align: center; color: #666; font-size: 0.7em; margin-bottom: 15px; letter-spacing: 2px; }
    
    /* 隱藏 Streamlit 預設元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. 邏輯核心 (V9.8) ---
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
    time_str = now.strftime("%Y%m%d%H%M%S%f") 
    raw_str = f"{name}_{birth_date}_{time_str}"
    seed_val = int(hashlib.sha256(raw_str.encode('utf-8')).hexdigest(), 16)
    return seed_val

def calculate_element_distribution(main_element, seed):
    elements = ['金', '木', '水', '火', '土']
    random.seed(seed)
    values = [random.randint(30, 60) for _ in range(5)] # 降低基礎值讓圖形更明顯
    if main_element in elements:
        idx = elements.index(main_element)
        values[idx] = random.randint(90, 100)
        support_map = {'金': 4, '木': 2, '水': 0, '火': 1, '土': 3}
        support_idx = support_map[main_element]
        values[support_idx] += random.randint(15, 30)
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
    
    return {
        'l': l_main, 'ls': l_spec, 's': s_main, 'ss': s_spec, 't': final_tails,
        'elem': element_name, 'zod': zodiac, 'const': constellation,
        'r_labels': radar_labels, 'r_values': radar_values
    }

def render_balls(numbers, special=None, is_blur=False):
    html = '<div class="ball-container">'
    blur_class = "blur" if is_blur else ""
    for n in numbers:
        html += f'<div class="ball {blur_class}">{n:02d}</div>'
    if special is not None:
        html += f'<div class="ball special {blur_class}">{special:02d}</div>'
    html += '</div>'
    return html

# --- 3. App 流程 ---

# 標題 (只有在非截圖模式下顯示完整標題，截圖模式顯示簡潔版)
if not st.session_state['screenshot_mode']:
    st.markdown("<h1>🎰 TINO LUCKY JACKPOT</h1>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>V9.9 CASINO EDITION</div>", unsafe_allow_html=True)
else:
    # 截圖模式下的標題
    st.markdown("<h1>🎱 TINO DECISION CORE</h1>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>QUANTUM PREDICTION RESULT</div>", unsafe_allow_html=True)

# 側邊欄 (審計)
with st.sidebar:
    st.header("⚙️")
    audit_txt = st.text_input("排除號碼", "")
    audit_list = []
    if audit_txt:
        try: audit_list = [int(x.strip()) for x in audit_txt.split(",")]
        except: pass

# --- 輸入區與按鈕區 (截圖模式下隱藏) ---
if not st.session_state['screenshot_mode']:
    col_input1, col_input2 = st.columns(2)
    with col_input1:
        u_name = st.text_input("玩家姓名", value="", placeholder="輸入姓名")
    with col_input2:
        u_dob = st.date_input("玩家生日", value=date(2000, 1, 1), min_value=date(1900, 1, 1))

    st.write("") # Spacer

    if st.button("🔴 拉動拉霸 (PULL LEVER)"):
        if not u_name:
            st.warning("⚠️ 請輸入姓名！")
        else:
            # 儲存使用者資訊
            st.session_state['u_name'] = u_name
            
            # 動畫與計算
            placeholder = st.empty()
            
            # 動畫階段
            for i in range(5): # 稍微縮短動畫時間讓體驗更流暢
                fake_l = sorted(random.sample(range(1, 50), 6))
                fake_ls = random.randint(1, 49)
                placeholder.markdown(render_balls(fake_l, fake_ls, is_blur=True), unsafe_allow_html=True)
                time.sleep(0.1)
            
            placeholder.empty()
            
            # 計算並存入 Session
            result = run_simulation(u_name, u_dob, audit_list)
            st.session_state['last_result'] = result

# --- 結果顯示區 (如果有結果) ---
if st.session_state['last_result']:
    res = st.session_state['last_result']
    
    # 1. 儀表板
    st.markdown(f"""
    <div class="status-container">
        <div class="status-item">屬性<span class="status-val">{res['elem']}</span></div>
        <div class="status-item">生肖<span class="status-val">{res['zod']}</span></div>
        <div class="status-item">星座<span class="status-val">{res['const']}</span></div>
    </div>
    """, unsafe_allow_html=True)

    # 2. 佈局核心：使用 columns 將 號碼(左/上) 和 雷達圖(右/下) 分開
    # 在手機上 st.columns 會自動堆疊，所以這是完美的響應式設計
    col_res, col_chart = st.columns([1.3, 1])
    
    with col_res:
        # 大樂透
        st.markdown(f"""
        <div class="slot-frame" style="border-color: #00e5ff;">
            <div class="slot-label">大樂透 Lotto 649</div>
            {render_balls(res['l'], res['ls'])}
        </div>
        """, unsafe_allow_html=True)

        # 威力彩
        st.markdown(f"""
        <div class="slot-frame" style="border-color: #00ff00;">
            <div class="slot-label">威力彩 Super Lotto</div>
            {render_balls(res['s'], res['ss'])}
        </div>
        """, unsafe_allow_html=True)
        
        # 刮刮樂
        t = res['t']
        st.markdown(f"""
        <div class="slot-frame" style="border-color: #ffd700;">
            <div class="slot-label">刮刮樂 Scratch</div>
            <div style="font-size: 1.5em; color: #ffd700; font-weight: 900; letter-spacing: 3px;">
                {t[0]} > {t[1]} > {t[2]}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_chart:
        # 五行雷達圖
        r_vals = res['r_values'] + [res['r_values'][0]]
        r_labs = res['r_labels'] + [res['r_labels'][0]]
        
        fig = go.Figure(data=go.Scatterpolar(
            r=r_vals, theta=r_labs, fill='toself',
            line_color='#00e5ff', fillcolor='rgba(0, 229, 255, 0.2)',
            marker=dict(color='#fff', size=4)
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=False, range=[0, 100]),
                angularaxis=dict(tickfont=dict(size=10, color='#aaa'), rotation=90, direction='clockwise'),
                bgcolor='rgba(0,0,0,0)'
            ),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False, 
            height=250, # 高度縮小以適配手機
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

    # --- 截圖模式切換按鈕 ---
    st.write("---")
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if not st.session_state['screenshot_mode']:
            if st.button("📸 開啟截圖模式"):
                st.session_state['screenshot_mode'] = True
                st.rerun()
        else:
            if st.button("🔙 返回操作模式"):
                st.session_state['screenshot_mode'] = False
                st.rerun()
                
    with col_btn2:
        if st.session_state['screenshot_mode']:
            st.caption("✨ 現在畫面最乾淨，請直接使用手機截圖！")
