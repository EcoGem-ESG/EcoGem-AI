♻️ EcoGem Waste Oil Report Generator – 전체 동작 로직
 음식점의 폐식용유 수거 데이터를 기반으로, 자동 PDF 보고서를 생성하는 시스템을 만듦. Gemini API를 이용한 요약 & 해석, 그리고 보고서 형식에 맞춘 시각화 통합.

📦 1. CSV 데이터 로드
waste_collection_realistic_final.csv 파일을 Pandas로 불러옴

Collected At 컬럼은 날짜로 파싱

📍 2. 사용자 입력 받기
가게 이름 (store_name)

분석 시작일 (start_date)

분석 종료일 (end_date)

📊 3. 데이터 필터링 및 통계 계산
analyze_store_range_summary() 함수에서

선택한 가게의 기간 내 데이터를 필터링

총 수거 횟수, 평균 수거량, 평균 수거 간격, 총 수거 금액 계산

🤖 4. Gemini 프롬프트 생성
요약용: Executive Summary용 프롬프트

시각화 해석용: 수거량, 수익 그래프 해석용 프롬프트

🔑 5. Gemini API 호출
call_gemini(prompt, api_key)

gemini-1.5-pro 모델로 요청

응답에서 핵심 텍스트 추출

temperature는 기본값이므로 같은 입력일 때 같은 출력 보장됨

📈 6. 수거량 & 수익 그래프 생성
matplotlib로 두 개의 시계열 라인 그래프 생성

BytesIO()로 이미지 버퍼에 저장 (PDF 삽입을 위해)

📄 7. PDF 보고서 생성 (reportlab)
ECOGEM 스타일 타이틀, 기간, 가게명 포함

Gemini 응답을 줄 단위로 래핑해서 텍스트 박스에 표시

그래프는 넉넉한 크기로 삽입하고, 하단에 해석도 정리

모든 요소는 페이지 나눔과 간격을 고려해서 레이아웃

✅ 최종 결과
가게이름_시작일_to_종료일_report.pdf 형식으로 저장



📂 더미 데이터셋 설명
이 프로젝트에서 사용하는 waste_collection_realistic_final.csv는 2년간의 폐식용유 수거 기록을 기반으로 생성된 더미 데이터셋입니다. 실제 환경을 모사하여 다음과 같은 특징을 가집니다:

| 컬럼명 | 설명 |
|--------|------|
| Store Name | 가게 이름 |
| Address | 가게 주소 |
| Phone Number | 전화번호 |
| Delivery Type | 배출 유형 (SMALL / MEDIUM / LARGE) |
| Collected At | 수거 일자 |
| Volume (L) | 수거량 (리터 단위) |
| Unit Price (KRW) | 리터당 가격 |
| Total Price (KRW) | 수거 총액 |
| Collector | 수거 담당자 이름 |

기간: 2023년 5월 1일 ~ 2025년 4월 30일 (총 2년)

가게 수: 20개 (예: Tony’s Pizza, Mama’s Kimbap 등 실존처럼 보이는 이름)

수거 기록 수: 약 1,300건 이상

가게당 수거 횟수: 최소 20회 ~ 최대 112회 (업종 및 규모 기반 차등 배분)

📌 고정 정보
**주소 / 전화번호 / 배출 유형 (Delivery Type)**은 가게별로 일관되게 유지됨

수거 담당자 이름: Park Ji Hye, Lee Jeong Hwa 등 영어 전체 이름 형식

🚚 Delivery Type 기준
Type	예측 주간 배출량	1회 수거량 범위	예시 업종
SMALL	1~5L	4~10L	카페, 분식집
MEDIUM	6~20L	10~25L	치킨집, 식당
LARGE	20L 이상	25~50L	프랜차이즈, 대형주방


