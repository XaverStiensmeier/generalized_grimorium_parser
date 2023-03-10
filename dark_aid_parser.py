#!/usr/bin/env python3
import json
import re

attributes = {"MU":"mut", "KL":"klugheit", "IN":"intuition", "CH":"charisma","FF":"fingerfertigkeit","KK":"körperkraft","KO":"konstitution", "GE":"gewandtheit"}
durations = {"sofort":"immediate", "aufrechterhaltend":"sustaining"}
reach = {"Berührung": "touch", "selbst": "self"}
traditions = {"elfen": "elf", "hexen": "hexe","allgemein":"alle"}

def id(name):
    return name.replace("(","").replace(")","").replace("ä","ae").replace("ö","oe").replace("ü", "ue").replace("ß","ss").replace(" ", "").lower()

def get_enhancements(enhancements):
    return_list = []
    for key, value in enhancements.items():
        enhancement = {"id": id(key), "name":key,
                            "rulesdescription": value["description"]}
        if value.get("prerequisites"):
            enhancement["prerequisites"] = [id(elem) for elem in value["prerequisites"]]
        return_list.append(enhancement)
    return return_list

def get_duration_abbreviation(duration):
    bracket_pattern = r'.*?(\((.*?)\)).*?'
    bracket_match = re.search(bracket_pattern, duration)
    if bracket_match:
        duration = bracket_match.group(1)
    duration = duration.split(",")[0]
    return duration.replace(" Minuten", "min").replace(" Stunden", "h").replace("Kampfrunden", "KR").replace("Jahr","a").replace("pro","/").replace(" ", "")

def dark_aid_parse(general_dict):
    da_dict = {}
    if general_dict["AsP-Kosten"]["value"]["interval_asp_cost"]:
        interval_time = general_dict['AsP-Kosten']['value']['interval_time']
        da_dict["castingcost"] = {
            "abbreviation": "%1+%2/5min",
            "cost": general_dict["AsP-Kosten"]["value"]["initial_asp_cost"],
            "costvariable": general_dict["AsP-Kosten"]["value"]["interval_asp_cost"],
            "name": f"%1 %3 (Aktivierung des Zaubers) + %2 %3 pro{' ' + interval_time if interval_time else ''} "
            f"{general_dict['AsP-Kosten']['value']['interval_time_unit']}"}
        if not general_dict["AsP-Kosten"]["modifiable"]:
            da_dict["castingcost"]["fixed"] = True
    else:
        da_dict["castingcost"] = general_dict["AsP-Kosten"]["value"]["initial_asp_cost"] + ("!" if not general_dict["AsP-Kosten"]["modifiable"] else "")
    da_dict["castingtime"] = general_dict["Zauberdauer"]["value"] + ("!" if not general_dict["Zauberdauer"]["modifiable"] else "")
    da_dict["check"] = [attributes[attribute] for attribute in general_dict["Probe"]["value"]]

    duration = durations.get(general_dict["Wirkungsdauer"], general_dict["Wirkungsdauer"])
    abbreviation = get_duration_abbreviation(duration)
    if abbreviation == duration:
        da_dict["duration"] = duration
    else:
        da_dict["duration"] = {"abbreviation": get_duration_abbreviation(duration),
                            "name":duration}
    
    da_dict["enhancements"] = get_enhancements(general_dict["Zaubererweiterungen"]) # [::2]
    da_dict["ic"] = general_dict["Steigerungsfaktor"].lower()
    da_dict["id"] = id(general_dict["name"])
    if general_dict["Probe"]["modifier"]:
        da_dict["mod"] = general_dict["Probe"]["modifier"]
    da_dict["name"] = general_dict["name"]
    da_dict["page"] = general_dict["page"]
    da_dict["property"] = id(general_dict["Merkmal"])
    da_dict["targets"] = [id(elem) for elem in general_dict["Zielkategorie"]]
    if general_dict["Verbreitung"][0].lower() == "allgemein":
        da_dict["traditions"] = []
    else:
        da_dict["traditions"] = [traditions.get(elem.lower(), elem.lower()) for elem in general_dict["Verbreitung"]]
    da_dict["range"] = reach.get(general_dict["Reichweite"]["value"],general_dict["Reichweite"]["value"]) + ("!" if not general_dict["Reichweite"]["modifiable"] else "")
    da_dict["rulesdescription"] = general_dict["Wirkung"]["value"] + ("\n" + "\n".join([f"QS {key}:{value}" for key,value in general_dict["Wirkung"]["qs"].items()]) if general_dict["Wirkung"]["qs"] else "")
    da_dict["reversalis"]=general_dict["reversalis"]
    #with open("sample.json", "w") as outfile:
    #    outfile.write(json.dumps(da_dict, indent=4, ensure_ascii=False))
    print(json.dumps({"id": da_dict["id"], "page": da_dict["page"]}, indent=4, ensure_ascii=False))
    print("\n\n ")
    return json.dumps(da_dict, indent=4, ensure_ascii=False)