from typing import List, Optional
from tqdm import tqdm
import pandas as pd
import fire
import json
import os


def merge_excel_files(directory: str, output_excel: str, output_json: str) -> None:
    """
    주어진 디렉토리 안에 있는 모든 엑셀 파일을 읽어 하나의 파일로 병합한 후,
    새로운 엑셀 파일과 JSON 파일로 저장하는 함수.

    Args:
        directory (str): 엑셀 파일들이 위치한 디렉토리 경로.
        output_excel (str): 병합된 데이터를 저장할 엑셀 파일 경로.
        output_json (str): 병합된 데이터를 저장할 JSON 파일 경로.

    Raises:
        FileNotFoundError: 주어진 디렉토리가 없을 경우 발생.
        ValueError: 엑셀 파일이 디렉토리 안에 없을 경우 발생.
    """
    
    # 디렉토리가 유효한지 확인
    if not os.path.isdir(directory):
        raise FileNotFoundError(f"디렉토리 {directory}를 찾을 수 없습니다.")
    
    # 디렉토리 내의 모든 엑셀 파일을 찾음
    excel_files: List[str] = [file for file in os.listdir(directory) if file.endswith('.xlsx') or file.endswith('.xls')]
    
    # 엑셀 파일이 없을 경우 예외 처리
    if not excel_files:
        raise ValueError(f"{directory} 안에 엑셀 파일이 없습니다.")
    
    # 엑셀 파일을 하나씩 읽어 병합
    data_frames: List[pd.DataFrame] = []
    for file in tqdm(excel_files, desc="Merging Excel Files"):
        file_path = os.path.join(directory, file)
        df = pd.read_excel(file_path)
        data_frames.append(df)
    
    # 데이터 프레임 병합
    merged_df = pd.concat(data_frames, ignore_index=True)
    
    # 병합된 데이터를 엑셀 파일로 저장
    merged_df.to_excel(output_excel, index=False)
    
    # 병합된 데이터를 JSON 파일로 저장
    merged_df.to_json(output_json, orient='records', force_ascii=False, indent=4)


def main(directory_path: Optional[str] = "risk_factor_profiles", output_path: Optional[str] = "risk_factor_profiles") -> None:
    """
    Args: 
        directory_path(Optional[str]): 엑셀 파일들이 있는 디렉토리 경로
        output_path(Optional[str]): 저장할 파일 경로
    """
    merge_excel_files(directory_path, f"{output_path}.xlsx", f"{output_path}.json")

# Main Entry point
if __name__ == '__main__':
    fire.Fire(main)

