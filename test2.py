import json
from datetime import datetime, timezone, timedelta
import time

def convert_utc_to_kst(utc_timestamp):
    # UTC 시간을 datetime 객체로 변환
    utc_time = datetime.utcfromtimestamp(utc_timestamp / 1000).replace(tzinfo=timezone.utc)
    
    # UTC 시간을 KST로 변환
    kst_time = utc_time.astimezone(timezone(timedelta(hours=9)))
    
    return kst_time


def get_rank_information(json_file_path):
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    for i, match in enumerate(data['matchlists']):
        team_info = 0
        blue_team_num = 1
        red_team_num = 1
        print(f'\n{i+1}번째 경기 포지션 정보')
        metadata = match['metadata']
        matchID = metadata['matchId']
        print(matchID)
        matchInfo = match['info']
        startTime = matchInfo['gameStartTimestamp']
        print(f'게임 시작 시간 : {convert_utc_to_kst(startTime)}')
        endTime = matchInfo['gameEndTimestamp']
        print(f'게임 종료 시간 : {convert_utc_to_kst(endTime)}')
        matchData = matchInfo['participants']
        print('')
        for n, player_data in enumerate(matchData):
            if player_data['teamId'] == 100 and team_info == 0:
                print('Team Blue\n')
                team_info += 1
            elif player_data['teamId'] == 200 and team_info == 1:
                print('Team Red\n')
                team_info += 100
            
            position = player_data['teamPosition']
            champion = player_data['championName']
            total_gold = player_data["goldEarned"]
            kills = player_data['kills']
            deaths = player_data['deaths']
            earlysurrender = player_data['gameEndedInEarlySurrender']
            if n < 5:
                print(f'팀원 {blue_team_num}')
                blue_team_num += 1
            else:
                print(f'팀원 {red_team_num}')
                red_team_num += 1
            print(f'조기 항복 여부 : {earlysurrender}')
            print(f'Position: {position}\nChampion: {champion}')
            print(f'최종 골드량: {total_gold}')
            print(f'Kill: {kills}, Death: {deaths}\n')
        time.sleep(1)

# JSON 파일 경로를 지정하고 함수를 호출합니다.
json_file_path = 'game_info1.json'
get_rank_information(json_file_path)