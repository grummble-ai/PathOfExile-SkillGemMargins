import json
import requests
import pandas as pd
from .. import data_handler as dh
from ortools.sat.python import cp_model as cp

SAVE_FILE_NAME = "sextant_info_and_data.json"
URL_TFT_DATA = "https://raw.githubusercontent.com/The-Forbidden-Trove/tft-data-prices/master/lsc/bulk-compasses.json"

#
# class VarArraySolutionPrinter(cp.CpSolverSolutionCallback):
#     """Print intermediate solutions."""
#
#     def __init__(self, variables):
#         cp.CpSolverSolutionCallback.__init__(self)
#         self.__variables = variables
#         self.__solution_count = 0
#
#     def on_solution_callback(self):
#         self.__solution_count += 1
#         for v in self.__variables:
#             print('%s=%i' % (v, self.Value(v)), end=' ')
#         print()
#
#     def solution_count(self):
#         return self.__solution_count


def load_TFTdata_from_github():
    print(f"Requesting data from TFT Github")
    req = requests.get(URL_TFT_DATA)
    data = req.json()
    storage_path = dh.get_data_path(filename="sextant_data_tft.json", subf="app2")
    dh.write_json(data=data, file_path=storage_path)
    print(f"Data from TFT Github saved \n")


def add_html_colors_to_confidence_val(df):
    green = "#008000"
    red = "#ff0000"
    df = df.assign(lowConfidenceHTML=
                   [f"<span style=\"color: {red}\">Yes</span>"
                    if x else f"<span style=\"color: {green}\">No</span>"
                    for x in df['lowConfidence']])
    return df


def save_mixed_data(df):
    storage_path = dh.get_data_path(filename=SAVE_FILE_NAME, subf="app2")
    df.to_json(path_or_buf=storage_path)


def mix_sextant_info_and_tft_data():
    print(f"Starting to mix sextant info and tft data")
    path_info = dh.get_data_path(filename="raw_sextant_info.xlsx", subf="app2")
    df_raw = pd.read_excel(path_info, index_col="Nr")

    path_data = dh.get_data_path(filename="sextant_data_tft.json", subf="app2")
    with open(path_data) as f:
        data_json = json.load(f)
    df_tft = pd.json_normalize(data_json, record_path=['data'], meta=['timestamp'])
    # merge both dataframes (raw data and TFT info together)
    df = df_raw.merge(df_tft, on="name")
    # exchange False and True with html spans including colors
    df = add_html_colors_to_confidence_val(df)
    save_mixed_data(df)
    print(f"Mixed data saved")


def exclude_minion_sextants___legacy():
    minion_sextants = ["Additional Monsters deal Fire",
                       "Additional Monsters deal Cold",
                       "Additional Monsters deal Lightning",
                       "Additional Monsters deal Physical",
                       "Additional Monsters deal Chaos"]
    path_data = dh.get_data_path(filename="sextant_data_tft.json", subf="app2")
    data = dh.read_json(path_data)
    sextant_data = data["data"]

    info = []
    exclude = []
    for minion_type in minion_sextants:
        sextant_dict = next(item for item in sextant_data if item["name"] == minion_type)
        info.append([sextant_dict["chaos"], minion_type])

    info_sorted = sorted(info, key=lambda x: int(x[0]))

    # take worst 3 entries and only save their names
    for slices in info_sorted[:3]:
        exclude.append(slices[1])

    dh.write_json(exclude, dh.get_data_path(filename="sextants_to_block.json", subf="app2"))


def find_sextants_to_block(data, tot_weight):
    print("Trying to find sextants to block.")
    model = cp.CpModel()
    num_items = len(data["w_default"])

    # create boolean coefficients
    dv_select_items = {i: model.NewBoolVar("item_" + str(i)) for i in data["w_default"]}

    # constraint: remove exactly 3 items
    model.Add(sum(dv_select_items[i] for i in dv_select_items) == num_items - 3)

    # ##### numerator equation ##### works yields 16750
    constant = 1000
    # x_i * w_i * p_i // sum of weightings * prices = 200.000 -> UB 500.000 to give some space?
    xi_wi_pi = model.NewIntVar(50000 * constant, 500000 * constant, "xi_wi_pi")
    model.Add(xi_wi_pi == sum(
        dv_select_items[i] * data["w_default"][i] * data["chaos"][i] * constant for i in dv_select_items))

    ##### denominator equation ##### works yields 3750
    # xi_wi // sum of weightings 23665: 20665 with 3 blocked
    lb_weights = int(tot_weight * 0.75)
    xi_wi = model.NewIntVar(lb_weights, tot_weight, "xi_wi")
    model.Add(xi_wi == sum(dv_select_items[i] * data["w_default"][i] for i in dv_select_items))

    objective = model.NewIntVar(0, 100 * constant, "objective")
    model.AddDivisionEquality(objective, xi_wi_pi, xi_wi)

    # set target
    model.Maximize(objective)

    # solve the model
    solver = cp.CpSolver()
    status = solver.Solve(model)

    # https://developers.google.com/optimization/cp/cp_solver?hl=de
    # debugging
    solution_printer = VarArraySolutionPrinter([objective, xi_wi_pi, xi_wi])
    solver.parameters.enumerate_all_solutions = True

    # inspect the solution
    objective_function_value = solver.ObjectiveValue()
    solution_info = solver.SolutionInfo()
    status = solver.Solve(model, solution_printer)

    try:
        result = [(i, solver.Value(dv_select_items[i])) for i in dv_select_items]

        # save indices of sextants to exclude
        keep = []
        for item in result:
            if item[1] != 0:
                keep.append(item[0])

        ids = set(range(num_items)).difference(keep)
        names = []
        for index in ids:
            names.append(data["name"][index])

        print(f"Succesfully identified: {names} with ids: {ids}.")
    except:
        ids = []
        names = []
        print(f"Couldn't find any sextants to block!")

        # print(f"exclude: {exclude}")
    # print(f"names: {names}")
    return ids, names


def exclude_sextants():
    # declare data type for dataframe entries
    dtypes = {'name': 'str',
              'w_default': 'int64',
              'chaos': 'int64'}

    path_data = dh.get_data_path(filename="sextant_info_and_data.json", subf="app2")
    df_raw = pd.read_json(path_data)

    # drop unnecessary columns
    df = df_raw[['name', 'w_default', 'chaos', 'lowConfidence']]

    tot_weight = int(df['w_default'].sum())
    # # testing: drop all except first 6 rows
    # df = df.drop(range(5, 74))

    # set datatypes of df columns
    df = df.astype(dtypes)
    # create dict of dict from dataframe
    df_to_dict = df.to_dict(orient="list")

    # create dict from each entry with index as key
    dict_name = {v: k for v, k in enumerate(df_to_dict["name"])}
    dict_weighting = {v: k for v, k in enumerate(df_to_dict["w_default"])}
    dict_price = {v: k for v, k in enumerate(df_to_dict["chaos"])}
    # add all dicts together to a single one
    data = {'name': dict_name, 'w_default': dict_weighting, 'chaos': dict_price}

    # run the optimization
    id, names = find_sextants_to_block(data, tot_weight)

    # # save the results
    print(f"Saving results")
    dh.write_json([list(id), names], dh.get_data_path(filename="sextants_to_block.json", subf="app2"))
    print(f"Results succesfully saved")
