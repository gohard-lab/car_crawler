import requests

def fetch_kcar_prices(keyword):
    """
    케이카 내부 API를 직접 호출하여 특정 차종의 매물 가격 데이터를 JSON 형태로 수집합니다.
    """
    # 실제 K Car의 API 엔드포인트 URL (분석을 통해 찾아낸 주소로 변경 필요)
    api_url = "https://api.kcar.com/search/api/v1/car/search-list" 
    
    # 봇 차단을 우회하고 정상적인 브라우저 요청으로 인식시키기 위한 헤더
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # 서버에 보낼 검색 조건 페이로드 (Payload)
    # 개발자 도구(F12) Network 탭의 'Payload' 또는 'Request Body' 탭에서 구조 확인 가능
    payload = {
        "car_name": keyword,
        "page": 1,
        "limit": 50  # 한 번에 가져올 매물 수
    }
    
    try:
        # POST 방식으로 API에 데이터를 요청합니다.
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        
        # 응답받은 순수 JSON 데이터를 파이썬 딕셔너리로 변환합니다.
        data = response.json()
        
        # JSON 구조를 탐색하여 차량 가격 데이터만 리스트로 추출합니다.
        # 실제 K Car 응답 JSON의 Key 값에 맞게 아래 로직을 수정해야 합니다.
        prices = []
        car_list = data.get('data', {}).get('list', [])
        
        for car in car_list:
            price = car.get('price')
            if price:
                prices.append(int(price))
                
        return prices
        
    except requests.exceptions.RequestException as e:
        print(f"API 요청 중 네트워크 오류가 발생했습니다: {e}")
        return []
    except ValueError:
        print("서버에서 올바른 JSON 데이터를 반환하지 않았습니다.")
        return []

if __name__ == "__main__":
    target_car = "그랜저"
    print(f"[{target_car}] 케이카 API 데이터 수집 시작...")
    
    market_prices = fetch_kcar_prices(target_car)
    
    if market_prices:
        print(f"총 {len(market_prices)}대의 매물 가격 데이터를 수집했습니다.")
        avg_price = sum(market_prices) / len(market_prices)
        print(f"평균 가격: {avg_price:,.0f}만 원")
    else:
        print("데이터를 가져오는 데 실패했거나 매물이 없습니다.")