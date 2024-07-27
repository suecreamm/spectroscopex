import pandas as pd
import sys

def process_csv(file_path):
    df = pd.read_csv(file_path)
    # 데이터 처리 로직 추가
    return df.to_json()

if __name__ == "__main__":
    file_path = sys.argv[1]
    result = process_csv(file_path)
    print(result)

