# 빅테크를 누르는 건 관세가 아니라 할인율이다

> **[실험 ④] enriched.db + 웹서치 · CEO 피드백 후**
> 적용 프레임: [기대치 역산형] [자본 사이클형] [병목 인프라형]
> 전개 패턴: A (컨센서스 반박형)

**핵심 주장:** 시장은 관세가 빅테크 실적을 직접 때린다고 두려워하지만, 진짜 전달 경로는 다른 데 있다. 관세 → 수입물가 → 기대인플레 재점화 → Fed 인하 지연 → 할인율 상승. 나스닥이 맞고 있는 건 실적이 아니라 멀티플이다.

---

"관세가 빅테크 공급망을 흔든다." "AAPL의 중국 의존이 위험하다." "NVDA 수출 규제가 실적을 깎는다." 관세 뉴스가 나올 때마다 반복되는 내러티브다. 틀린 말은 아니다. 그런데 이 프레임은 지금 시장이 왜 이렇게 움직이는지 절반밖에 설명하지 못한다.

MSFT, GOOGL, META — 이 셋의 매출은 소프트웨어, 클라우드, 디지털 광고다. 물리적 재화를 수출입하는 비중은 미미하다. 그런데 왜 같이 빠지는가. 관세가 실적을 직접 때려서가 아니다. **관세가 할인율을 때리기 때문이다.**

---

경로를 따라가 보자.

관세가 수입물가를 밀어올린다. 2025년 수입물가는 거의 10% 올랐고, 기업들이 관세 이전에 쌓아둔 재고 버퍼가 소진되면서 2026년부터 본격적으로 소비자에게 전가되고 있다. 2025년 중반까지 소비자가 부담한 관세 비용은 전체의 22%였지만, 지금은 67%까지 올라왔다([EBC](https://www.ebc.com/forex/how-are-tariffs-affecting-inflation-and-stock-markets-in-2026)). 가구당 연간 $570~600의 숨은 세금이다.

이게 기대인플레를 자극한다. 소비자 1년 기대인플레이션은 2월 3.0%에서 3월 3.4%로 뛰었고, 휘발유 가격 상승 기대는 9.4%까지 치솟았다([Trading Economics](https://tradingeconomics.com/united-states/inflation-expectations)). 핵심 PCE는 연율 3.0%로, Fed 목표 2%를 한참 웃돈다. 서비스 PMI 물가지수는 70.7%까지 올라 2022년 10월 이후 최고치를 찍었다([FinancialContent](https://markets.financialcontent.com/stocks/article/marketminute-2026-4-7-the-feds-2027-pivot-why-sticky-inflation-and-an-energy-shock-have-pushed-rate-cuts-over-the-horizon)).

여기에 WTI 유가가 $100에 근접하면서 에너지 충격이 겹쳤다. 시카고 연은 Goolsbee 총재는 인플레 전망을 "orange에서 red로" 이동 중이라고 표현했고, 클리블랜드 연은 Hammack 총재는 인플레가 지속되면 **금리 인상**까지 고려할 수 있다는 입장을 냈다. Goldman Sachs는 3월 중순 2026년 인하 전망을 3회에서 2회로 줄였고, CME FedWatch는 이제 금리 인하를 **2027년 하반기**까지 밀어내고 있다.

여기서 핵심이 나온다. 할인율이 올라가면 가장 먼저, 가장 크게 맞는 자산이 뭔가. **먼 미래의 이익에 높은 멀티플을 주고 있는 장기 duration 자산** — 성장주, 빅테크다. PER 30x짜리 기업의 현재가치는 할인율 50bp 변화에 10% 이상 흔들린다. PER 10x짜리 가치주는 같은 변화에 3~4%다. 이게 나스닥이 다우보다 더 빠지고, 금융주가 빅테크를 이기는 구조적 이유다.

---

raw DB의 금리 데이터가 이걸 숫자로 확인해준다.

US 10년물(DGS10)은 3월 10일 4.15%에서 3월 27일 4.44%까지, 3주 만에 29bp 올랐다. 4월 3일 3월 고용 서프라이즈(178,000명, 예상 60,000명의 3배)가 나오자 장중 4.37%까지 치솟았다([FinancialContent](https://www.financialcontent.com/article/marketminute-2026-4-6-yield-shock-10-year-treasury-hits-435-as-march-jobs-surprise-redefines-the-feds-path)). 같은 기간 빅테크 주가를 보자 — META $592.92→$525.72(-11.3%), TSLA $383.03→$361.83(-5.5%), NVDA $175.20→$167.52(-4.4%). 10년물이 오를 때 빅테크가 빠지고, 4월 초 4.31%로 살짝 내려오자 AAPL과 GOOGL이 반등을 시작했다.

우연이 아니다. 금리와 멀티플은 같은 동전의 양면이다.

---

그런데 모든 빅테크가 같은 강도로 맞지는 않는다. 여기서 종목별 차이가 갈린다.

enriched DB의 macro_sensitivity를 보면, interest_rate에 HIGH 노출로 분류된 건 TSLA 하나뿐이다. 나머지는 대부분 LOW. 하지만 이건 **운영적 금리 민감도** — 차입 비용, 오토론 같은 것만 반영한다. 진짜 중요한 건 **밸류에이션 금리 민감도**, 즉 PER이 얼마나 높은 위치에 있느냐다.

PER 밴드 포지션으로 재정렬하면 그림이 완전히 달라진다.

**할인율에 가장 취약한 그룹:**

TSLA — 5년 PER 밴드 95번째 백분위, PER 332x. 여기에 오토론 금리까지 직접 물린다. 고용 서프라이즈 날 5.5% 빠진 이유가 있다. 관세 이전에 이미 설명 불가능한 가격이다.

AAPL — 밴드 72%, PBR 43.5x 역사적 최고. 여기에 중국 하드웨어 생산이라는 관세 직격탄이 겹친다. 할인율에도 맞고, 공급망에도 맞는 이중 노출.

COST(85%), AVGO(80%) — 퀄리티 기업이지만 밸류에이션이 높은 자리에 있어서 할인율 변화에 취약.

**할인율 방어력이 높은 그룹:**

MSFT — 밴드 45%, PER 23.3x. 빅테크 중 가장 낮은 멀티플. Azure + Copilot 이중 동력. 관세 직접 노출 거의 없음. 할인율이 올라도 멀티플 수축 폭이 제한적이다.

META — 밴드 35%, PER 24.5x. 빅테크 중 저평가. AI 기반 광고 효율화로 ARPU 상승 중. Reality Labs 연간 $15B+ 손실을 본업이 상쇄하고도 남음.

AMZN — 밴드 40%, AWS + 광고의 고마진 믹스. 이커머스는 관세에 노출되지만 이익의 핵심인 AWS/광고는 아니다.

핵심은 간단하다. **PER 밴드가 낮고, 관세 직접 노출이 없고, 현금흐름이 견조한 종목**이 할인율 상승 국면에서 방어력이 가장 높다. MSFT와 META가 그 교집합의 한가운데 있다.

---

앞으로 내가 제일 먼저 볼 건 실적이 아니다. 할인율의 방향이다.

**DGS10이 4.50%를 돌파하면** — 2026년 인하 기대가 완전히 소멸하고, 클리블랜드 연은이 시사한 인상 시나리오가 시장 화두로 올라온다. PER 밴드 상위의 TSLA, AAPL, COST가 가장 먼저, 가장 크게 흔들린다.

**DGS10이 4.00% 아래로 내려오면** — 인하 기대가 부활하고, 성장주 멀티플이 빠르게 복원된다. MSFT, META, AMZN이 가장 먼저 돌아온다.

4월 말 빅테크 실적 시즌에서 봐야 할 것도 달라진다. 매출·이익 숫자 자체보다 **가이던스의 언어**가 더 중요하다. "tariff"를 몇 번 언급하는지보다, "demand", "FX", "rate environment"를 어떤 톤으로 이야기하는지가 시장의 다음 방향을 결정한다. "관세 영향 제한적, 수요 견조"가 나오면 할인율 공포가 빠진다. "불확실성으로 가이던스 보류"가 나오면 10년물이 다시 오른다.

관세전쟁은 소음이다. 진짜 전쟁은 금리 시장에서 벌어지고 있다.

---

*이 글은 시장 분석 의견이며 투자 권유가 아닙니다. 모든 투자 판단과 그에 따른 결과는 투자자 본인에게 있습니다.*

작성일: 2026.04.09

---

Sources:
- [Goldman Sachs — Fed Rate Cut Outlook 2026](https://www.goldmansachs.com/insights/articles/the-outlook-for-fed-rate-cuts-in-2026)
- [FinancialContent — Fed's 2027 Pivot](https://markets.financialcontent.com/stocks/article/marketminute-2026-4-7-the-feds-2027-pivot-why-sticky-inflation-and-an-energy-shock-have-pushed-rate-cuts-over-the-horizon)
- [FinancialContent — Yield Shock: 10Y Hits 4.35%](https://www.financialcontent.com/article/marketminute-2026-4-6-yield-shock-10-year-treasury-hits-435-as-march-jobs-surprise-redefines-the-feds-path)
- [EBC — Tariffs Affecting Inflation and Stock Markets 2026](https://www.ebc.com/forex/how-are-tariffs-affecting-inflation-and-stock-markets-in-2026)
- [Morningstar — Inflation Set to Rise as Tariff Costs Hit](https://www.morningstar.com/economy/inflation-set-rise-tariff-costs-hit-consumers-2026)
- [FinancialContent — Core PCE Climbs to 3.0%](https://markets.financialcontent.com/stocks/article/marketminute-2026-3-18-inflations-stubborn-shadow-core-pce-climbs-to-30-as-divergence-from-cpi-clouds-fed-rate-path)
- [Trading Economics — US Inflation Expectations](https://tradingeconomics.com/united-states/inflation-expectations)

**태그:** #나스닥 #할인율 #관세전쟁 #금리 #빅테크 #Fed #멀티플 #인플레이션 #미국주식 #GapFinder
