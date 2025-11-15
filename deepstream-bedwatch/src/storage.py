import json, os, time, csv
from typing import Optional


def ensure_dir(path: str):
    """
    path에 해당하는 파일이 저장될 폴더가 없다면 자동으로 생성해 주는 함수.
    예: path가 'output/status.json'이면 'output/' 폴더를 만들어 둔다.
    """
    d = os.path.dirname(path)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)


def write_status(
    path: str,
    camera_id: str,
    track_id: int,
    prefall: bool,
    dwell: float,
    note: Optional[str] = None,
):
    """
    카메라별/사람별 '현재 상태 스냅샷'을 JSON 파일로 저장하는 함수.

    - path      : 저장할 JSON 파일 경로 (예: output/status.json)
    - camera_id : 카메라 ID (예: 'cam01')
    - track_id  : 추적 ID (지금은 단일 대상이라 1로 사용)
    - prefall   : 현재 침대 엣지 근처 Zone1 안에 있는지 여부
                  ⚠️ 주의: 이름은 prefall이지만, 실제로는 'in_zone1' 의미로 사용 중
    - dwell     : Zone1 안에 누적 체류한 시간(초)
    - note      : 메모 (필요 없으면 None 또는 빈 문자열)

    JSON 구조 예시:
    {
      "cam01:1": {
        "timestamp": "2025-11-14 16:30:12",
        "camera": "cam01",
        "track_id": 1,
        "prefall": true,
        "dwell_sec": 12.34,
        "color": "red",
        "note": ""
      }
    }
    """
    ensure_dir(path)

    data = {}
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            # 파일이 깨져 있거나 파싱에 실패하면 새로 시작
            data = {}

    now = time.strftime("%Y-%m-%d %H:%M:%S")
    key = f"{camera_id}:{track_id}"

    data[key] = {
        "timestamp": now,
        "camera": camera_id,
        "track_id": track_id,
        "prefall": prefall,                 # 현재는 'Zone1에 있는지' 의미
        "dwell_sec": round(dwell, 2),
        "color": "red" if prefall else "green",
        "note": note or "",
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def append_timeline_row(
    path: str,
    camera_id: str,
    track_id: int,
    prefall: bool,
    dwell: float,
    note: Optional[str] = None,
):
    """
    시간 흐름에 따른 로그를 CSV 파일(timeline.csv)에 한 줄씩 추가하는 함수.

    - path      : 저장할 CSV 파일 경로 (예: output/timeline.csv)
    - camera_id : 카메라 ID
    - track_id  : 추적 ID
    - prefall   : 현재 침대 엣지 근처 Zone1 안에 있는지 여부
    - dwell     : Zone1 안에 누적 체류한 시간(초)
    - note      : 메모

    CSV 예시 (첫 줄은 헤더):
    timestamp,camera,track_id,prefall,dwell_sec,note
    2025-11-14 16:30:12,cam01,1,0,0.00,
    2025-11-14 16:30:13,cam01,1,1,3.21,
    """
    ensure_dir(path)
    file_exists = os.path.exists(path)
    now = time.strftime("%Y-%m-%d %H:%M:%S")

    with open(path, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)

        # 파일이 처음 만들어질 때만 헤더를 한 번 써 준다
        if not file_exists:
            writer.writerow(
                ["timestamp", "camera", "track_id", "prefall", "dwell_sec", "note"]
            )

        writer.writerow(
            [now, camera_id, track_id, int(prefall), round(dwell, 2), note or ""]
        )
