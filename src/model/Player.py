from dataclasses import dataclass

@dataclass 
class Player:
    name: str        # 선수 이름 
    age: int         # 선수 나이 
    year: int        # 선수 태어난 년도
    month: int       # 선수 태어난 월
    day: int         # 선수 태어난 일
    height: int      # 선수 신장
    weight: int      # 선수 몸무게
    position: str    # 선수 포지션
    back_number: int # 선수 등번호
    team: str        # 선수 팀이름
    img_file_path: str # 선수 사진 이미지 파일 경로
    save_file_name: str # 선수 사진 이미지 저장 파일 이름 