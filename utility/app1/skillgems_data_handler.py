import requests
import json
import os
from datetime import datetime
from .. import data_handler as dh

cwd = os.getcwd()

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


def get_item_divine_value(item_json):
    try:
        return item_json['divineValue']
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
def parse_category(json_data, category_name):
    category_data = {}
    timestamp = datetime.now().isoformat()

    if category_name == 'Currency':
        # next(item for item in json_data["currencyDetails"] if item["name"] == "Divine Orb")
        divine_dict = next(item for item in json_data["lines"] if item["currencyTypeName"] == "Divine Orb")
        divine_price_in_chaos = divine_dict["chaosEquivalent"]
        save_divine_price(divine_price_in_chaos)
        dh.write_json(json_data, dh.get_data_path("currency_prices.json"))

    for i, line in enumerate(json_data['lines']):
        item = json_data['lines'][i]
        category_data[i] = {}
        category_data[i]['name'] = get_item_name(item)
        category_data[i]['value_chaos'] = get_item_chaos_value(item)

        if category_name == 'Currency':
            category_data[i]['value_divine'] = get_item_divine_value(item) / divine_price_in_chaos
        else:
            category_data[i]['value_divine'] = get_item_divine_value(item)

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
        current_league = leagues[8]["id"]

        with open(os.path.join(cwd, "data", "League.txt"), "w") as f:
            f.write(current_league)


def get_path(filename:str, **kwargs):
    subfolder = kwargs.get('subf', None)
    if subfolder:
        path_cur = os.path.abspath(cwd)
        path = os.path.join(path_cur, "data", subfolder, filename)
    else:
        path_cur = os.path.abspath(cwd)
        path = os.path.join(path_cur, "data", filename)
    return path


def load_league():
    os.path.join(cwd, "utility", "", "app1/regular_gem_xp_df")
    path = get_path(filename="League.txt")
    with open(path, "r") as f:
        league = f.readlines()
    return league[0]


def last_update():
    path = get_path(filename="history_gems.txt")
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


def save_divine_price(value):
    with open(os.path.join(cwd, "data", "DivPriceInChaos.txt"), "wt") as f:
        f.write(str(value))


def load_divine_price():
    with open(os.path.join(cwd, "data", "DivPriceInChaos.txt"), "r") as f:
        lines = f.readlines()
        div_val = lines[0]
    return div_val


def get_category_list():
    return [name for name in POENINJA_URL_LIST]


def getList(dict):
    return dict.keys()


def save_raw_json(data):
    path = get_path(filename="raw_data.json", subf="app1")
    with open(path, 'wt') as outfile:
        json.dump(data, outfile)


def load_raw_json():
    path = get_path(filename="raw_data.json", subf="app1")
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
    path_data = get_path(filename="data.json", subf="app1")
    with open(path_data, 'w+') as outfile:
        json.dump(data, outfile)
    path_history = get_path(filename='history_gems.txt')
    with open(path_history, 'a') as record:
        record.write(f'\n {datetime.now().strftime("%d.%m.%Y, %H:%M")}')


def load_json():
    path = get_path(filename="data.json", subf="app1")
    with open(path, 'r') as infile:
        data = json.load(infile)
    return data
