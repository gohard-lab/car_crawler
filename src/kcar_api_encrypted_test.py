import requests
import json

def test_encrypted_payload():
    """
    브라우저에서 추출한 암호화된 Payload를 서버에 그대로 재전송하여 
    응답이 정상적으로 오는지 확인하는 테스트 함수입니다.
    """
    url = "https://api.kcar.com/bc/search/list/drct"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Accept": "application/json",
        # 필요하다면 Referer나 Origin 헤더가 추가로 요구될 수 있습니다.
        "Origin": "https://www.kcar.com",
        "Referer": "https://www.kcar.com/"
    }
    
    # 사용자가 개발자 도구에서 직접 낚아챈 암호화된 Payload
    payload = {
        "enc":"Fb8LpAsK37E++mr/G+Sg/VH1vH4h2v4t9AUl1JJEWo0S84lNGGShtzD4tIgHt2z+yh8/8bZbxIPcki6gW0AumfOCnst0VJP3jABnNKi48V1khuGJST1oEYHBQq9QByMuHFcjJnNSn8dhPEazsautT5QUhpl7z8/6GXrabOC0BywAL9ohsKt4qTVxNgduOGRA"
    }
    
    try:
        print("서버에 암호화된 Payload 요청을 전송합니다...")
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        # 응답 데이터 확인
        data = response.json()
        print("\n[서버 응답 성공!]")
        print("응답 데이터의 일부를 출력합니다:")
        
        # 데이터가 크므로 앞부분만 살짝 잘라서 보여줍니다.
        # 응답 데이터 자체도 암호화되어 있을 가능성이 있습니다.
        print(str(data)[:500] + " ... (이하 생략)")
        
    except requests.exceptions.RequestException as e:
        print(f"\n[오류 발생] 서버가 요청을 거부했습니다: {e}")
        print("암호문에 시간(Timestamp) 정보가 포함되어 만료되었거나, 추가적인 인증 토큰이 필요할 수 있습니다.")

if __name__ == "__main__":
    test_encrypted_payload()