import requests
import json
import time

API_KEY = '-'
REGION = 'kr'
MATCH_LIMIT = 30
matchs_ids = set() # 매칭 아이디들을 저장할 셋

def write_to_file(data, file_name):
    with open(f'{file_name}.txt', 'w') as f:
        for item in data:
            f.write(str(item) + '\n')
    print(f"{file_name}.txt 파일 작성 완료")

def get_puuid_by_summoner_name(api_key, region, summoner_name): #소환사 이름으로 PUUID 가져오기
    summoner_url = f'https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}'
    headers = {'X-Riot-Token': api_key}
    response = requests.get(summoner_url, headers=headers)

    if response.status_code == 200:
        summoner_data = response.json()
        return summoner_data.get('puuid')
    else:
        print(f"소환사 PUUID 가져오기 실패. 상태 코드: {response.status_code}")
        return None

def get_match_ids(api_key, puuid): #PUUID로 매치 ID 추출 함수
    matchlist_url = f'https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?type=ranked&start=0&count=20&api_key={api_key}'
    headers = {'X-Riot-Token': api_key}
    response = requests.get(matchlist_url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"매치 리스트 가져오기 실패. 상태 코드: {response.status_code}")
        return []

def get_tier_summoner_list(api_key, region, tier, level, page=1, request_limit=10): #티어로 소환사 이름 가져오기
    cnt = 0
    print(f'현재 수집할 티어 : {tier} {level}')
    tier_summoner_list_url = f'https://kr.api.riotgames.com/lol/league/v4/entries/RANKED_SOLO_5x5/{tier}/{level}?page={page}&api_key={api_key}'
    headers = {'X-Riot-Token': api_key}
    response = requests.get(tier_summoner_list_url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        for entry in data:
            print(f"소환사 이름: {entry['summonerName']} 불러옴")
            # 소환사 이름으로 PUUID 가져옴
            puuid = get_puuid_by_summoner_name(api_key, region, entry['summonerName'])
            if puuid:
                #가져온 PUUID으로 매치 ID 추출
                match_ids = get_match_ids(api_key, puuid)
                #추출된 매치 리스트를 셋에 저장
                matchs_ids.update(match_ids)
                time.sleep(1)  # API 호출 간격을 조절

                if cnt >= 5:
                    break
                else:
                    cnt += 1
    else:
        print(f"{tier}티어 소환사 정보 요청이 실패하였습니다. 상태 코드: {response.status_code}")

# 매치 ID 수집
tiers = ['CHALLENGER', 'GRANDMASTER', 'MASTER', 'DIAMOND', 'EMERALD', 'PLATINUM', 'GOLD', 'SILVER', 'BRONZE', 'IRON']
levels = ['I', 'II', 'III', 'IV']

cnt = 0
for tier in tiers:
    for level in levels:
        get_tier_summoner_list(API_KEY, REGION, tier, level, page=1)
        
write_to_file(matchs_ids, 'matchs_ids1')

# 게임 정보 수집
game_info = []

def get_match_info(api_key, match_id, request_limit=30): #매치 아이디로 게임정보 가져오기
    match_info_url = f"https://asia.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={api_key}"
    headers = {'X-Riot-Token': api_key}
    response = requests.get(match_info_url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"매칭 ID : {match_id} 의 정보를 불러오지 못하였습니다. 상태 코드: {response.status_code}")
        return None

def process_match_data(api_key, match_ids):
    request_cnt = 0
    for match_id in match_ids:
        match_info_data = get_match_info(api_key, match_id)
        if match_info_data:
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
