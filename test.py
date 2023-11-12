import requests

def file_out(data, file_name):
    f = open(f'{file_name}.txt', 'w')
    for i in data:
        f.write(str(i)+'\n')
    f.close()
    print(f"{file_name}.txt 파일 작성 완료")


api_key = '-' #API Key
region = 'kr'  # 서버 지역

matchs_ids = set() # 매칭 아이디들을 저장할 셋

def get_match_ids(summoner_name): #소환사 이름으로 매치 ID 추출 함수
    # 소환사 이름으로 PUUID 추출
    summoner_url = f'https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}'
    headers = {'X-Riot-Token': api_key}
    response = requests.get(summoner_url, headers=headers)

    if response.status_code == 200:
        summoner_data = response.json()
        puuid = summoner_data['puuid']
    else:
        print(f"소환사 PUUID 가져오기 실패. 상태 코드: {response.status_code}")
        return None

    #추출한 PUUID로 매칭 ID 추출
    matchlist_url = f'https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?type=ranked&start=0&count=20&api_key={api_key}'
    response = requests.get(matchlist_url, headers=headers)

    if response.status_code == 200:
        matchlist_data = response.json()
        if matchlist_data != []:
            #추출된 매치 리스트를 셋에 저장
            for i in matchlist_data:
                matchs_ids.add(i)
        else:
            print(f"{summoner_name} 유저 랭크 매칭 정보 없음")
    else:
        print(f"매치 리스트 가져오기 실패. 상태 코드: {response.status_code}")
        return None

def get_tier_summoner_list_4_match_id(tier, level, page = 1, request_limit = 10): #티어별로 소환사 이름 수집
    #tier = 'GOLD'
    print(f'현재 수집할 티어 : {tier} {level}')
    tier_summoner_list = f'https://kr.api.riotgames.com/lol/league/v4/entries/RANKED_SOLO_5x5/{tier}/{level}?page={page}&api_key={api_key}'
    headers = {
        'X-Riot-Token': api_key
    }
    response = requests.get(tier_summoner_list, headers=headers)

    if response.status_code == 200:
        data = response.json()
        request_cnt = 0
        for entry in data:
            print(f"소환사 이름: {entry['summonerName']} 불러옴")
            
            # 소환사 이름으로 매치 ID 가져옴
            get_match_ids(entry['summonerName'])
            
            #요청 수 제한 위함
            if request_cnt > request_limit:
                break
            else:
                request_cnt += 1
    else:
        print(f"{tier}티어 소환사 정보 요청이 실패하였습니다. 상태 코드: {response.status_code}")



#티어에 따라 정보 수집
tiers = ['CHALLENGER', 'GRANDMASTER', 'MASTER', 'DIAMOND', 'EMERALD', 'PLATNUM', 'GOLD', 'SILVER', 'BRONZE' , 'IRON']
levels = ['I', 'II', 'III', 'IV']

get_tier_summoner_list_4_match_id(tiers[4], levels[0])
file_out(matchs_ids,'matchs_ids')



game_timeline = [] # 게임 정보들을 넣을 칸
game_info = []

def get_match_timeline(matchs_ids, request_limit = 10):
    request_cnt = 0
    for match_id in matchs_ids:
        match_timeline = f'https://asia.api.riotgames.com/lol/match/v5/matches/{match_id}/timeline?api_key={api_key}'
        headers = {
            'X-Riot-Token': api_key
        }
        response = requests.get(match_timeline, headers=headers)
        if response.status_code == 200:
            data = response.json()
            game_timeline.append(data)
            if request_cnt > request_limit:
                break
            else:
                request_cnt += 1
            print(f"매칭 ID : {match_id} 의 타임라인 불러옴")
        else:
            print(f"매칭 ID : {match_id} 의 타임라인을 불러오지 못하였습니다. 상태 코드: {response.status_code}")
            return None



def get_match_info(matchs_ids, request_limit = 30): #매칭 아이디 셋으로 매칭 정보 불러오기
    request_cnt = 0
    for match_id in matchs_ids:
        match_info = f"https://asia.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={api_key}"
        headers = {
            'X-Riot-Token': api_key
        }
        response = requests.get(match_info, headers=headers)
        if response.status_code == 200:
            data = response.json()
            game_info.append(data)
            if request_cnt > request_limit:
                break
            else:
                request_cnt += 1
            print(f"매칭 ID : {match_id} 의 정보 불러옴")
        else:
            print(f"매칭 ID : {match_id} 의 정보를 불러오지 못하였습니다. 상태 코드: {response.status_code}")
            return None

import json
#json 파일 작성
def json_out(data, file_name):
    data_dic = {}
    data_dic['matchlists'] = []
    for origin_data in data:
        data_dic['matchlists'].append(origin_data)
    with open(f'{file_name}.json', 'w') as outfile:
        json.dump(data_dic, outfile, indent=4)
    print(f"{file_name}.json 파일 작성 완료")

#get_match_timeline(matchs_ids)
#json_out(game_timeline,'game_timeline')

get_match_info(matchs_ids)
json_out(game_info,'game_info')