import requests
import json
import time

API_KEY = '-'
REGION = 'kr'
MATCH_LIMIT = 100
matchs_ids = set()

with open('matchs_ids1.txt', 'r') as file:
    data = file.read()
    data = data.split('\n')
    for id in data:
        if id != '':
            matchs_ids.add(id)

# 게임 타임라인 및 정보 수집
game_info = []

def get_match_info(api_key, match_id, request_limit=100):
    match_info_url = f"https://asia.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={api_key}"
    headers = {'X-Riot-Token': api_key}
    response = requests.get(match_info_url, headers=headers)

    if response.status_code == 200:
        time.sleep(1)
        return response.json()
    else:
        print(f"매칭 ID : {match_id} 의 정보를 불러오지 못하였습니다. 상태 코드: {response.status_code}")
        return None

def process_match_data(api_key, match_ids):

    request_cnt = 0
    for match_id in match_ids:
        match_info_data = get_match_info(api_key, match_id)
        if match_info_data:
            print(f'{match_id} 불러옴')
            game_info.append(match_info_data)
            request_cnt += 1

        if request_cnt >= MATCH_LIMIT:
            break

# 매치 정보 수집
process_match_data(API_KEY, matchs_ids)

#json 파일 작성
def json_out(data, file_name):
    data_dic = {}
    data_dic['matchlists'] = []
    for origin_data in data:
        data_dic['matchlists'].append(origin_data)
    with open(f'{file_name}.json', 'w') as outfile:
        json.dump(data_dic, outfile, indent=4)
    print(f"{file_name}.json 파일 작성 완료")

# 결과를 파일로 저장
json_out(game_info, 'game_info1')