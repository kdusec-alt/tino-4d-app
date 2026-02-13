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

# ✅ 強制台灣時間 (GMT+8)
def get_taiwan_time():
    return datetime.utcnow() + timedelta(hours=8)

# Session State
if 'last_result' not in st.session_state:
    st.session_state['last_result'] = None

# ==========================================
# 2. CSS 樣式表 (含底部警示)
# ==========================================
st.markdown("""
<style>
/* 全局黑金風格 */
.stApp { background: #000; color: #eee; font-family: "Microsoft JhengHei", sans-serif; }
.block-container { padding: 0.5rem 0.8rem 1rem !important; max-width: 520px !important; }

/* 標題 */
h2 { margin: 0.4rem 0 0.8rem !important; font-size: 1.6em !important; text-align: center; color: #ffd700; text-shadow: 0 0 10px #ff0000; }

/* 輸入區塊優化 */
div[data-testid="stHorizontalBlock"] { gap: 0.5rem; }
div[data-baseweb="select"] > div { 
    background-color: #111; border-color: #444; color: #eee; border-radius: 6px;
}

/* 日期時間 */
.today-info {
    text-align: center; font-size: 0.9em; color: #ffcc00; margin: 0.3rem 0 0.8rem; padding: 6px;
    background: rgba(255,204,0,0.1); border-radius: 6px; letter-spacing: 1px; border: 1px solid #332200;
}

/* 命理戰報卡 */
.fate-card { 
    background: linear-gradient(180deg, #1a0505 0%, #000 100%);
    border: 1px solid #ff4444; border-radius: 10px; padding: 12px; margin: 0.5rem 0; 
    box-shadow: 0 4px 10px rgba(255, 68, 68, 0.1);
}
.fate-header { font-size: 1.1em; color: #ffd700; margin-bottom: 8px; font-weight: bold; border-bottom: 1px solid #331111; padding-bottom: 5px;}
.fate-content { font-size: 0.9em; line-height: 1.6; color: #ddd; text-align: justify; }
.highlight { color: #00e5ff; font-weight: bold; margin-right: 3px; }

/* 主星區塊 */
.main-star-box { margin-top: 8px; padding: 8px; background: rgba(255,255,255,0.05); border-radius: 6px; }
.main-star-title { color: #aaa; font-size: 0.8em; letter-spacing: 1px;}
.main-star-name { color: #ffeb3b; font-size: 1.4em; font-weight: bold; margin: 2px 0; text-shadow: 0 0 8px #ff9900; }
.main-star-desc { color: #ffddaa; font-size: 0.95em; font-style: normal; display: block; margin-top: 4px; border-top: 1px solid #444; padding-top: 4px;}

/* 樂透區 */
.slot-machine { background: #0a0a0a; border: 2px solid #ffd700; border-radius: 12px; padding: 10px; margin-top: 15px; margin-bottom: 20px;}
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

/* 底部警示標語 */
.disclaimer-box {
    margin-top: 30px; padding-top: 15px; border-top: 1px solid #333;
    text-align: center; color: #666; font-size: 0.75em; line-height: 1.5;
}

/* 按鈕 */
div.stButton > button {
    width: 100%; height: 50px; border-radius: 25px;
    background: linear-gradient(180deg, #ff4444 0%, #cc0000 100%);
    border: 2px solid #ffd700; color: white; font-weight: bold; font-size: 1.2em;
    box-shadow: 0 4px 0 #880000; margin-top: 10px;
}
div.stButton > button:active { transform: translateY(2px); box-shadow: 0 0 0 #880000; }

@media (max-width: 480px) {
    .main-star-name { font-size: 1.3em; }
    .ball { width: 28px !important; height: 28px !important; font-size: 12px !important; }
}

#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. 核心邏輯 (完整大師版)
# ==========================================

def get_element_by_year(year):
    last = year % 10
    mapping = {0:"金",1:"金",2:"水",3:"水",4:"木",5:"木",6:"火",7:"火",8:"土",9:"土"}
    return mapping.get(last, "未知")

element_tails = {
    "金": [4,9,0,5], "木": [3,8,1,6], "水": [1,6,4,9],
    "火": [2,7,3,8], "土": [0,5,2,7]
}

def calculate_fixed_fate(name, dob):
    tw_now = get_taiwan_time()
    today_str = tw_now.strftime("%Y%m%d")
    fate_seed = int(hashlib.sha256(f"{name}{dob}{today_str}".encode('utf-8')).hexdigest(), 16)
    random.seed(fate_seed)
    
    gan = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
    zhi = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]
    ganzhi = f"{gan[(dob.year-4)%10]}{zhi[(dob.year-4)%12]}"
    
    # 大師敘事資料庫 (含隱形策略)
    stars_db = [
        ("紫微", "帝王降臨", "紫微星入局，如帝王親臨。今日氣場強大，能壓制煞氣。適合展現魄力，鎖定心中首選，勿受他人動搖。", "BALANCED"),
        ("天機", "智謀百出", "天機星化氣為善，主智慧與靈動。今日靈感將如泉湧般出現，若有突如其來的號碼靈感，請務必把握，那是宇宙的訊號。", "FLOW"),
        ("太陽", "光芒萬丈", "太陽星高照，正財運勢旺盛。今日格局光明磊落，不宜走偏門，適合大方下注，財氣將隨陽光普照。", "AGGRESSIVE"),
        ("武曲", "剛毅果決", "武曲為正財大星，金氣剛毅。今日財庫穩固，決策應果斷，不宜猶豫不決。看準目標，重注出擊。", "BALANCED"),
        ("天同", "福星高照", "天同星坐守，主福氣與享受。今日偏財運佳，適合抱著輕鬆的心態遊玩，無心插柳往往柳成蔭。", "FLOW"),
        ("廉貞", "公關之神", "廉貞星主次桃花，人脈即財脈。今日直覺敏銳，氣場帶有變化的能量，適合嘗試非傳統的組合。", "FLOW"),
        ("天府", "庫房充盈", "天府星為南斗之主，掌管天之庫房。今日運勢穩健，適合守成與佈局，避開過於極端的選擇，穩中求勝。", "CONSERVATIVE"),
        ("太陰", "財運如水", "太陰星主富，象徵財運如水般細水長流。今日晚間運勢更佳，適合參考與水有關的尾數 (1, 6)。", "FLOW"),
        ("貪狼", "慾望之主", "貪狼星化祿，為第一大偏財星。今日慾望強烈，投機運勢爆發。適合放手一搏，嘗試冷門或極端號碼。", "AGGRESSIVE"),
        ("巨門", "深思熟慮", "巨門主暗，財運隱藏於深處。今日不宜張揚，需低調行事。相信自己深思熟慮後的分析，不隨波逐流。", "CONSERVATIVE"),
        ("天相", "輔佐得力", "天相星掌印，主輔佐與平衡。今日運勢平穩，適合參考過往熱門號碼，或跟隨他人的幸運數字。", "BALANCED"),
        ("天梁", "逢凶化吉", "天梁為蔭星，主呈祥解厄。今日雖無橫財爆發之象，但有意外之福。保持平常心，幸運自然降臨。", "CONSERVATIVE"),
        ("七殺", "將軍出征", "七殺星主肅殺，成敗在於一線。今日運勢起伏大，適合單點突破，選擇一組號碼堅持到底。", "AGGRESSIVE"),
        ("破軍", "先破後立", "破軍星主變動，舊的不去新的不來。今日適合打破常規，選擇平時不會選的怪號，或許會有奇蹟。", "AGGRESSIVE")
    ]
    my_star_data = stars_db[fate_seed % 14]
    
    name_analyses = [
        "格局外圓內方，決策果斷，今日具有強大的領袖磁場。", 
        "財庫飽滿之象，直覺敏銳，適合大膽佈局，捕捉稍縱即逝的機會。", 
        "五行相生有情，貴人顯現，順勢而為即可獲得助力。", 
        "氣場強大如虹，能突破重圍，今日易有意外之喜降臨。", 
        "運勢穩紮穩打，積沙成塔，正財運勢極佳，不宜貪快。", 
        "靈光乍現之局，思緒清晰，請相信您腦中閃過的第一個數字。"
    ]
    name_res = name_analyses[fate_seed % 6]
    
    elements = ['金','木','水','火','土']
    r_vals = [random.randint(40,75) for _ in range(5)]
    elem_char = get_element_by_year(dob.year)
    if elem_char in elements:
        r_vals[elements.index(elem_char)] = 95
    
    return {
        'ganzhi': ganzhi, 
        'star_name': my_star_data[0],
        'star_short': my_star_data[1],
        'star_desc': my_star_data[2],
        'strategy': my_star_data[3],
        'name_res': name_res,
        'r_labs': elements, 'r_vals': r_vals, 'elem': elem_char
    }

# 生存協議 + 策略注入
def calculate_variable_numbers(lucky_digits, strategy):
    tw_now = get_taiwan_time()
    now_seed = int(hashlib.sha256(tw_now.strftime("%Y%m%d%H%M%S%f").encode()).hexdigest(), 16)
    random.seed(now_seed)
    
    pool = list(range(1, 50))
    weights = [1] * 49
    
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
        draws = random.choices(pool, weights=weights, k=10)
        unique_draws = list(set(draws))
        if len(unique_draws) >= 6:
            temp = sorted(unique_draws[:6])
            if sum(1 for i in range(5) if temp[i+1] == temp[i]+1) > 2: continue
            if temp[-1] < 25 or temp[0] > 35: continue 
            final_l = temp
            break
            
    if not final_l: final_l = sorted(random.sample(pool, 6))
    
    l_spec = random.randint(1,49)
    while l_spec in final_l: l_spec = random.randint(1,49)
    
    s_main = sorted(random.sample(range(1,39),6))
    s_spec = random.randint(1,8)
    t_nums = random.sample(range(10),3)
    
    return final_l, l_spec, s_main, s_spec, t_nums

# ==========================================
# 4. 介面流程 (新版日期輸入)
# ==========================================
st.markdown("<h2 style='text-align:center; color:#ffd700; margin:0.4rem 0;'>🎱 Tino Lucky Ball</h2>", unsafe_allow_html=True)

# 姓名輸入
u_name = st.text_input("姓名", "", placeholder="請輸入您的姓名")

# 日期三欄輸入
st.markdown("<div style='margin-bottom:5px; color:#aaa; font-size:0.9em;'>出生日期</div>", unsafe_allow_html=True)
c_y, c_m, c_d = st.columns([1.3, 1, 1])

with c_y:
    years = list(range(1930, 2041))
    # 預設 2000 年 (index = 2000-1930 = 70)
    sel_year = st.selectbox("年", years, index=70, label_visibility="collapsed")
with c_m:
    sel_month = st.selectbox("月", list(range(1, 13)), label_visibility="collapsed")
with c_d:
    sel_day = st.selectbox("日", list(range(1, 32)), label_visibility="collapsed")

# 組合日期並防呆
try:
    u_dob = date(sel_year, sel_month, sel_day)
except ValueError:
    # 處理 2/30 這種無效日期，自動修正為該月最後一天
    last_day = calendar.monthrange(sel_year, sel_month)[1]
    u_dob = date(sel_year, sel_month, last_day)

if st.button("SPIN (啟動演算)", type="primary", use_container_width=True):
    if not u_name.strip():
        st.error("請輸入姓名以啟動命盤運算")
    else:
        # 🛸 未來人彩蛋
        if sel_year >= 2027:
            st.toast(f"🛸 偵測到來自 {sel_year} 年的未來訊號！歡迎親臨 Tino Lucky Ball！", icon="👽")

        # 動畫
        placeholder = st.empty()
        placeholder.markdown("""<div class="slot-machine"><h3 style="text-align:center;color:#ffeb3b;">⚡ 天機演算中...</h3></div>""", unsafe_allow_html=True)
        time.sleep(0.5)
        placeholder.empty()
        
        # 演算
        fate_data = calculate_fixed_fate(u_name.strip(), u_dob)
        tails = element_tails.get(fate_data['elem'], [1,6])
        l, ls, s, ss, t = calculate_variable_numbers(tails, fate_data['strategy'])
        
        st.session_state['last_result'] = {
            'fate': fate_data, 'l': l, 'ls': ls, 's': s, 'ss': ss, 't': t,
            'name': u_name.strip(), 'time': get_taiwan_time()
        }
        st.rerun()

# ==========================================
# 5. 結果顯示
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
        st.markdown(f"""
        <div class="fate-card">
            <div class="fate-header">🔮 今日運勢 ({res['name']})</div>
            <div class="fate-content">
                <span class="highlight">【先天】</span> {f['ganzhi']}年 屬{f['elem']}<br>
                <div class="main-star-box">
                    <span class="main-star-title">今日命宮主星</span><br>
                    <div class="main-star-name">{f['star_name']} . {f['star_short']}</div>
                    <span class="main-star-desc">{f['star_desc']}</span>
                </div>
                <div style="margin-top:6px;">
                    <span class="highlight">【靈動】</span>{f['name_res']}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
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
            showlegend=False, margin=dict(l=5,r=5,t=20,b=5), height=180
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # 樂透機台
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

# ==========================================
# 6. 底部警示標語 (Safe Harbor)
# ==========================================
st.markdown("""
<div class="disclaimer-box">
    ⚠️ <strong>免責聲明 (Disclaimer)</strong><br>
    本程式之命理運算與號碼生成僅供 <strong>民俗學術研究</strong> 及 <strong>娛樂體驗</strong> 之用。<br>
    所有的分析結果均基於機率與統計模型，<strong>不保證任何中獎機率</strong>。<br>
    請使用者 <strong>量力而為，理性投注</strong>，切勿過度沉迷。<br>
    本程式開發者不對任何投注盈虧負任何法律責任。
</div>
""", unsafe_allow_html=True)
