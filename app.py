import streamlit as st
import random
import hashlib
from datetime import datetime, date
import time
import plotly.graph_objects as go

# --- 1. 系統初始化 ---
st.set_page_config(
    page_title="Tino Lucky Ball", 
    page_icon="🌌", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

if 'screenshot_mode' not in st.session_state:
    st.session_state['screenshot_mode'] = False
if 'last_result' not in st.session_state:
    st.session_state['last_result'] = None
if 'u_name' not in st.session_state:
    st.session_state['u_name'] = ""

# --- 2. CSS 渲染 (修復亂碼與版面) ---
st.markdown("""
<style>
    /* 全局設定 */
    .stApp { background-color: #000; color: #f0f0f0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    .block-container { 
        padding-top: 0.5rem !important; padding-bottom: 5rem !important; 
        padding-left: 0.8rem !important; padding-right: 0.8rem !important;
        max-width: 500px !important; 
    }

    /* 命理報告卡片 (新增) */
    .fate-report-card {
        background: linear-gradient(180deg, #1a0505 0%, #000 100%);
        border: 2px solid #ff4444;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 20px;
        box-shadow: 0 0 15px rgba(255, 68, 68, 0.3);
        text-align: left;
    }
    .fate-title { color: #ffd700; font-size: 1.1em; font-weight: bold; margin-bottom: 8px; border-bottom: 1px solid #444; padding-bottom: 5px; }
    .fate-content { color: #ddd; font-size: 0.95em; line-height: 1.5; margin-bottom: 10px; }
    .highlight-text { color: #00e5ff; font-weight: bold; }

    /* 拉霸機外殼 */
    .slot-machine-casing {
        background: linear-gradient(135deg, #1a1a1a 0%, #050505 100%);
        border: 4px solid #ffd700; border-radius: 25px; padding: 15px;
        box-shadow: 0 0 30px rgba(255, 215, 0, 0.2), inset 0 0 50px #000;
        margin-bottom: 15px; position: relative;
    }
    .machine-top {
        text-align: center; background: #3a0000; border-radius: 15px;
        padding: 12px 5px; margin-bottom: 15px; border: 2px solid #ff3333;
        box-shadow: 0 0 15px #ff0000, inset 0 0 20px #000;
    }
    .machine-title {
        color: #ffeb3b; font-weight: 900; font-size: 7.5vw; letter-spacing: 2px;
        text-shadow: 0 0 8px #ff0000; margin: 0; font-style: italic; white-space: nowrap;
    }
    
    /* 捲軸視窗 */
    .reel-window {
        background: #000; border: 2px solid #333; border-radius: 12px;
        margin-bottom: 10px; padding: 10px 2px; box-shadow: inset 0 0 20px #000;
    }
    .reel-label {
        font-size: 0.7em; color: #888; font-weight: bold; text-transform: uppercase;
        margin-bottom: 5px; text-align: center; letter-spacing: 1.5px;
    }
    .reel-label.main { color: #00e5ff; text-shadow: 0 0 5px #00e5ff; }
    .reel-label.super { color: #00ff00; text-shadow: 0 0 5px #00ff00; }
    .reel-label.scratch { color: #ffd700; text-shadow: 0 0 5px #ffd700; }

    /* --- 數字球 (亂碼修復關鍵) --- */
    .ball-container { 
        display: flex; justify-content: center; gap: 4px; flex-wrap: nowrap; width: 100%; 
    }
    .ball {
        width: 38px; height: 38px;  /* 固定大小 */
        min-width: 32px; /* 最小寬度防止擠壓 */
        border-radius: 50%;
        background: radial-gradient(circle at 30% 30%, #ffffff, #bbbbbb);
        color: #000; font-weight: 900; 
        font-size: 16px; /* 固定字體大小，避免 vw 計算錯誤導致亂碼 */
        display: flex; align-items: center; justify-content: center;
        border: 1.5px solid #000; box-shadow: 1px 1px 4px rgba(0,0,0,0.8); 
        flex-shrink: 0; /* 禁止壓縮 */
    }
    .ball.special { background: radial-gradient(circle at 30% 30%, #ff3333, #990000); color: white; border: 1.5px solid #ff9999; }
    
    .scratch-num { font-size: 2em; font-weight: 900; color: #ffd700; text-shadow: 0 0 12px #ff9900; letter-spacing: 12px; text-align: center; }

    /* 拉桿按鈕 */
    .stButton { text-align: center; }
    div.stButton > button {
        width: 90px !important; height: 90px !important; border-radius: 50% !important;
        background: radial-gradient(circle at 30% 30%, #ff4444, #990000) !important;
        border: 4px solid #cc0000 !important;
        box-shadow: 0 8px 0 #550000, 0 15px 20px rgba(0,0,0,0.6) !important;
        color: white !important; font-weight: bold !important; font-size: 1.1em !important; margin: 10px auto !important;
    }
    div.stButton > button:active { transform: translateY(8px) !important; box-shadow: 0 0 0 #550000, inset 0 0 20px rgba(0,0,0,0.8) !important; }
    
    .status-bar { display: flex; justify-content: space-between; background: #111; border-radius: 8px; padding: 8px 15px; margin-bottom: 12px; border: 1px solid #333; }
    .status-txt { color: #fff; font-size: 0.8em; }
    .status-highlight { color: #00e5ff; font-weight: bold; margin-left: 3px; }
    
    /* 手機版強制修正 */
    @media only screen and (max-width: 420px) {
        .ball { width: 32px !important; height: 32px !important; font-size: 14px !important; }
        .ball-container { gap: 2px !important; }
        .machine-title { font-size: 8vw; }
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 邏輯層 ---

def get_zodiac(year):
    zods = ["🐵", "🐔", "🐶", "🐷", "🐭", "🐮", "🐯", "🐰", "🐲", "🐍", "🐴", "🐑"]
    return zods[year % 12]

def get_constellation(month, day):
    dates = (20, 19, 21, 20, 21, 22, 23, 23, 23, 24, 22, 22)
    consts = ["♑", "♒", "♓", "♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐"]
    return consts[month-1] if day < dates[month-1] else consts[month]

def get_element_by_year(year):
    last = year % 10
    mapping = {0:"金", 1:"金", 2:"水", 3:"水", 4:"木", 5:"木", 6:"火", 7:"火", 8:"土", 9:"土"}
    return mapping.get(last, "未知")

element_tails = { "金": [4,9,0,5], "木": [3,8,1,6], "水": [1,6,4,9], "火": [2,7,3,8], "土": [0,5,2,7] }

def check_smart_filters(numbers):
    if sum(1 for n in numbers if n <= 31) > 4: return False
    sn = sorted(numbers)
    if sum(1 for i in range(len(sn)-1) if sn[i+1] == sn[i]+1) > 2: return False
    if all(n < 25 for n in sn): return False
    if len(set([sn[i+1]-sn[i] for i in range(len(sn)-1)])) == 1: return False
    return True

def generate_rational_numbers(lucky_digits, seed, pool_range=49):
    random.seed(seed)
    for _ in range(300):
        l1_pool = [n for n in range(1, pool_range+1) if n % 10 in lucky_digits]
        l1_nums = random.sample(l1_pool, 2)
        l2_pool = [n for n in range(1, pool_range+1) if n not in l1_nums]
        l2_nums = random.sample(l2_pool, 4)
        final = l1_nums + l2_nums
        if check_smart_filters(final): return sorted(final)
    return sorted(final)

def generate_cosmic_data(name, element, zodiac, constellation, seed, birth_year):
    """
    生成結構化的命理數據 (不生成 HTML，改為回傳字典以便排版)
    """
    random.seed(seed)
    
    # 1. 天干地支
    gan_list = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    zhi_list = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
    gan_idx = (birth_year - 4) % 10
    zhi_idx = (birth_year - 4) % 12
    ganzhi = f"{gan_list[gan_idx]}{zhi_list[zhi_idx]}"
    
    # 2. 姓名靈動
    name_analyses = [
        "外圓內方，領袖運強，決策果斷", "財庫飽滿，直覺敏銳，偏財運旺",
        "順水推舟，貴人相助，順勢而為", "五行相生，人脈通達，氣場強大",
        "突破重圍，開創格局，意外之喜", "穩健佈局，步步為營，積沙成塔"
    ]
    name_result = name_analyses[seed % len(name_analyses)]

    # 3. 紫微斗數主星
    ziwei_stars = [
        ("紫微星", "帝王之星，氣場強大，今日財運由您主導。"),
        ("天機星", "智慧之星，反應敏捷，靈感將是關鍵。"),
        ("太陽星", "權貴之星，正財運旺盛，適合大方下注。"),
        ("武曲星", "正財之星，金氣剛毅，執行力強，財庫穩固。"),
        ("天同星", "福星高照，不勞而獲，偏財運極佳。"),
        ("廉貞星", "公關之星，人緣帶財，相信第一直覺。"),
        ("天府星", "天之庫房，納財守成，適合穩健佈局。"),
        ("太陰星", "田宅之主，財運如水，晚間運勢更佳。"),
        ("貪狼星", "慾望之星，偏財最旺，今日適合放手一搏。"),
        ("巨門星", "暗財之星，需低調行事，憑隱密訊息獲利。"),
        ("天相星", "印星掌印，跟隨強者下注或合資大吉。"),
        ("天梁星", "蔭星庇佑，逢凶化吉，若有靈感突現必有後福。"),
        ("七殺星", "將軍之星，衝鋒陷陣，成敗一線，適合單點突破。"),
        ("破軍星", "耗星變動，先破後立，今日運勢起伏大，或有奇蹟。")
    ]
    my_star = ziwei_stars[seed % 14]

    # 4. 流日星曜
    daily_guides = [
        "祿存入局，財氣加倍", "化權坐守，掌握先機", "化科顯耀，名利雙收", 
        "左輔右弼，左右逢源", "文昌文曲，靈感湧現"
    ]
    daily_star = random.choice(daily_guides)
    
    return {
        'ganzhi': ganzhi,
        'element': element,
        'name_result': name_result,
        'star_name': my_star[0],
        'star_desc': my_star[1],
        'daily_star': daily_star
    }

def run_simulation(name, dob):
    elem = get_element_by_year(dob.year)
    tails = element_tails.get(elem, [1,6])
    zod = get_zodiac(dob.year)
    const = get_constellation(dob.month, dob.day)
    
    dynamic_seed = int(hashlib.sha256(f"{name}{dob}{datetime.now().strftime('%f')}".encode()).hexdigest(), 16) % (10**8)
    
    l_main = generate_rational_numbers(tails, dynamic_seed)
    l_spec = random.randint(1, 49)
    while l_spec in l_main: l_spec = random.randint(1, 49)
    
    s_main = generate_rational_numbers(tails, dynamic_seed + 99, 38)
    s_spec = random.randint(1, 8)
    
    t_pool = [n for n in tails]
    t_nums = random.sample(t_pool, 2) + [int(datetime.now().strftime('%S')) % 10]
    random.shuffle(t_nums)
    
    # 獲取命理數據
    fate_data = generate_cosmic_data(name, elem, zod, const, dynamic_seed, dob.year)
    
    elements = ['金', '木', '水', '火', '土']
    r_vals = [random.randint(40, 70) for _ in range(5)]
    if elem in elements: r_vals[elements.index(elem)] = 95
    
    return {
        'l': l_main, 'ls': l_spec, 's': s_main, 'ss': s_spec, 't': t_nums,
        'elem': elem, 'zod': zod, 'const': const, 'fate': fate_data,
        'r_labels': elements, 'r_vals': r_vals
    }

def render_balls(numbers, special=None):
    html = '<div class="ball-container">'
    for n in numbers: html += f'<div class="ball">{n:02d}</div>'
    if special: html += f'<div class="ball special">{special:02d}</div>'
    return html + '</div>'

# --- 4. 介面流程 ---

st.markdown("<h1>🎱 Tino Lucky Ball</h1>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center; color:#666; font-size:0.8em; margin-bottom:20px;'>TINO COSMIC ENGINE V10.9</div>", unsafe_allow_html=True)

if not st.session_state['screenshot_mode']:
    col_x, col_btn, col_y = st.columns([1, 1, 1])
    with col_btn: spin_btn = st.button("SPIN")
    
    c1, c2 = st.columns(2)
    # 修正：預設值為空與通用日期
    with c1: u_name = st.text_input("玩家姓名", value="", placeholder="請輸入姓名")
    with c2: u_dob = st.date_input("生日日期", value=date(2000, 1, 1), min_value=date(1900, 1, 1), max_value=date(2030, 12, 31))

    if spin_btn:
        if not u_name: st.warning("請輸入姓名")
        else:
            if u_dob > date.today(): st.toast("🛸 未來人訊號...", icon="👽")
            st.session_state['u_name'] = u_name
            ph = st.empty()
            for _ in range(5): # 縮短一點時間
                fake_l = sorted(random.sample(range(1, 50), 6))
                ph.markdown(f'<div class="slot-machine-casing"><div class="machine-top"><h1 class="machine-title">ANALYZING...</h1></div><div class="reel-window">{render_balls(fake_l)}</div></div>', unsafe_allow_html=True)
                time.sleep(0.05)
            ph.empty()
            st.session_state['last_result'] = run_simulation(u_name, u_dob)

# --- 5. 結果呈現 (調整順序：命理在先，號碼在後) ---

if st.session_state['last_result']:
    res = st.session_state['last_result']
    f = res['fate']
    
    # 1. 命學推論卡片 (置頂顯示)
    st.markdown(f"""
    <div class="fate-report-card">
        <div class="fate-title">🌌 命盤與運勢推演 ({st.session_state['u_name']})</div>
        <div class="fate-content">
            <span class="highlight-text">【先天根基】</span> {f['ganzhi']}年 ({res['zod']})，五行屬{f['element']}。<br>
            <span class="highlight-text">【姓名靈動】</span> {f['name_result']}<br>
            <span class="highlight-text">【紫微主星】</span> <strong>{f['star_name']}</strong> — {f['star_desc']}<br>
            <span class="highlight-text">【今日指引】</span> {f['daily_star']}，機率雲正在坍縮。
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. 拉霸機 (開獎結果)
    st.markdown(f"""
    <div class="slot-machine-casing">
        <div class="machine-top"><h1 class="machine-title">TINO LUCKY BALL</h1></div>
        <div class="status-bar">
            <div>屬性 <span class="status-highlight">{res['elem']}</span></div>
            <div>生肖 <span class="status-highlight">{res['zod']}</span></div>
            <div>星座 <span class="status-highlight">{res['const']}</span></div>
        </div>
        <div class="reel-window">
            <div class="reel-label main">大樂透 LOTTO 649</div>
            {render_balls(res['l'], res['ls'])}
        </div>
        <div class="reel-window">
            <div class="reel-label super">威力彩 SUPER LOTTO</div>
            {render_balls(res['s'], res['ss'])}
        </div>
        <div class="reel-window">
            <div class="reel-label scratch">刮刮樂尾數</div>
            <div class="scratch-num">{res['t'][0]} &nbsp; {res['t'][1]} &nbsp; {res['t'][2]}</div>
        </div>
    </div>""", unsafe_allow_html=True)
    
    # 3. 雷達圖
    with st.expander("📊 五行能量分析"):
        r_vals = res['r_vals'] + [res['r_vals'][0]]
        fig = go.Figure(data=go.Scatterpolar(r=r_vals, theta=res['r_labels']+['金'], fill='toself', line_color='#00e5ff', fillcolor='rgba(0, 229, 255, 0.2)'))
        fig.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 100]), bgcolor='rgba(0,0,0,0)'), paper_bgcolor='rgba(0,0,0,0)', showlegend=False, height=220, margin=dict(l=40, r=40, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    if st.button("📸 戰報模式切換"):
        st.session_state['screenshot_mode'] = not st.session_state['screenshot_mode']
        st.rerun()
