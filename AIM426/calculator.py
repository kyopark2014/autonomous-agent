def add(a, b):
    """
    두 수를 더하는 함수
    
    Args:
        a (float): 첫 번째 수
        b (float): 두 번째 수
    
    Returns:
        float: 두 수의 합
    """
    return a + b

def subtract(a, b):
    """
    두 수를 빼는 함수
    
    Args:
        a (float): 첫 번째 수 (피감수)
        b (float): 두 번째 수 (감수)
    
    Returns:
        float: 두 수의 차
    """
    return a - b

def multiply(a, b):
    """
    두 수를 곱하는 함수
    
    Args:
        a (float): 첫 번째 수
        b (float): 두 번째 수
    
    Returns:
        float: 두 수의 곱
    """
    return a * b

def divide(a, b):
    """
    두 수를 나누는 함수
    
    Args:
        a (float): 첫 번째 수 (피제수)
        b (float): 두 번째 수 (제수)
    
    Returns:
        float: 두 수의 나눈 결과
        
    Raises:
        ValueError: b가 0일 때 발생
    """
    if b == 0:
        raise ValueError("0으로 나눌 수 없습니다.")
    return a / b

def calculator(a, b, operation):
    """
    계산기 메인 함수
    
    Args:
        a (float): 첫 번째 수
        b (float): 두 번째 수
        operation (str): 연산자 ('+', '-', '*', '/')
    
    Returns:
        float: 계산 결과
        
    Raises:
        ValueError: 지원하지 않는 연산자일 때 발생
    """
    operations = {
        '+': add,
        '-': subtract,
        '*': multiply,
        '/': divide
    }
    
    if operation not in operations:
        raise ValueError(f"지원하지 않는 연산자입니다: {operation}")
    
    return operations[operation](a, b)

def interactive_calculator():
    """
    대화형 계산기 함수
    사용자로부터 입력을 받아 계산을 수행합니다.
    """
    print("=== 간단한 계산기 ===")
    print("지원하는 연산자: +, -, *, /")
    print("종료하려면 'q'를 입력하세요.")
    print()
    
    while True:
        try:
            # 사용자 입력 받기
            user_input = input("계산식을 입력하세요 (예: 5 + 3): ").strip()
            
            if user_input.lower() == 'q':
                print("계산기를 종료합니다.")
                break
            
            # 입력 파싱
            parts = user_input.split()
            if len(parts) != 3:
                print("올바른 형식으로 입력해주세요. (예: 5 + 3)")
                continue
            
            a_str, operation, b_str = parts
            
            # 숫자 변환
            a = float(a_str)
            b = float(b_str)
            
            # 계산 수행
            result = calculator(a, b, operation)
            print(f"결과: {a} {operation} {b} = {result}")
            
        except ValueError as e:
            print(f"오류: {e}")
        except Exception as e:
            print(f"예상치 못한 오류가 발생했습니다: {e}")
        
        print()  # 빈 줄 추가

# 테스트 함수
def test_calculator():
    """
    계산기 함수들을 테스트하는 함수
    """
    print("=== 계산기 테스트 ===")
    
    # 테스트 케이스
    test_cases = [
        (10, 5, '+', 15),
        (10, 5, '-', 5),
        (10, 5, '*', 50),
        (10, 5, '/', 2),
        (7, 3, '+', 10),
        (7, 3, '-', 4),
        (7, 3, '*', 21),
        (7, 3, '/', 7/3)
    ]
    
    for a, b, op, expected in test_cases:
        try:
            result = calculator(a, b, op)
            status = "✓" if abs(result - expected) < 1e-10 else "✗"
            print(f"{status} {a} {op} {b} = {result} (예상: {expected})")
        except Exception as e:
            print(f"✗ {a} {op} {b} 오류: {e}")
    
    # 0으로 나누기 테스트
    try:
        calculator(10, 0, '/')
        print("✗ 0으로 나누기 테스트 실패")
    except ValueError:
        print("✓ 0으로 나누기 예외 처리 성공")
    
    print("\n테스트 완료!")

if __name__ == "__main__":
    # 테스트 실행
    test_calculator()
    print("\n" + "="*50 + "\n")
    
    # 대화형 계산기 실행
    interactive_calculator()
