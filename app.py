import os
import json
from abc import ABC, abstractmethod
from flask import Flask, jsonify, request, render_template_string

# ---------------------------------------------------------
# 1. 사용자 정의 예외 처리
# ---------------------------------------------------------
class InsufficientCoinError(Exception):
    def __init__(self, message="코인이 부족하여 정책을 실행할 수 없습니다."):
        super().__init__(message)

# ---------------------------------------------------------
# 2. 객체지향 클래스 정의
# ---------------------------------------------------------
class Player:
    def __init__(self):
        self._pop = 5000
        self._trust = 70
        self._env = 60
        self._coins = 20

    @property
    def pop(self): return self._pop
    @pop.setter
    def pop(self, val): self._pop = max(0, min(5000, val))

    @property
    def trust(self): return self._trust
    @trust.setter
    def trust(self, val): self._trust = max(0, min(100, val))

    @property
    def env(self): return self._env
    @env.setter
    def env(self, val): self._env = max(0, min(100, val))

    def add_coins(self, amount): self._coins += amount

    def spend_coins(self, amount):
        if self._coins < amount:
            raise InsufficientCoinError()
        self._coins -= amount

    def __str__(self): return f"인구:{self.pop} 신뢰도:{self.trust} 환경지수:{self.env}"
    def __int__(self): return self._coins


class Policy:
    def __init__(self, name, cost, pop_effect, trust_effect, env_effect, desc):
        self.name = name
        self.cost = cost
        self.pop_effect = pop_effect
        self.trust_effect = trust_effect
        self.env_effect = env_effect
        self.desc = desc


class Disaster(ABC):
    def __init__(self, name, base_pop, base_trust, base_env, bg_img):
        self.name = name
        self.base_pop = base_pop
        self.base_trust = base_trust
        self.base_env = base_env
        self.bg_img = bg_img
        self.policies = []

    def add_policy(self, policy):
        self.policies.append(policy)

    def get_multiplier(self, env_score):
        if env_score >= 45: return 1
        elif 25 <= env_score <= 44: return 2
        else: return 3

    @abstractmethod
    def get_disaster_report(self): pass


class Heatwave(Disaster):
    def __init__(self):
        super().__init__("폭염", 100, 3, 3, "폭염.png")
        self.add_policy(Policy("폭염 쉼터와 냉방 지원 확대", 3, 100, 3, -4, "폭염 쉼터 확대로 시민을 보호했으나 전력 과소비로 환경지수가 하락함."))
        self.add_policy(Policy("야외 노동 전면 중단", 2, 150, -6, 0, "야외 노동 중단으로 생명을 구했으나 경제 활동 위축으로 신뢰도가 하락함."))
        self.add_policy(Policy("친환경 냉방 인프라 투자", 5, 40, -2, 6, "친환경 냉방 투자로 환경을 개선했으나 즉각적 구호가 부족했음."))
    def get_disaster_report(self): return "폭염 대책 보고서"

class Typhoon(Disaster):
    def __init__(self):
        super().__init__("태풍", 160, 5, 4, "태풍.png")
        self.add_policy(Policy("외출 금지", 3, 180, 3, 0, "외출 금지로 생명을 구하고 신뢰가 상승함."))
        self.add_policy(Policy("방재 예산 투입", 5, 140, -3, 6, "방재 예산 투입으로 환경 피해를 줄였으나 예산 논란이 일었음."))
        self.add_policy(Policy("일회용 구호물품 배포", 4, 200, 6, -8, "구호물품 배포로 생존율은 올랐으나 쓰레기 증가로 환경지수가 악화됨."))
        self.add_policy(Policy("자율대피 권고", 0, 0, -2, 0, "자율대피만 권고하여 특별한 방어 없이 피해를 고스란히 받음."))
    def get_disaster_report(self): return "태풍 대책 보고서"

class HeavyRain(Disaster):
    def __init__(self):
        super().__init__("폭우/침수", 200, 6, 5, "폭우.png") 
        self.add_policy(Policy("저지대 대피", 3, 220, -2, 0, "선제 대피로 인명피해를 막았으나 강제 이주 불만이 발생함."))
        self.add_policy(Policy("임시 배수로 건설", 5, 180, 3, -6, "배수로로 침수를 막았으나 자연 훼손으로 환경지수가 감소함."))
        self.add_policy(Policy("자연배수 유도", 5, -120, -5, 10, "자연배수를 유도하여 환경지수는 지켰으나 희생자가 발생함."))
    def get_disaster_report(self): return "폭우 및 침수 보고서"

class LivestockCrisis(Disaster):
    def __init__(self):
        super().__init__("가축위기", 220, 8, 3, "가축 위기.png")
        self.add_policy(Policy("식량 배급", 6, 260, 8, -2, "식량 배급으로 민심을 다독임."))
        self.add_policy(Policy("대체식량 연구/생산", 7, 60, -5, 12, "미래 식량 연구로 환경을 개선했으나 당장의 식량난으로 불만이 커짐."))
        self.add_policy(Policy("감염 가축 소각", 3, 0, -6, -10, "감염 가축을 전면 소각하여 팬데믹의 연결 고리를 끊어냄."))
    def get_disaster_report(self): return "가축 위기 대책 보고서"

class Pandemic(Disaster):
    def __init__(self):
        super().__init__("전염병", 300, 10, 2, "팬데믹.png")
        self.add_policy(Policy("감염지역 봉쇄", 5, 320, -12, 0, "강력한 봉쇄로 생명은 구했지만 신뢰가 폭락함."))
        self.add_policy(Policy("원격근무/디지털 전환", 6, 200, -4, 10, "디지털 전환으로 탄소배출이 감소했으나 현장의 반발을 삼."))
        self.add_policy(Policy("방역 물질 살포", 6, 260, 5, -8, "대규모 화학 방역으로 바이러스를 잡았지만 생태계가 파괴됨."))
    def get_disaster_report(self): return "팬데믹 방역 보고서"


class NewsSystem:
    def __init__(self, filename):
        self.news_data = {}
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                self.news_data = json.load(f)

    def __len__(self): return sum(len(articles) for articles in self.news_data.values())
    def get_news_for_disaster(self, disaster_name): return self.news_data.get(disaster_name, [])


class GameManager:
    def __init__(self):
        self.player = Player()
        self.turn = 1
        self.disasters = [Heatwave(), Typhoon(), HeavyRain(), LivestockCrisis(), Pandemic()]
        self.news_system = NewsSystem('news_data.json')
        self.skip_pandemic = False
        self.state = "MAIN"
        
        self.pending_diff = {'pop': 0, 'trust': 0, 'env': 0}
        self.report_descs = []
        self.full_log = [] 
        
        self.last_report = {}
        self.ending_image = ""
        self.ending_title = ""

    def __call__(self, action_type, policy_idx=None):
        if self.state != "MAIN": return
        current_disaster = self.disasters[(self.turn - 1) // 2]
        policy = None
        if action_type == 'POLICY' and policy_idx is not None:
            policy = current_disaster.policies[policy_idx]
            self.player.spend_coins(policy.cost)
            if policy.name == "감염 가축 소각": self.skip_pandemic = True
        self._process_turn(current_disaster, policy)

    def _process_turn(self, current_disaster, policy):
        mult = current_disaster.get_multiplier(self.player.env)
        pop_change = -(current_disaster.base_pop * mult)
        trust_change = -(current_disaster.base_trust * mult)
        env_change = -(current_disaster.base_env * mult)
        
        turn_desc = f"▶ [Turn {self.turn} - {current_disaster.name}] (환경 배율 x{mult})\n"
        if policy:
            pop_change += policy.pop_effect
            trust_change += policy.trust_effect
            env_change += policy.env_effect
            turn_desc += f"  - 시행 정책: {policy.name}\n  - 결과: {policy.desc}"
        else:
            turn_desc += "  - 정책 미시행 (SKIP): 어떠한 방어 대책도 내놓지 않았습니다."

        self.pending_diff['pop'] += pop_change
        self.pending_diff['trust'] += trust_change
        self.pending_diff['env'] += env_change
        self.report_descs.append(turn_desc)
        self.full_log.append(turn_desc)

        if self.turn % 2 != 0:
            self.turn += 1
            self.player.add_coins(4)
        else:
            self.player.pop += self.pending_diff['pop']
            self.player.trust += self.pending_diff['trust']
            self.player.env += self.pending_diff['env']

            if self.player.pop <= 0 or self.player.trust <= 0 or self.player.env <= 0:
                self._set_ending("게임 오버 엔딩.png", "모든 것이 무너졌습니다.")
                return

            self.last_report = {
                "title": current_disaster.get_disaster_report(),
                "desc": "\n\n".join(self.report_descs),
                "stats": {"pop": self.player.pop, "trust": self.player.trust, "env": self.player.env},
                "diff": self.pending_diff.copy()
            }
            self.state = "REPORT"

    def _calculate_final_ending(self):
        bonus = (int(self.player) // 10) * 5
        self.player.trust += bonus
        pop, trust, env = self.player.pop, self.player.trust, self.player.env
        
        if pop <= 1200: self._set_ending("국가 붕괴 엔딩.png", "국가의 기능이 완전히 무너졌습니다.")
        elif env <= 15: self._set_ending("환경 붕괴 엔딩.png", "자연의 경고를 무시한 대가는 참혹했습니다.")
        elif trust < 20 and env >= 35: self._set_ending("독재 국가 엔딩.png", "자유를 희생하여 환경을 지켜냈습니다.")
        elif pop >= 3800 and trust >= 65 and env >= 70: self._set_ending("지속가능 국가 엔딩.png", "당신의 선택이 더 나은 미래를 만들었습니다.")
        elif pop >= 2800 and env >= 35: self._set_ending("생존 국가 엔딩.png", "수많은 위기 속에서도 국가를 지켜냈습니다.")
        else: self._set_ending("게임 오버 엔딩.png", "미래를 바꾸지 못했습니다.")

    def _set_ending(self, img, title):
        self.state = "ENDING"
        self.ending_image = img
        self.ending_title = title

    def get_frontend_state(self):
        current_idx = min((self.turn - 1) // 2, 4)
        current_disaster = self.disasters[current_idx]
        face = "😀" if self.player.trust >= 70 else "😐" if self.player.trust >= 31 else "😡"
        
        # 1. 아카이브 뉴스 (1턴부터 현재 진행중인 턴까지의 모든 재난 뉴스 누적)
        archive_news = []
        for i in range(current_idx + 1):
            archive_news.extend(self.news_system.get_news_for_disaster(self.disasters[i].name))
            
        # 2. 현재 뉴스 (마키 효과에 띄울 속보)
        current_news = self.news_system.get_news_for_disaster(current_disaster.name)

        return {
            "turn": self.turn,
            "state": self.state,
            "pop": self.player.pop,
            "trust": self.player.trust,
            "env": self.player.env,
            "coins": int(self.player),
            "face": face,
            "bg_img": current_disaster.bg_img,
            "policies": [{"name": p.name, "cost": p.cost} for p in current_disaster.policies],
            "current_news": current_news,
            "archive_news": archive_news,
            "report": self.last_report,
            "ending_img": self.ending_image,
            "ending_title": self.ending_title,
            "full_summary": "\n\n".join(self.full_log)
        }


# ---------------------------------------------------------
# 3. Flask 웹 서버 및 HTML UI
# ---------------------------------------------------------
app = Flask(__name__, static_folder='.', static_url_path='/assets')
game = GameManager()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>기후 시뮬레이터</title>
    <style>
        @import url('https://cdn.jsdelivr.net/gh/neodgm/neodgm-webfont@1.530/neodgm/style.css');
        body { margin: 0; background: #111; display: flex; justify-content: center; align-items: center; height: 100vh; font-family: 'NeoDunggeunmo', sans-serif; user-select: none; }
        .game-screen { width: 1280px; height: 720px; position: relative; overflow: hidden; background: #000; box-shadow: 0 0 30px rgba(0,0,0,1); border: 2px solid #333; }
        .bg-image { width: 100%; height: 100%; position: absolute; top: 0; left: 0; object-fit: cover; z-index: 1; transition: opacity 0.5s; }
        
        /* 1. 뉴스 마키 (속보) - 화면 최상단 */
        .marquee-bar { position: absolute; top: 0; left: 0; width: 100%; height: 45px; background: rgba(192, 57, 43, 0.95); color: #fff; display: flex; align-items: center; overflow: hidden; z-index: 100; border-bottom: 2px solid #fff; }
        .marquee-content { display: inline-block; white-space: nowrap; padding-left: 100%; animation: marquee 25s linear infinite; font-size: 24px; font-weight: bold; letter-spacing: 1px; text-shadow: 1px 1px 0 #000; }
        @keyframes marquee { 0% { transform: translateX(0); } 100% { transform: translateX(-100%); } }

        /* HUD UI (마키 바 때문에 top 위치를 45px 이상으로 내림) */
        .stat-panel { position: absolute; top: 45px; left: 0; background: rgba(30, 30, 30, 0.85); width: 220px; padding: 20px; z-index: 10; display: flex; flex-direction: column; gap: 20px; border-bottom-right-radius: 15px; border-right: 2px solid #555; border-bottom: 2px solid #555; }
        .stat-row { display: flex; align-items: center; gap: 20px; color: white; font-size: 26px; }
        .coin-panel { position: absolute; top: 65px; right: 20px; background: rgba(80, 80, 80, 0.8); border-radius: 30px; padding: 10px 30px; display: flex; align-items: center; gap: 15px; z-index: 10; color: #ffd700; font-size: 28px; border: 2px solid #ffd700; }
        
        /* 뉴스 아이콘 및 아카이브(과거 뉴스) */
        .news-center { position: absolute; top: 65px; left: 50%; transform: translateX(-50%); z-index: 20; display: flex; flex-direction: column; align-items: center; }
        .news-icon { font-size: 55px; cursor: pointer; text-shadow: 3px 3px 0px rgba(0,0,0,0.8); transition: transform 0.2s; }
        .news-icon:hover { transform: scale(1.1); }
        .news-dropdown { margin-top: 15px; background: rgba(40,40,40,0.95); width: 500px; color: white; position: relative; display: none; border: 3px solid #f39c12; border-radius: 10px; max-height: 400px; overflow-y: auto; }
        .news-item { padding: 20px; border-bottom: 1px solid #555; }
        .news-title { font-size: 20px; font-weight: bold; color: #f39c12; margin-bottom: 10px; }
        .news-body { font-size: 16px; color: #ccc; line-height: 1.4; }
        
        /* 하단 컨트롤 */
        .turn-display { position: absolute; bottom: 20px; left: 20px; color: #fff; font-size: 32px; z-index: 10; text-shadow: 2px 2px 0px #000; background: rgba(231, 76, 60, 0.8); padding: 5px 20px; border-radius: 5px; }
        .skip-btn { position: absolute; bottom: 30px; right: 30px; background: #3498db; color: white; padding: 15px 40px; font-size: 26px; border-radius: 10px; border: 3px solid #2980b9; cursor: pointer; z-index: 25; font-family: inherit; transition: 0.2s; }
        .skip-btn:hover { background: #2980b9; }
        .office-icon { position: absolute; top: 50%; right: 40px; font-size: 60px; cursor: pointer; z-index: 10; text-shadow: 3px 3px 0px rgba(0,0,0,0.8); transition: 0.2s; }
        
        /* 정책 제안서 박스 정렬 */
        .policy-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); display: none; flex-direction: column; justify-content: center; align-items: center; z-index: 30; }
        .policy-paper-container { position: relative; width: 550px; height: 750px; }
        .policy-bg { width: 100%; height: 100%; object-fit: fill; }
        
        .policy-slot { position: absolute; left: 12%; width: 76%; height: 11%; display: flex; align-items: center; justify-content: center; font-size: 18px; font-weight: bold; color: #333; cursor: pointer; z-index: 32; box-sizing: border-box; text-align: center; padding: 0 10px; word-break: keep-all; }
        .policy-slot:hover { background: rgba(0,0,0,0.05); border-radius: 8px; }
        .slot-0 { top: 30%; }
        .slot-1 { top: 46%; }
        .slot-2 { top: 62.5%; }
        .slot-3 { top: 78.5%; }

        /* 승인도 이미지 */
        .stamp { position: absolute; width: 90px; right: 8%; z-index: 35; display: none; transform: rotate(-15deg); }

        /* 결과/요약 화면 */
        .report-screen { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.95); z-index: 40; display: none; flex-direction: column; justify-content: center; align-items: center; color: white; }
        .summary-popup { position: absolute; top: 5%; left: 10%; width: 80%; height: 85%; background: #000; border: 4px solid #fff; z-index: 100; color: white; padding: 40px; overflow-y: auto; display: none; }
        
        /* 엔딩 화면 버튼 레이아웃 */
        .ending-btn-group { position: absolute; bottom: 80px; display: flex; gap: 40px; z-index: 61; }
        .end-btn { background: #34495e; color: white; padding: 15px 40px; font-size: 26px; border-radius: 10px; border: 3px solid #fff; cursor: pointer; font-family: inherit; }
        
        .alert-toast { position: absolute; top: 45px; right: 250px; background: #e74c3c; color: white; padding: 15px 30px; border-radius: 5px; font-size: 20px; z-index: 100; display: none; border: 2px solid #fff; }
        .manual-popup { position: absolute; top: 10%; left: 15%; width: 70%; height: 80%; background: rgba(20,20,20,0.95); border: 4px solid #fff; z-index: 100; color: white; padding: 40px; overflow-y: auto; display: none; border-radius: 15px; }
    </style>
</head>
<body>
    <div class="game-screen">
        <div class="manual-popup" id="manual-popup">
            <h1 style="text-align:center; color:#f1c40f; font-size: 40px; margin-top:0;">게임 설명서</h1>
            <div style="font-size: 22px; line-height: 1.8;">
                <p>당신은 대통령이 되어 10턴의 재난을 막아야 합니다.</p>
                <p>매 턴 재난 페널티가 적용되며, 2턴마다 보고서에서 일괄 정산됩니다.</p>
                <p>가축 위기에서 소각 정책 선택 시 팬데믹을 피할 수 있습니다.</p>
            </div>
            <button class="skip-btn" style="position: static; display: block; margin: 40px auto 0;" onclick="document.getElementById('manual-popup').style.display='none'">닫기</button>
        </div>

        <div class="summary-popup" id="summary-popup">
            <h1 style="text-align:center; color:#f1c40f; font-size: 40px;">국정 운영 총괄 보고서</h1>
            <p id="summary-content" style="font-size: 20px; line-height: 1.6; white-space: pre-wrap; background: #222; padding: 20px; border-radius: 10px;"></p>
            <button class="skip-btn" style="position: static; display: block; margin: 30px auto 0;" onclick="document.getElementById('summary-popup').style.display='none'">닫기</button>
        </div>

        <div id="title-screen" style="position: absolute; width: 100%; height: 100%; z-index: 50; display: flex; flex-direction: column; justify-content: center; align-items: center;">
            <img src="/assets/타이틀 화면.png" class="bg-image" onerror="this.style.display='none'">
            <div style="display: flex; flex-direction: column; gap: 20px; margin-top: 350px; z-index: 51;">
                <button onclick="startGame()" style="padding: 15px 50px; font-size: 30px; background: #d35400; color: white; border: 4px solid #fff; border-radius: 10px; cursor: pointer; font-family: inherit;">게임 시작</button>
                <button onclick="document.getElementById('manual-popup').style.display='block'" style="padding: 15px 50px; font-size: 30px; background: #2c3e50; color: white; border: 4px solid #fff; border-radius: 10px; cursor: pointer; font-family: inherit;">게임 설명</button>
            </div>
        </div>

        <img id="main-bg" class="bg-image" src="" onerror="this.src=''">
        
        <div id="hud-layer" style="display: none;">
            <div class="marquee-bar">
                <div class="marquee-content" id="marquee-text"></div>
            </div>

            <div class="stat-panel">
                <div class="stat-row">🧑🏻 <span id="val-pop">5000</span>명</div>
                <div class="stat-row"><span id="val-face">😀</span> <span id="val-trust">70</span>%</div>
                <div class="stat-row">🌳 <span id="val-env">60</span></div>
            </div>
            <div class="coin-panel">🪙 <span id="val-coin">20</span></div>
            <div class="news-center">
                <div class="news-icon" onclick="toggleNews()">📢</div>
                <div class="news-dropdown" id="news-box"></div>
            </div>
            <div class="turn-display">🚩 Turn <span id="val-turn">1</span></div>
            <button class="skip-btn" onclick="takeAction('SKIP')">Skip Turn</button>
            <div class="office-icon" id="office-btn" onclick="openOffice()">📜✒️</div>
        </div>

        <div id="office-click-layer" style="display: none; position: absolute; width:100%; height:100%; z-index: 15; pointer-events: none;">
            <div onclick="openPolicy()" style="position: absolute; top: 400px; left: 400px; width: 300px; height: 150px; cursor: pointer; pointer-events: auto;"></div>
            <div onclick="closeOffice()" style="position: absolute; top: 100px; right: 50px; width: 150px; height: 350px; cursor: pointer; pointer-events: auto;"></div>
        </div>

        <div class="policy-overlay" id="policy-overlay">
            <div class="policy-paper-container">
                <img src="/assets/정책 제안서.png" class="policy-bg" onerror="this.src=''">
                <div id="policy-list"></div>
                <img src="/assets/승인도.png" class="stamp" id="stamp-img" onerror="this.src=''">
            </div>
            <div style="position: absolute; top: 30px; right: 40px; color: white; font-size: 50px; cursor: pointer;" onclick="document.getElementById('policy-overlay').style.display='none'">✖</div>
            <button class="skip-btn" style="position: absolute; bottom: 40px; right: 40px; background: #e74c3c; border-color: #c0392b; z-index: 40;" onclick="document.getElementById('policy-overlay').style.display='none'">뒤로 가기</button>
        </div>

        <div class="report-screen" id="report-screen">
            <h1 style="font-size: 55px; margin-bottom: 30px; color: #f1c40f;" id="rep-title">대책 보고서</h1>
            <div style="display: flex; gap: 50px; font-size: 28px; margin-bottom: 30px; background: rgba(255,255,255,0.1); padding: 20px 40px; border-radius: 15px;">
                <div>🧑🏻 <span id="rep-pop"></span>명 (<span id="diff-pop"></span>)</div>
                <div><span id="rep-face"></span> <span id="rep-trust"></span>% (<span id="diff-trust"></span>)</div>
                <div>🌳 <span id="rep-env"></span> (<span id="diff-env"></span>)</div>
            </div>
            <p style="font-size: 22px; text-align: left; width: 800px; line-height: 1.6; padding: 20px; background: rgba(0,0,0,0.5); border-radius: 10px; white-space: pre-wrap;" id="rep-desc"></p>
            <button class="skip-btn" style="position: relative; right: 0; bottom: 0; margin-top: 30px;" onclick="nextPhase()">다음 턴으로</button>
        </div>

        <div id="ending-screen" style="position: absolute; width: 100%; height: 100%; z-index: 60; display: none; flex-direction: column; justify-content: center; align-items: center; background: #000;">
            <img id="end-bg" class="bg-image" src="" onerror="this.src=''">
            <div class="ending-btn-group">
                <button class="end-btn" style="background: #27ae60;" onclick="location.reload()">다시하기</button>
                <button class="end-btn" style="background: #f1c40f; color: #000;" onclick="showSummary()">요약</button>
            </div>
        </div>
        
        <div class="alert-toast" id="alert-toast"></div>
    </div>

    <script>
        let currentSummary = "";

        async function fetchState() {
            const res = await fetch('/api/state');
            const data = await res.json();
            updateUI(data);
        }

        function startGame() {
            document.getElementById('title-screen').style.display = 'none';
            document.getElementById('hud-layer').style.display = 'block';
            fetchState();
        }

        function showSummary() {
            document.getElementById('summary-content').innerText = currentSummary;
            document.getElementById('summary-popup').style.display = 'block';
        }

        function updateUI(data) {
            if (data.state === 'ENDING') {
                document.getElementById('ending-screen').style.display = 'flex';
                document.getElementById('end-bg').src = '/assets/' + data.ending_img;
                currentSummary = data.full_summary;
                return;
            }
            document.getElementById('val-turn').innerText = data.turn;
            document.getElementById('val-pop').innerText = data.pop;
            document.getElementById('val-trust').innerText = data.trust;
            document.getElementById('val-env').innerText = data.env;
            document.getElementById('val-coin').innerText = data.coins;
            document.getElementById('val-face').innerText = data.face;

            if (data.state === 'MAIN') {
                document.getElementById('main-bg').src = '/assets/' + data.bg_img;
                document.getElementById('report-screen').style.display = 'none';
                document.getElementById('office-click-layer').style.display = 'none';
                document.getElementById('office-btn').style.display = 'block';
                
                // 1. 최신 뉴스 속보 (마키) 반영
                if(data.current_news && data.current_news.length > 0) {
                    document.getElementById('marquee-text').innerText = "[긴급 속보] " + data.current_news[0].title + " - " + data.current_news[0].body;
                } else {
                    document.getElementById('marquee-text').innerText = "평화로운 하루입니다.";
                }

                // 2. 과거 뉴스 아카이브 (최신순 정렬)
                document.getElementById('news-box').innerHTML = data.archive_news.reverse().map(n => `
                    <div class="news-item">
                        <div class="news-title">${n.title}</div>
                        <div class="news-body">${n.body} <br><small style="color:#aaa;">- ${n.source}</small></div>
                    </div>
                `).join('');

                document.getElementById('policy-list').innerHTML = data.policies.map((p, idx) => `
                    <div class="policy-slot slot-${idx}" onclick="choosePolicy(${idx})">${idx + 1}. ${p.name} (${p.cost}🪙)</div>`).join('');
            } else if (data.state === 'REPORT') {
                const r = data.report;
                document.getElementById('rep-title').innerText = r.title;
                document.getElementById('rep-pop').innerText = r.stats.pop;
                document.getElementById('rep-trust').innerText = r.stats.trust;
                document.getElementById('rep-env').innerText = r.stats.env;
                document.getElementById('diff-pop').innerText = (r.diff.pop > 0 ? '+' : '') + r.diff.pop;
                document.getElementById('diff-trust').innerText = (r.diff.trust > 0 ? '+' : '') + r.diff.trust;
                document.getElementById('diff-env').innerText = (r.diff.env > 0 ? '+' : '') + r.diff.env;
                document.getElementById('rep-face').innerText = data.face;
                document.getElementById('rep-desc').innerText = r.desc;
                document.getElementById('report-screen').style.display = 'flex';
            }
        }

        async function takeAction(type, idx=null) {
            const res = await fetch('/api/action', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({type, idx})});
            const data = await res.json();
            if (data.status === 'error') {
                const toast = document.getElementById('alert-toast');
                toast.innerText = data.message; toast.style.display = 'block'; setTimeout(() => toast.style.display='none', 2000);
            } else fetchState();
        }

        async function choosePolicy(idx) {
            const stamp = document.getElementById('stamp-img');
            stamp.style.top = ['29.5%', '45.5%', '62%', '78%'][idx]; stamp.style.display = 'block';
            setTimeout(() => takeAction('POLICY', idx), 600);
        }

        function openOffice() { document.getElementById('main-bg').src = '/assets/집무실.png'; document.getElementById('office-click-layer').style.display = 'block'; document.getElementById('office-btn').style.display = 'none'; }
        function closeOffice() { fetchState(); }
        function openPolicy() { document.getElementById('policy-overlay').style.display = 'flex'; }
        function toggleNews() { const b = document.getElementById('news-box'); b.style.display = b.style.display === 'block' ? 'none' : 'block'; }
        async function nextPhase() { await fetch('/api/next_phase', {method: 'POST'}); fetchState(); }
    </script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(HTML_TEMPLATE)

@app.route('/api/state')
def get_state(): return jsonify(game.get_frontend_state())

@app.route('/api/action', methods=['POST'])
def handle_action():
    data = request.json
    try:
        game(data['type'], data.get('idx'))
        return jsonify({"status": "success"})
    except InsufficientCoinError as e: return jsonify({"status": "error", "message": str(e)})
    except Exception as e: return jsonify({"status": "error", "message": str(e)})

@app.route('/api/next_phase', methods=['POST'])
def next_phase():
    if game.state == "REPORT":
        if (game.turn == 8 and game.skip_pandemic) or game.turn == 10: game._calculate_final_ending()
        else:
            game.turn += 1; game.player.add_coins(4)
            game.pending_diff = {'pop': 0, 'trust': 0, 'env': 0}; game.report_descs = []; game.state = "MAIN"
    return jsonify({"status": "success"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
