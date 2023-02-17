#!/usr/bin/env python3
import json
import re

attributes = {"MU":"mut", "KL":"klugheit", "IN":"intuition", "CH":"charisma","FF":"fingerfertigkeit","KK":"körperkraft","KO":"konstitution", "GE":"gewandtheit"}
durations = {"sofort":"immediate", "aufrechterhaltend":"sustaining"}

def id(name):
    return name.replace("ä","ae").replace("ö","oe").replace("ü", "ue").replace(" ", "").lower()

def get_enhancements(enhancements):
    return_list = []
    for enhancement in enhancements:
        for key, value in enhancement.items():
            return_list.append({"id": id(key), "name":key,
                                "rule_description": value["description"]})
    return return_list

def get_duration_abbreviation(duration):
    bracket_pattern = r'.*?(\((.*?)\)).*?'
    bracket_match = re.search(bracket_pattern, duration)
    if bracket_match:
        duration = bracket_match.group(1)
    return duration.replace(" Minuten", "min").replace(" Stunden", "h").replace("Kampfrunden", "KR").replace("Jahr","a").replace("pro","/").replace(" ", "")

def dark_aid_parse(general_dict):
    da_dict = {}
    da_dict["castingcost"] = general_dict["AsP-Kosten"]["value"]["initial_asp_cost"] + "!" if general_dict["AsP-Kosten"]["modifiable"] else ""
    da_dict["castingcost"] = {
                "abbreviation": "%1+%2/5min",
                "cost": general_dict["AsP-Kosten"]["value"]["initial_asp_cost"] + "!" if general_dict["AsP-Kosten"]["modifiable"] else "",
                "costvariable": general_dict["AsP-Kosten"]["value"]["interval_asp_cost"],
                "name": f"%1 %3 (Aktivierung des Zaubers) + %2 %3 pro {general_dict['AsP-Kosten']['value']['interval_time']} "
                f"{general_dict['AsP-Kosten']['value']['interval_time_unit']}"}
    da_dict["castingtime"] = general_dict["Zauberdauer"]["value"]
    da_dict["check"] = [attributes[attribute] for attribute in general_dict["Probe"]["value"]]
    abbreviation = get_duration_abbreviation(general_dict["Wirkungsdauer"])
    if abbreviation == general_dict["Wirkungsdauer"]:
        da_dict["duration"] = durations.get(general_dict["Wirkungsdauer"], general_dict["Wirkungsdauer"])
    da_dict["duration"] = {"abbreviation": get_duration_abbreviation(general_dict["Wirkungsdauer"]),
                           "name":durations.get(general_dict["Wirkungsdauer"], general_dict["Wirkungsdauer"])}
    da_dict["enhancements"] = get_enhancements(general_dict["Zaubererweiterungen"])
    da_dict["ic"] = general_dict["Steigerungsfaktor"].lower()
    da_dict["id"] = id(general_dict["name"])
    if general_dict["Probe"]["modifier"]:
        da_dict["mod"] = general_dict["Probe"]["modifier"]
    da_dict["name"] = general_dict["name"]
    da_dict["page"] = general_dict["page"]
    da_dict["property"] = general_dict["Merkmal"]
    da_dict["targets"] = general_dict["Zielkategorie"] # why list?
    da_dict["traditions"] = general_dict["Verbreitung"]
    da_dict["range"] = general_dict["Reichweite"]["value"]
    da_dict["rulesdescription"] = general_dict["Wirkung"]["value"] + "\n" + "\n".join([f"QS {key}:{value}" for key,value in general_dict["Wirkung"]["qs"].items()])
    #return json.dumps(da_dict, ensure_ascii=False)
    with open("sample.json", "w") as outfile:
        outfile.write(json.dumps(da_dict, ensure_ascii=False))
    return da_dict