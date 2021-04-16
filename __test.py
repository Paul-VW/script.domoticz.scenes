import requests
import json


def get_switches(baseUrl):
    url = baseUrl + "type=devices&filter=light&used=true&order=Name"
    result = requests.get(url)
    answer = result.content
    json_result = json.loads(answer)
    device_result = json_result['result']
    return device_result


def set_dimmer(baseUrl, idx, value):
    url = baseUrl + "type=command&param=switchlight&idx=" + str(idx) + "&switchcmd=Set%20Level&level=" + value
    requests.get(url=url)


def get_dimmer_details(baseUrl, idx):
    url = baseUrl + "type=devices&rid=" + str(idx)
    answer = requests.get(url=url)
    jsonData = json.loads(answer.text)
    name = jsonData['result'][0]['Name']
    level = jsonData['result'][0]['Level']
    status = jsonData['result'][0]['Status']
    return name, level, status


def cli_box(baseUrl):
    idx = input("IDX :")
    name, level, status = get_dimmer_details(baseUrl=baseUrl, idx=idx)
    return idx, name, level, status


def switch_list(baseUrl):
    switches = get_switches(baseUrl=baseUrl)
    switchList = []
    switchList = []
    for s in switches:
        if s['SwitchType'] == 'Dimmer' and s['Type'] == 'Light/Switch':
            sDict = {"Name": s['Name'], "idx": s['idx'], "Status": s['Status']}
            switchList.append(sDict)

    return switchList


base_url = "http://paulvanwens.nl:8081/json.htm?username=UGF1bA==&password=TVh1SHd0YVgx&"
switchList = switch_list(baseUrl=base_url)

print("Idx\t\tNaam\t\t\t\tStatus\n---\t\t---------------\t\t-------------")
for s in switchList:
    print(s['idx'] + "\t\t" + s['Name'] + "\t" + s['Status'])


idx, name, level, status = cli_box(baseUrl=base_url)
new_level = input("Nieuwe level :")

set_dimmer(baseUrl=base_url, idx=idx, value=new_level)

if int(new_level) > 0:
    print('toggle dimmer on')
else:
    print('toggle dimmer off')



