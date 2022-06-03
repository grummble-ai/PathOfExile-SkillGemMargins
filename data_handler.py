import requests
import json
import os
from datetime import datetime

DATETIME_FORMAT = "%Y-%m-%d--%H-%M"
# POENINJA_URL_LIST = {
#     'Currency': {
#         'url': 'https://poe.ninja/api/data/currencyoverview',
#         'type': 'Currency'
#     },
#     'Fragments': {
#         'url': 'https://poe.ninja/api/data/currencyoverview',
#         'type': 'Fragment'
#     },
#     'Incubators': {
#         'url': 'https://poe.ninja/api/data/itemoverview',
#         'type': 'Incubator'
#     },
#     'Scarabs': {
#         'url': 'https://poe.ninja/api/data/itemoverview',
#         'type': 'Scarab'
#     },
#     'Fossils': {
#         'url': 'https://poe.ninja/api/data/itemoverview',
#         'type': 'Fossil'
#     },
#     'Resonators': {
#         'url': 'https://poe.ninja/api/data/itemoverview',
#         'type': 'Resonator'
#     },
#     'Essences': {
#         'url': 'https://poe.ninja/api/data/itemoverview',
#         'type': 'Essence'
#     },
#     'DivinationCards': {
#         'url': 'https://poe.ninja/api/data/itemoverview',
#         'type': 'DivinationCard'
#     },
#     'Prophecies': {
#         'url': 'https://poe.ninja/api/data/itemoverview',
#         'type': 'Prophecy'
#     },
#     'SkillGems': {
#         'url': 'https://poe.ninja/api/data/itemoverview',
#         'type': 'SkillGem'
#     },
#     'BaseTypes': {
#         'url': 'https://poe.ninja/api/data/itemoverview',
#         'type': 'BaseType'
#     },
#     'HelmetEnchants': {
#         'url': 'https://poe.ninja/api/data/itemoverview',
#         'type': 'HelmetEnchant'
#     },
#     'UniqueMaps': {
#         'url': 'https://poe.ninja/api/data/itemoverview',
#         'type': 'UniqueMap'
#     },
#     'Maps': {
#         'url': 'https://poe.ninja/api/data/itemoverview',
#         'type': 'Map'
#     },
#     'UniqueJewels': {
#         'url': 'https://poe.ninja/api/data/itemoverview',
#         'type': 'UniqueJewel'
#     },
#     'UniqueFlasks': {
#         'url': 'https://poe.ninja/api/data/itemoverview',
#         'type': 'UniqueFlask'
#     },
#     'UniqueWeapons': {
#         'url': 'https://poe.ninja/api/data/itemoverview',
#         'type': 'UniqueWeapon'
#     },
#     'UniqueArmour': {
#         'url': 'https://poe.ninja/api/data/itemoverview',
#         'type': 'UniqueArmour'
#     },
#     'UniqueAccesories': {
#         'url': 'https://poe.ninja/api/data/itemoverview',
#         'type': 'UniqueAccessory'
#     },
#     'Beasts': {
#         'url': 'https://poe.ninja/api/data/itemoverview',
#         'type': 'Beast'
#     }
# }

POENINJA_URL_SHORTLIST = {
    'Currency': {
        'url': 'https://poe.ninja/api/data/currencyoverview',
        'type': 'Currency'
    },
    'SkillGems': {
        'url': 'https://poe.ninja/api/data/itemoverview',
        'type': 'SkillGem'
    }
}

POENINJA_URL_LIST = POENINJA_URL_SHORTLIST


def get_item_name(item_json):
    try:
        return item_json['name']
    except KeyError:
        return item_json['currencyTypeName']


def get_item_chaos_value(item_json):
    try:
        return item_json['chaosValue']
    except KeyError:
        return item_json['chaosEquivalent']


def get_item_exalted_value(item_json):
    try:
        return item_json['exaltedValue']
    except KeyError:
        return item_json['chaosEquivalent']


def get_skillGem_additional_info(item_json):
    return item_json['gemLevel'], item_json['levelRequired'], item_json['icon'], item_json['listingCount']


def get_skillGem_corrupted(item_json):
    # some gems are not corrupted and therefore no field is returned
    try:
        return item_json['corrupted']
    except KeyError:
        return False


def get_skillGem_quality(item_json):
    # some gems don't have any quality and therefore no field is returned
    try:
        return item_json['gemQuality']
    except KeyError:
        return 0


# Return data structure:
# dict[item name][key], for example to get Exalted Orb price, use data['Exalted Orb']['value']
def parse_category(json_data, category_name):
    category_data = {}
    timestamp = datetime.now().isoformat()

    if category_name == 'Currency':
        exalted_price = json_data['lines'][7]['chaosEquivalent']

    for i, line in enumerate(json_data['lines']):
        item = json_data['lines'][i]
        category_data[i] = {}
        category_data[i]['name'] = get_item_name(item)
        category_data[i]['value_chaos'] = get_item_chaos_value(item)

        if category_name == 'Currency':
            category_data[i]['value_exalted'] = get_item_exalted_value(item) / exalted_price
        else:
            category_data[i]['value_exalted'] = get_item_exalted_value(item)

        category_data[i]['created'] = timestamp
        category_data[i]['datetime'] = datetime.fromisoformat(timestamp).strftime(DATETIME_FORMAT)
        if category_name == 'SkillGems':
            category_data[i]['corrupted'] = get_skillGem_corrupted(item)
            if "Phantasmal" in item['name']:
                category_data[i]['qualityType'] = "Phantasmal"
                category_data[i]['skill'] = item['name'].replace("Phantasmal", "").lstrip()
            elif "Divergent" in item['name']:
                category_data[i]['qualityType'] = "Divergent"
                category_data[i]['skill'] = item['name'].replace("Divergent", "").lstrip()
            elif "Anomalous" in item['name']:
                category_data[i]['qualityType'] = "Anomalous"
                category_data[i]['skill'] = item['name'].replace("Anomalous", "").lstrip()
            elif "Awakened" in item['name']:
                category_data[i]['qualityType'] = "Awakened"
                category_data[i]['skill'] = item['name']
            elif "Enhance" in item['name']:
                category_data[i]['qualityType'] = "Passive"
                category_data[i]['skill'] = item['name']
            elif "Empower" in item['name']:
                category_data[i]['qualityType'] = "Passive"
                category_data[i]['skill'] = item['name']
            elif "Enlighten" in item['name']:
                category_data[i]['qualityType'] = "Passive"
                category_data[i]['skill'] = item['name']
            elif "Detonate Mines" in item['name']:
                category_data[i]['qualityType'] = "Special"
                category_data[i]['skill'] = item['name']
            elif "Portal" in item['name']:
                category_data[i]['qualityType'] = "Special"
                category_data[i]['skill'] = item['name']
            elif "Blood and Sand" in item['name']:
                category_data[i]['qualityType'] = "Special"
                category_data[i]['skill'] = item['name']
            elif "Brand Recall" in item['name']:
                category_data[i]['qualityType'] = "Special"
                category_data[i]['skill'] = item['name']
            else:
                category_data[i]['qualityType'] = "Normal"
                category_data[i]['skill'] = item['name']

            category_data[i]['gemQuality'] = get_skillGem_quality(item)
            category_data[i]['gemLevel'], \
            category_data[i]['levelRequired'], \
            category_data[i]['icon_url'],\
            category_data[i]['listing_count'] = get_skillGem_additional_info(item)

    return category_data


def load_category(category_name, LEAGUE):
    request_arguments = {'league': LEAGUE,
                         'type': POENINJA_URL_LIST[category_name]['type'],
                         'language': 'en'}

    data_request = requests.get(
        POENINJA_URL_LIST[category_name]['url'], params=request_arguments)

    json_data = data_request.json()

    parsed = parse_category(json_data, category_name)

    return parsed


def request_current_league():
    url = 'https://www.pathofexile.com/api/leagues'
    my_headers = {'user-agent': 'Gem-Margin-Checker/0.5'}
    response = requests.get(url, headers=my_headers)
    if response.status_code == 200:
        leagues = response.json()
        print("Current leagues fetched from poe API:")
        print(leagues)
        current_league = leagues[4]["id"]

        with open("League.txt", "w") as f:
            f.write(current_league)


def get_path(filename):
    path_cur = os.path.abspath(os.getcwd())
    path = os.path.join(path_cur, filename)
    return path


def load_league():
    path = get_path(filename="League.txt")
    with open(path, "r") as f:
        league = f.readlines()
    return league[0]


def last_update():
    path = get_path(filename="History.txt")
    with open(path, "r") as f:
        date = f.readlines()[-1]
    return date


def load_all_categories():
    print("\n")
    request_current_league()
    LEAGUE = load_league()
    print(f"Start fetching data from poe.ninja for league: {LEAGUE}")
    category_data = {}

    for category_name in get_category_list():
        print('Downloading and parsing {0}'.format(category_name))
        category_data[category_name] = load_category(category_name, LEAGUE)

    # database(category_data)
    save_raw_json(category_data)
    print("Successfully saved data to data.json")
    print("\n")


def get_category_list():
    return [name for name in POENINJA_URL_LIST]


def getList(dict):
    return dict.keys()


def save_raw_json(data):
    path = get_path(filename="raw_data.json")
    with open(path, 'wt') as outfile:
        json.dump(data, outfile)


def load_raw_json():
    path = get_path(filename="raw_data.json")
    with open(path, 'r') as infile:
        data = json.load(infile)
    return data


def load_raw_dict(type: str):
    data = load_raw_json()
    if type == "Currency":
        dict = data["Currency"]
    elif type == "Gems":
        dict = data["SkillGems"]
    else:
        ValueError("Provide appropriate type to load.")
    return dict


def save_json(data):
    path_data = get_path(filename="data.json")
    with open(path_data, 'wt') as outfile:
        json.dump(data, outfile)
    path_history = get_path(filename='History.txt')
    with open(path_history, 'a') as record:
        record.write(f'\n {datetime.now().strftime("%d.%m.%Y, %H:%M")}')


def load_json():
    path = get_path(filename="data.json")
    with open(path, 'r') as infile:
        data = json.load(infile)
    return data
