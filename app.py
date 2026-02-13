import streamlit as st
import random
import hashlib
from datetime import datetime, date, timedelta
import time
import plotly.graph_objects as go
import calendar

# ==========================================
# 1. 系統核心配置
# ==========================================
st.set_page_config(
    page_title="Tino Lucky Ball",
    page_icon="🌌",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 強制台灣時間
def get_taiwan_time():
    return datetime.utcnow() + timedelta(hours=8)

if 'last_result' not in st.session_state:
    st.session_state['last_result'] = None

# ==========================================
# 2. CSS 樣式表 (手機極致優化版)
# ==========================================
st.markdown("""
<style>
/* 全局黑金風格 */
.stApp { background: #000; color: #eee; font-family: "Microsoft JhengHei", sans-serif; }
.block-container { padding: 0.5rem 0.8rem 1rem !important; max-width: 520px !important; }

/* 標題 */
h2 { margin: 0.4rem 0 0.8rem !important; font-size: 1.6em !important; text-align: center; color: #ffd700; text-shadow: 0 0 10px #ff0000; }

/* 輸入優化 */
div[data-testid="stHorizontalBlock"] { gap: 0.5rem; }
input[type="number"] {
    background-color: #111 !important; color: #eee !important; border: 1px solid #444 !important;
    border-radius: 6px !important; text-align: center !important; font-weight: bold !important;
}

/* 戰報與顯示 */
.today-info {
    text-align: center; font-size: 0.85em; color: #ffcc00; margin: 0.3rem 0 0.8rem; padding: 6px;
    background: rgba(255,204,0,0.05); border-radius: 6px; letter-spacing: 1px; border: 1px solid #332200;
}
.fate-card { 
    background: linear-gradient(180deg, #0f0505 0%, #000 100%);
    border: 1px solid #ff4444; border-radius: 12px; padding: 15px; margin: 0.5rem 0; 
    box-shadow: 0 4px 15px rgba(255, 68, 68, 0.1);
}
.fate-header { 
    font-size: 1.2em; color: #ffd700; margin-bottom: 10px; font-weight: bold; 
    border-bottom: 1px solid #331111; padding-bottom: 8px; text-align: center;
}
/* 文案優化：行高拉大，閱讀舒適 */
.fate-content { font-size: 0.95em; line-height: 1.7; color: #ddd; text-align: justify; letter-spacing: 0.5px; }

/* 主星 */
.main-star-box { margin-bottom: 10px; }
.main-star-name { color: #ffeb3b; font-size: 1.4em; font-weight: bold; display: block; margin-bottom: 8px; text-shadow: 0 0 8px #ff9900; }

/* 樂透區 */
.slot-machine { background: #0a0a0a; border: 2px solid #ffd700; border-radius: 12px; padding: 10px; margin-top: 20px; margin-bottom: 20px;}
.machine-title { font-size: 1.3em; margin: 0 0 8px; text-align: center; color: #ffeb3b; font-weight: bold; font-style: italic; }
.reel-box { margin: 8px 0; padding: 8px 4px; border-radius: 8px; background: #000; border: 1px solid #333; }
.reel-label { font-size: 0.8em; margin-bottom: 5px; text-align: center; color: #00e5ff; letter-spacing: 1px; }
.ball-row { display: flex; justify-content: center; gap: 4px; flex-wrap: nowrap; overflow-x: auto; }
.ball {
    width: 32px !important; height: 32px !important; min-width: 32px !important;
    border-radius: 50% !important; background: radial-gradient(circle at 30% 30%, #fff, #ccc);
    color: #000; font-weight: bold; font-size: 14px;
    display: flex; align-items: center; justify-content: center;
    border: 1px solid #333; flex-shrink: 0;
}
.ball.special { background: radial-gradient(circle at 30% 30%, #ff3333, #990000); color: white; border: 1px solid #ff8888; }
.scratch-text { font-size: 1.8em; color: #ffd700; text-align: center; letter-spacing: 6px; margin-top: 4px; font-weight: 900; text-shadow: 0 0 8px #ff9900; }

/* 底部警示 */
.disclaimer-box { margin-top: 30px; padding-top: 15px; border-top: 1px solid #333; text-align: center; color: #666; font-size: 0.75em; line-height: 1.5; }

/* 按鈕 */
div.stButton > button {
    width: 100%; height: 50px; border-radius: 25px;
    background: linear-gradient(180deg, #ff4444 0%, #cc0000 100%);
    border: 2px solid #ffd700; color: white; font-weight: bold; font-size: 1.2em;
    box-shadow: 0 4px 0 #880000; margin-top: 10px;
}
div.stButton > button:active { transform: translateY(2px); box-shadow: 0 0 0 #880000; }

@media (max-width: 480px) { .main-star-name { font-size: 1.3em; } .ball { width: 28px !important; height: 28px !important; font-size: 12px !important; } }
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. 核心邏輯 (後台運算保留，前台顯示淨化)
# ==========================================

GAN = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
ZHI = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]

# 紫微資料庫 (完全移除數字，純大師敘事)
ZIWEI_STARS = [
    ("紫微", "帝王降臨", "紫微星入局，氣象萬千。今日氣場如帝王親臨，能壓制一切煞氣。適合展現魄力，鎖定心中首選。若有猶豫，請相信自己的第一直覺，勿受他人雜音干擾。", "BALANCED"),
    ("天機", "智謀百出", "天機化氣為善，主智慧與靈動。今日思緒敏捷，靈感如泉湧。若腦海中突然閃過某個念頭或畫面，請務必把握，那可能是宇宙傳遞的訊號。", "FLOW"),
    ("太陽", "光芒萬丈", "太陽高照，正財旺盛。今日格局光明磊落，氣場正向強大。不宜走偏門或過於投機，適合大方下注，財氣將隨陽光普照，心態越正，運勢越旺。", "AGGRESSIVE"),
    ("武曲", "剛毅果決", "武曲為財帛主，金氣剛毅。今日財庫穩固，決策應果斷明快。看準目標後，不宜猶豫不決。保持堅定的信念，財神自會眷顧。", "BALANCED"),
    ("天同", "福星高照", "天同坐守，主福氣享受。今日偏財運佳，適合抱著輕鬆、玩樂的心態參與。無心插柳往往柳成蔭，越是不在意，驚喜越容易降臨。", "FLOW"),
    ("廉貞", "公關之神", "廉貞主變化，氣場多端。今日直覺敏銳，能量帶有跳躍性。適合嘗試非傳統的選擇，或打破過往的習慣，變動中藏有轉機。", "FLOW"),
    ("天府", "庫房充盈", "天府為財庫之主，主守成。今日運勢穩健厚實，不宜過於冒進。適合採取穩紮穩打的策略，避開極端風險，細水長流方為上策。", "CONSERVATIVE"),
    ("太陰", "財運如水", "太陰主富，財運如水般靜謐流動。今日不宜急躁搶進，建議採取柔性佈局。若心中有猶豫，請選擇讓您感到平靜安穩的組合，晚間氣場更佳。", "FLOW"),
    ("貪狼", "慾望之主", "貪狼化祿，為第一大偏財星。今日慾望強烈，投機運勢爆發。適合放手一搏，順應內心的渴望。或許那些平時不敢碰的選擇，正是今日的鑰匙。", "AGGRESSIVE"),
    ("巨門", "深思熟慮", "巨門主暗，財運隱藏於深處。今日不宜張揚，需低調行事。請相信自己深思熟慮後的分析，不隨波逐流。沈默是金，財不露白。", "CONSERVATIVE"),
    ("天相", "輔佐得力", "天相掌印，主平衡與輔佐。今日運勢平穩和諧，氣場圓融。適合參考過往的熱門指標，或跟隨他人的幸運指引，借力使力。", "BALANCED"),
    ("天梁", "逢凶化吉", "天梁為蔭星，主呈祥解厄。今日雖無橫財爆發之象，但有意外之福。保持平常心，不強求、不執著，幸運自然會在轉角處降臨。", "CONSERVATIVE"),
    ("七殺", "將軍出征", "七殺主肅殺，成敗在於一線。今日運勢起伏較大，氣場銳利。適合單點突破，選擇一組信念堅定的組合堅持到底，勇者無懼。", "AGGRESSIVE"),
    ("破軍", "先破後立", "破軍主變動，舊的不去新的不來。今日適合打破常規，選擇平時絕對不會選的標的。破壞後的重建，往往蘊藏著巨大的機會。", "AGGRESSIVE")
]

def get_ganzhi_year(year):
    return f"{GAN[(year-4)%10]}{ZHI[(year-4)%12]}"
def get_ganzhi_month(year_gan_idx, month):
    start_gan_idx = (year_gan_idx % 5) * 2 + 2 
    current_gan_idx = (start_gan_idx + (month - 1)) % 10
    current_zhi_idx = (2 + (month - 1)) % 12 
    return f"{GAN[current_gan_idx]}{ZHI[current_zhi_idx]}"
def get_ganzhi_day(d):
    base_date = date(1900, 1, 1) 
    days_diff = (d - base_date).days
    offset = (10 + days_diff) % 60
    return f"{GAN[offset % 10]}{ZHI[offset % 12]}"
def get_ganzhi_hour(day_gan_idx, hour_zhi_idx):
    start_gan = (day_gan_idx % 5) * 2
    hour_gan_idx = (start_gan + hour_zhi_idx) % 10
    return f"{GAN[hour_gan_idx]}{ZHI[hour_zhi_idx]}"

def calculate_real_fate(name, dob, birth_hour):
    # 1. 四柱推算 (後台運算用，不輸出到前台)
    y_gz = get_ganzhi_year(dob.year)
    year_gan_idx = GAN.index(y_gz[0])
    m_gz = get_ganzhi_month(year_gan_idx, dob.month)
    d_gz = get_ganzhi_day(dob)
    if birth_hour >= 23 or birth_hour < 1: h_idx = 0
    else: h_idx = (birth_hour + 1) // 2 % 12
    day_gan_idx = GAN.index(d_gz[0])
    h_gz = get_ganzhi_hour(day_gan_idx, h_idx)
    
    # 2. 真實時系排盤
    fate_seed = int(hashlib.sha256(f"{name}{dob}{birth_hour}".encode()).hexdigest(), 16)
    star_idx = fate_seed % 14
    my_star = ZIWEI_STARS[star_idx]
    
    # 3. 五行強度 (用於雷達圖)
    wuxing_map = {"甲":"木","乙":"木","丙":"火","丁":"火","戊":"土","己":"土","庚":"金","辛":"金","壬":"水","癸":"水",
                  "子":"水","丑":"土","寅":"木","卯":"木","辰":"土","巳":"火","午":"火","未":"土","申":"金","酉":"金","戌":"土","亥":"水"}
    pillars = [y_gz, m_gz, d_gz, h_gz]
    elements = {'金':0, '木':0, '水':0, '火':0, '土':0}
    for p in pillars:
        elements[wuxing_map[p[0]]] += 1
        elements[wuxing_map[p[1]]] += 1
    r_vals = []
    r_labs = ['金','木','水','火','土']
    for e in r_labs:
        base = 40; count = elements[e]
        r_vals.append(base + count * 12)
    max_elem = max(elements, key=elements.get)
    
    return {
        'star_name': my_star[0],
        'star_short': my_star[1],
        'star_desc': my_star[2],
        'strategy': my_star[3],
        'r_vals': r_vals,
        'r_labs': r_labs,
        'main_elem': max_elem,
        'ganzhi_year': y_gz, # 只保留年柱給介面顯示
        'ganzhi_elem': max_elem
    }

# ==========================================
# 4. 數學核心：逐次消去法
# ==========================================
def calculate_variable_numbers(lucky_digits, strategy):
    tw_now = get_taiwan_time()
    now_seed = int(hashlib.sha256(tw_now.strftime("%Y%m%d%H%M%S%f").encode()).hexdigest(), 16)
    random.seed(now_seed)
    pool = list(range(1, 50)); weights = [1] * 49
    if strategy == 'CONSERVATIVE':
        for i in range(14, 35): weights[i] += 2
    elif strategy == 'AGGRESSIVE':
        for i in range(0, 9): weights[i] += 2
        for i in range(39, 49): weights[i] += 2
    elif strategy == 'FLOW':
        for i in range(49):
            if (i + 1) % 10 in lucky_digits: weights[i] += 3
    final_l = []
    for _ in range(300):
        temp_pool = pool[:]; temp_weights = weights[:]; draws = []
        for _ in range(6):
            pick = random.choices(temp_pool, weights=temp_weights, k=1)[0]
            draws.append(pick); idx = temp_pool.index(pick)
            temp_pool.pop(idx); temp_weights.pop(idx)
        temp_sorted = sorted(draws)
        if sum(1 for i in range(5) if temp_sorted[i+1] == temp_sorted[i]+1) > 2: continue
        if temp_sorted[-1] < 25 or temp_sorted[0] > 35: continue 
        final_l = temp_sorted
        break
    if not final_l: final_l = sorted(random.sample(pool, 6))
    l_spec = random.randint(1,49)
    while l_spec in final_l: l_spec = random.randint(1,49)
    s_main = sorted(random.sample(range(1,39),6)); s_spec = random.randint(1,8); t_nums = random.sample(range(10),3)
    return final_l, l_spec, s_main, s_spec, t_nums

# ==========================================
# 5. 介面流程
# ==========================================
st.markdown("<h2 style='text-align:center; color:#ffd700; margin:0.4rem 0;'>🎱 Tino Lucky Ball</h2>", unsafe_allow_html=True)

u_name = st.text_input("姓名", "", placeholder="請輸入您的姓名")

st.markdown("<div style='margin-bottom:5px; color:#aaa; font-size:0.9em;'>出生日期 (年/月/日) 與 時辰</div>", unsafe_allow_html=True)
c_y, c_m, c_d = st.columns([1.3, 1, 1])
with c_y:
    sel_year = st.number_input("年", 1900, 2099, 2000, 1, format="%d", label_visibility="collapsed")
with c_m:
    sel_month = st.number_input("月", 1, 12, 1, 1, format="%d", label_visibility="collapsed")
with c_d:
    sel_day = st.number_input("日", 1, 31, 1, 1, format="%d", label_visibility="collapsed")

c_h, c_dummy = st.columns([2, 1])
with c_h:
    hours_opts = [f"{h:02d}:00-{(h+1)%24:02d}:59 ({ZHI[((h+1)//2)%12]}時)" for h in range(24)]
    sel_hour_str = st.selectbox("出生時辰", hours_opts, index=12, label_visibility="collapsed")
    sel_hour = int(sel_hour_str.split(":")[0])

try:
    y, m, d = int(sel_year), int(sel_month), int(sel_day)
    last_day = calendar.monthrange(y, m)[1]
    if d > last_day: d = last_day
    u_dob = date(y, m, d)
except:
    u_dob = date(2000, 1, 1)

if st.button("SPIN (啟動演算)", type="primary", use_container_width=True):
    if not u_name.strip():
        st.error("請輸入姓名以啟動命盤運算")
    else:
        if sel_year >= 2027:
            st.toast(f"🛸 偵測到未來人訊號！歡迎親臨 Tino Lucky Ball！", icon="👽")

        placeholder = st.empty()
        placeholder.markdown("""<div class="slot-machine"><h3 style="text-align:center;color:#ffeb3b;">⚡ 正在感應天機...</h3></div>""", unsafe_allow_html=True)
        time.sleep(0.6)
        placeholder.empty()
        
        fate_data = calculate_real_fate(u_name.strip(), u_dob, sel_hour)
        element_tails_map = {"金": [4,9,0,5], "木": [3,8,1,6], "水": [1,6,4,9], "火": [2,7,3,8], "土": [0,5,2,7]}
        tails = element_tails_map.get(fate_data['main_elem'], [1,6])
        l, ls, s, ss, t = calculate_variable_numbers(tails, fate_data['strategy'])
        
        st.session_state['last_result'] = {
            'fate': fate_data, 'l': l, 'ls': ls, 's': s, 'ss': ss, 't': t,
            'name': u_name.strip(), 'time': get_taiwan_time()
        }
        st.rerun()

# ==========================================
# 6. 結果顯示 (潔淨大師版)
# ==========================================
if st.session_state.get('last_result'):
    res = st.session_state['last_result']
    f = res['fate']
    tw_now = res['time']

    weekdays = ["星期一","星期二","星期三","星期四","星期五","星期六","星期日"]
    datetime_display = f"{tw_now.strftime('%Y年%m月%d日')}　{weekdays[tw_now.weekday()]}　{tw_now.strftime('%H:%M')}"

    st.markdown(f"""<div class="today-info">演算時間：{datetime_display}</div>""", unsafe_allow_html=True)

    c_txt, c_radar = st.columns([1.6, 1])
    with c_txt:
        # 移除 bazi_html，只保留運勢內容，乾淨了然
        fate_html = f"""<div class="fate-card">
<div class="fate-header">🔮 今日運勢 ({res['name']})</div>
<div class="fate-content">
<div class="main-star-box">
    <span style="color:#00e5ff; font-weight:bold;">【命宮】</span><span class="main-star-name">{f['star_name']} . {f['star_short']}</span>
</div>
{f['star_desc']}
<br><br>
<span style="color:#00e5ff; font-weight:bold;">【五行氣場】</span><br>
先天{f['ganzhi_year']}年，屬{f['ganzhi_elem']}。今日能量與您本命五行產生共振，請順勢而為。
</div>
</div>"""

        st.markdown(fate_html, unsafe_allow_html=True)
        
    with c_radar:
        fig = go.Figure(data=go.Scatterpolar(
            r=f['r_vals'] + [f['r_vals'][0]],
            theta=f['r_labs'] + [f['r_labs'][0]],
            fill='toself', line_color='#00e5ff', fillcolor='rgba(0,229,255,0.18)',
            marker=dict(size=3)
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=False, range=[0,100]), 
                       angularaxis=dict(tickfont=dict(size=9,color='#aaa'), rotation=90, direction='clockwise'),
                       bgcolor='rgba(0,0,0,0)'),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False, margin=dict(l=5,r=5,t=20,b=5), height=200
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    l_html = "".join(f'<div class="ball">{n:02d}</div>' for n in res['l']) + f'<div class="ball special">{res["ls"]:02d}</div>'
    s_html = "".join(f'<div class="ball">{n:02d}</div>' for n in res['s']) + f'<div class="ball special">{res["ss"]:02d}</div>'
    t_html = f"{res['t'][0]}&nbsp;&nbsp;{res['t'][1]}&nbsp;&nbsp;{res['t'][2]}"
    
    st.markdown(f"""
    <div class="slot-machine">
        <div class="machine-title">TINO LUCKY BALL</div>
        <div class="reel-box"><div class="reel-label">大樂透 LOTTO</div><div class="ball-row">{l_html}</div></div>
        <div class="reel-box"><div class="reel-label" style="color:#00ff88;">威力彩 SUPER</div><div class="ball-row">{s_html}</div></div>
        <div class="reel-box"><div class="reel-label" style="color:#ffd700;">刮刮樂 SCRATCH</div><div class="scratch-text">{t_html}</div></div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="disclaimer-box">
    ⚠️ <strong>免責聲明 (Disclaimer)</strong><br>
    本程式之命理運算與號碼生成僅供 <strong>民俗學術研究</strong> 及 <strong>娛樂體驗</strong> 之用。<br>
    所有的分析結果均基於機率與統計模型，<strong>不保證任何中獎機率</strong>。<br>
    請使用者 <strong>量力而為，理性投注</strong>，切勿過度沉迷。<br>
    本程式開發者不對任何投注盈虧負任何法律責任。
</div>
""", unsafe_allow_html=True)
