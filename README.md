# F1 대시보드

Formula 1 월드 챔피언십 1950~2026 데이터로 만든 Streamlit 대시보드입니다.
메인(최신 레이스 결과), 기록(과거 전체 열람), 그리고 질문 8개(폴포지션, 최강팀, GOAT, 리타이어, 서킷, 나이, 날씨, 타이어)로 구성됩니다.

## 실행

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 데이터

- 출처: Kaggle의 Formula 1 World Championship 데이터셋(유지보수: Atharv Ranjan, [github.com/Arths17/f1-dataset](https://github.com/Arths17/f1-dataset)). 라이선스 CC0(퍼블릭 도메인). 칸 설명은 `data/f1/SCHEMA.md`.
- 원본은 2026시즌 15라운드까지였고, 16~20라운드는 [Jolpica-F1 API](https://api.jolpi.ca/ergast/f1/)에서 받아 `update_f1.py`로 이어 붙였습니다.
  - 갱신한 표: races, results, qualifying, sprint_results, driver_standings, constructor_standings (+ 새 드라이버 1명).
  - 갱신하지 않은 표: tire_stints, weather (15라운드까지). 날씨·타이어 탭은 15라운드까지의 데이터입니다.
- 용량 때문에 `lap_times`, `pit_stops`, `constructor_results`, `practice_results`는 저장소에 넣지 않았습니다(앱에서 쓰지 않음).

## 다음 라운드 추가

```bash
python3 update_f1.py --check   # 기존 마지막 라운드를 API로 다시 만들어 비교만 함
python3 update_f1.py           # 빠진 라운드를 추가 (바꾸는 표는 data/f1_backup/ 에 먼저 복사)
```
