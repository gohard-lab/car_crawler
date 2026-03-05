import sys

def fetch_from_kcar(keyword):
    """
    케이카 API를 호출하여 데이터를 수집합니다.
    """
    print(f"[진행] 케이카 시스템에서 '{keyword}' 데이터를 수집합니다...")
    # 실제 K Car 수집 로직 구현 (이전 코드 참고)
    return [{"site": "Kcar", "price": 25000000}]

def fetch_from_encar(keyword):
    """
    엔카 웹사이트를 분석하여 데이터를 수집합니다.
    """
    print(f"[진행] 엔카 시스템에서 '{keyword}' 데이터를 수집합니다...")
    # 실제 엔카 수집 로직 구현
    return [{"site": "Encar", "price": 24500000}]

def fetch_from_kb(keyword):
    """
    KB차차차 웹사이트를 분석하여 데이터를 수집합니다.
    """
    print(f"[진행] KB차차차 시스템에서 '{keyword}' 데이터를 수집합니다...")
    # 실제 KB차차차 수집 로직 구현
    return [{"site": "KB", "price": 24800000}]

def main():
    print("=" * 40)
    print("중고차 감가 방어율 통합 분석 시스템")
    print("=" * 40)
    print("1. 케이카 (K Car)")
    print("2. 엔카 (Encar)")
    print("3. KB차차차")
    print("=" * 40)
    
    choice = input("데이터를 수집할 타겟 사이트의 번호를 선택하세요: ")
    keyword = input("분석할 차종을 입력하세요 (예: 그랜저): ")
    
    # 사용자의 선택에 따라 각기 다른 크롤링 로직으로 분기 처리 (라우팅)
    if choice == '1':
        results = fetch_from_kcar(keyword)
    elif choice == '2':
        results = fetch_from_encar(keyword)
    elif choice == '3':
        results = fetch_from_kb(keyword)
    else:
        print("잘못된 입력입니다. 프로그램을 종료합니다.")
        sys.exit(1)
        
    print(f"\n[완료] 총 {len(results)}건의 데이터 수집 완료. 분석을 시작합니다.")

if __name__ == "__main__":
    main()