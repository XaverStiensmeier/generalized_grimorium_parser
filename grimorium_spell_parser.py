#!/usr/bin/env python3
import pdftotext
import argparse
import re
import pprint
import dark_aid_parser

specific_parser = {"darkaid": dark_aid_parser.dark_aid_parse}

parser = argparse.ArgumentParser(description='Parse Grimorium style entries')
parser.add_argument('-p', "--pages", default=[42], nargs="+", type=int, help="Page to convert")
parser.add_argument('-s', "--specific_parser", default="general", help="What specific parser to use")
parser.add_argument('-c', '--clean', action="store_true", help="Removes all newlines")
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-f', "--pdf_file", type=str, help="PDF File to read")
group.add_argument('-t', "--txt_file", type=str, help="TXT File to read (ignores page)")


args = parser.parse_args()

def get_entry(s, start, end):
    start_dp = start + ":"
    end_index = s.find(end)
    result = s[s.find(start_dp)+len(start_dp):end_index].strip()
    if "#" in result:
        result = list(filter(None, result.split("#")))
        result_dict = {}
        for i, elem in enumerate(result):
            end_index = elem.find(":")
            name = elem[:end_index]
            body = elem[end_index:].strip(": ")
            if "(FW" in name:
                end_index = name.find("(")
                just_name = name[:end_index].strip()
                el_list = name[end_index:].strip("(FWAP)").split(",")
                if len(el_list) > 2:
                    print(el_list)
                    exit(0)
                fw, ap = name[end_index:].strip("(FWAP)").split(",")
                prereq_pattern = r'.*?(Voraussetzung:.*?rung (.*?)\.)' # rung because sometimes string is split
                prereq_match = re.search(prereq_pattern, body)
                if prereq_match:
                    prereq = prereq_match.group(2)
                    body = body.replace(prereq_match.group(1), "")
                    result_dict[just_name] = {"FW": fw.strip(), "AP": ap.strip(), "description": body.strip(), "prerequisites":[prereq.strip()]}    
                else:
                    result_dict[just_name] = {"FW": fw.strip(), "AP": ap.strip(), "description": body.strip()}
                result = result_dict
            else: # Fluff description
                result_dict[name]:body
    return end_index, start, result

if args.pdf_file:
    with open(args.pdf_file, "rb") as f:
        pdf = pdftotext.PDF(f)
else:
    with open(args.txt_file, "r") as f:
        pdf = {args.pages[0]: "".join(f.readlines())}

for page in args.pages:
    raw_text = pdf[page].replace("\n","",2)

    spell = {"page": page}

    # get name
    end_index = raw_text.find("\n")
    spell["name"] = raw_text[:end_index].strip()
    raw_text = raw_text[end_index:]
    if args.clean:
        raw_text = raw_text.replace("\n", " ").replace("  ", " ").strip()
    # get description
    end_index = raw_text.find("Probe")
    spell["description"] = raw_text[:end_index].strip().replace("\n", " ")
    raw_text = raw_text[end_index:]
    do_split = {"Verbreitung":",", "Zielkategorie": ","} # Probe has its own split
    modifiables = ["Zauberdauer", "AsP-Kosten", "Reichweite"]
    unitable = ["Zauberdauer", "Reichweite"]

    # get rest
    start_index = 0
    start = "Probe"
    for end in ["Wirkung", "Zauberdauer", "AsP-Kosten", "Reichweite", "Wirkungsdauer", "Zielkategorie", "Merkmal", 
                "Verbreitung", "Steigerungsfaktor", "Zaubererweiterungen", "Geste und Formel", "Reversalis"]:
        start_index, key, value = get_entry(raw_text, start+":", end+":")
        key = key[:-1]
        raw_text = raw_text[start_index:]
        if start == "Probe":
                sk_zk_pattern = r'.*?(\(modifiziert um (.*?)\))'
                sk_zk_match = re.search(sk_zk_pattern, value)
                sk_or_zk = None
                if sk_zk_match:
                    sk_or_zk = sk_zk_match.group(2)
                    value = value.replace(sk_zk_match.group(1), "")
                value = {"value": [elem.strip() for elem in value.split("/")], "modifier": sk_or_zk}
        if do_split.get(start):
            value = [elem.strip() for elem in value.split(do_split[start])]
        else:
            if start in modifiables:
                modifiable_pattern = r'.*?(\(.*? nicht modifizierbar\))'
                modifiable_match = re.search(modifiable_pattern, value)
                if modifiable_match:
                    value = value.replace(modifiable_match.group(1), "").strip()
                if start == "AsP-Kosten":
                    value = value.replace("\n","")
                    asp_cost_pattern = r'^(\d+)\sAsP.*\+\s?(\d+)\sAsP.*pro\s(\d+)?\s?(\w+)$'

                    asp_cost_match = re.search(asp_cost_pattern, value)
                    if asp_cost_match:
                        initial_asp_cost = asp_cost_match.group(1)
                        interval_asp_cost = asp_cost_match.group(2)
                        interval_time = asp_cost_match.group(3)
                        interval_unit = asp_cost_match.group(4)
                        value = {"initial_asp_cost": initial_asp_cost, "interval_asp_cost": interval_asp_cost, 
                                "interval_time": interval_time, "interval_time_unit": interval_unit, "modifiable": not bool(modifiable_match)}
                    else:
                        value = {"initial_asp_cost": value.split(" ")[0], "interval_asp_cost": 0, 
                                "interval_time": 0, "interval_time_unit": 0, "modifiable": not bool(modifiable_match)}
                if start in unitable:
                    value_split = value.split(" ")
                    if len(value_split) < 2:
                        value_split += [0]
                    value = {"value": value_split[0], "unit": value_split[1], "modifiable":not bool(modifiable_match)}
                else:
                    value = {"value": value, "modifiable":not bool(modifiable_match)}
            elif start == "Wirkung":
                qs_dict = {}
                if "QS 1:":
                    for qs in range(1,7):
                        qs_str = f"QS {qs}:"
                        start_index = value.find(qs_str)
                        if start_index != -1:
                            end_index = value[start_index:].find(f"QS {qs+1}:")
                            if end_index == -1: end_index = len(value)
                            qs_dict[qs] = value[start_index+len(qs_str):start_index+end_index].strip()
                            value = value[:start_index]+value[start_index+end_index:]
                value = {"value": value.strip(), "qs": qs_dict}
        spell[key] = value
        start = end
    # Reversalis
    start_index = raw_text.find("Reversalis:")
    spell["reversalis"] = raw_text[start_index+len("Reversalis:"):].strip(" 1234567890\n")
    if args.clean:
        spell["reversalis"] = spell["reversalis"].replace("\n", "")
    if args.specific_parser == "general":
        pprint.pprint(spell, width=200, sort_dicts=False)
    else:
        print(specific_parser[args.specific_parser](spell))
