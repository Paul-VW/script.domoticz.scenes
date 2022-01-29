import xbmcplugin
import xbmcgui
import xbmc
import xbmcaddon
import sys
import requests
import json
import base64

addon_handle = int(sys.argv[1])
xbmcplugin.setContent(addon_handle, "videos")
addonID = "script.domoticz.scenes"
addonVersion = "0.0.12"
addonDate = "29.01.2022"

__addon__ = xbmcaddon.Addon()
__addonname__ = __addon__.getAddonInfo("name")
__icon__ = __addon__.getAddonInfo("icon")
__language__ = __addon__.getLocalizedString

# Get plugin settings
DEBUG = __addon__.getSettingBool("debug")
domoticz_host = __addon__.getSettingString("domoticz_host")
domoticz_port = __addon__.getSettingInt("domoticz_port")
domoticz_ssl = __addon__.getSettingBool("SSL")
domoticz_user = __addon__.getSettingString("domoticz_user")
domoticz_pass = __addon__.getSettingString("domoticz_pass")
domoticz_group = __addon__.getSettingInt("group")


def get_base_url(host, port, useSsl, username, password):
    if useSsl:
        base_url = "https://" + host + ":" + str(port)
    else:
        base_url = "http://" + host + ":" + str(port)

    username64 = base64.b64encode(username.encode("utf-8"))
    password64 = base64.b64encode(password.encode("utf-8"))

    if not username:
        setcreds = ""
    else:
        setcreds = 'username=' + str(username64.decode("utf-8")) + '&password=' + str(password64.decode("utf-8")) + '&'

    url = base_url + "/json.htm?" + setcreds
    return url


def get_scenes(base_url):
    url = base_url + "type=scenes"
    try:
        result = requests.get(url, verify=False)
    except:
        return -1

    answer = result.content
    jsonResult = json.loads(answer)
    deviceResult = jsonResult["result"]
    return(deviceResult)


def get_favorite_devices_dict(base_url):
    url = base_url + "type=devices&used=true&filter=all&favorite=1"
    try:
        result = requests.get(url, verify=False)
    except:
        return -1

    answer = result.content

    jsonResult = json.loads(answer)
    deviceResult = jsonResult["result"]
    return(deviceResult)


def get_all_switches(base_url):
    url = base_url + "type=devices&filter=light&used=true&order=Name"
    try:
        result = requests.get(url, verify=False)
    except:
        return -1

    answer = result.content

    jsonResult = json.loads(answer)
    deviceResult = jsonResult["result"]
    return(deviceResult)


def switch_scene(base_url, idx):
    url = base_url + "type=command&param=switchscene&idx=" + str(idx) + "&switchcmd=On"
    requests.get(url=url, verify=False)


def switch_switch(base_url, idx):
    url = base_url + "type=command&param=switchlight&idx=" + str(idx) + "&switchcmd=Toggle"
    requests.get(url=url, verify=False)


def switch_dimmer(base_url, idx, state):
    url = base_url + "type=command&param=switchlight&idx=" + str(idx) + "&switchcmd=Set%20Level&level=" + state
    requests.get(url=url, verify=False)


def get_list(optionsDict):
    end_list = __addon__.getLocalizedString(30499)
    optionsList = []
    optionsDict = filter(lambda x: x["Type"] == "Group" or x["Type"] == "Scene" or x["Type"] == "Light/Switch" or x["Type"] == "Color Switch", optionsDict)

    for line in optionsDict:
        optionsList.append(line["Name"])

    optionsList.append(end_list)
    return optionsList


if DEBUG:
    xbmc.log("[ADDON] %s v%s (%s) is starting, ARGV = %s" % (addonID, addonVersion, addonDate, repr(sys.argv)), level=xbmc.LOGINFO)

base_url = get_base_url(host=domoticz_host, port=domoticz_port, useSsl=domoticz_ssl, username=domoticz_user, password=domoticz_pass)

if str(domoticz_group) == "0":
    optionsDict = get_scenes(base_url=base_url)
    optionsList = get_list(optionsDict=optionsDict)

elif str(domoticz_group) == "1":
    optionsDict = get_all_switches(base_url=base_url)
    optionsList = get_list(optionsDict=optionsDict)

elif str(domoticz_group) == "2":
    optionsDict = get_favorite_devices_dict(base_url=base_url)
    optionsList = get_list(optionsDict=optionsDict)

else:
    optionsDict = get_all_switches(base_url=base_url)
    optionsList = get_list(optionsDict=optionsDict)

title = __addon__.getLocalizedString(30498)

answer = xbmcgui.Dialog().select(heading=title, list=optionsList)
action = optionsList[answer]


def get_idx(optionsDict, action):
    for line in optionsDict:
        Name = line["Name"]
        if Name == action:
            idx = line["idx"]
            return idx


def get_favorites_idx(optionsDict, action):
    for line in optionsDict:
        Name = line["Name"]
        if Name == action:
            idx = line["idx"]
            type = line["Type"]
            return idx, type


def run():
    end_list = __addon__.getLocalizedString(30499)

    if action != end_list:
        if str(domoticz_group) == "0":
            idx = get_idx(optionsDict=optionsDict, action=action)
            switch_scene(base_url=base_url, idx=idx)
        elif str(domoticz_group) == "1":
            idx = get_idx(optionsDict=optionsDict, action=action)
            switch_switch(base_url=base_url, idx=idx)
        elif str(domoticz_group) == "2":
            idx, type = get_favorites_idx(optionsDict=optionsDict, action=action)
            if type == "Scene":
                switch_scene(base_url=base_url, idx=idx)
            if type == "Light/Switch":
                switch_switch(base_url=base_url, idx=idx)
            if type == "Color Switch":
                switch_switch(base_url=base_url, idx=idx)
        else:
            idx = get_idx(optionsDict=optionsDict, action=action)
            switch_switch(base_url=base_url, idx=idx)
