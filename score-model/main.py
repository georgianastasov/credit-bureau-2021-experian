###Imports###
import pandas as pd
import numpy as np
import sklearn as sk
import os
import csv
import json

from termcolor import colored
from IPython.testing.globalipapp import get_ipython
from sklearn.model_selection import train_test_split

import statsmodels.api as sm

from flask import Flask
from flask import jsonify

###DEF MAIN###
def main():

    ###Paths###
    projpath = r"D:\Programing\Work\credit-bureau-2021\score-model"
    get_ipython().run_line_magic('run', '"D:\\Programing\\data_dictionary.py"')

    ###Importing Data###
    ds = os.path.join(projpath, r"BankCaseStudyData.csv")
    bcs_data = pd.read_csv(ds)



    ###DataFrame - Json###
    br = 0
    jsonFilePath = r"D:\Programing\Work\credit-bureau-2021\score-model\data.json"
    data = [{
        "account": 1,
        "accountType": "x",
        "bureauScore": 1,
        "chequeCard": "x",
        "insuaranceRequired": "x",
        "loanToIncome": 1.1,
        "loanPaymentMethod": "x",
        "numbersOfPayments": 1,
        "residentialStatus": "x",
        "numberOfSearches": 1,
        "numberOfCCJ": 1,
        "timeAdress": 1,
        "timeEmployment": 1,
        "timeWithBank": 1
    }]
    for i, row in bcs_data.iterrows():
        # decision = row['Final_Decision']
        # delinquencyStatus = row['Current_Delinquency_status']
        # target = row['target']
        id = row['Account_Number']
        accountType = row['Account_Type']
        bureauScore = row['Bureau_Score']
        chequeCard = row['Cheque_Card_Flag']
        insuaranceRequired = row['Insurance_Required']
        loanToIncome = row['Loan_to_income']
        loanPaymentMethod = row['Loan_Payment_Method']
        numbersOfPayments = row['Number_of_Payments']
        residentialStatus = row['Residential_Status']
        numberOfSearches = row['SP_Number_Of_Searches_L6M']
        numberOfCCJ = row['SP_Number_of_CCJs']
        timeAdress = row['Time_at_Address']
        timeEmployment = row['Time_in_Employment']
        timeWithBank = row['Time_with_Bank']
        data.append({"account": id,
                     "accountType": accountType,
                     "bureauScore": bureauScore,
                     "chequeCard": chequeCard,
                     "insuaranceRequired": insuaranceRequired,
                     "loanToIncome": loanToIncome,
                     "loanPaymentMethod": loanPaymentMethod,
                     "numbersOfPayments": numbersOfPayments,
                     "residentialStatus": residentialStatus,
                     "numberOfSearches": numberOfSearches,
                     "numberOfCCJ": numberOfCCJ,
                     "timeAdress": timeAdress,
                     "timeEmployment": timeEmployment,
                     "timeWithBank": timeWithBank})

    # br = 0
    # for i, row in bcs_model.iterrows():
    #    score = row['Score']
    #    data[br]["score"] = score
    #    br += 1


    with open(jsonFilePath, 'w') as jsonFile:
        jsonFile.write(json.dumps(data, indent=4))

    app = Flask(__name__)

    @app.route("/")
    def index():
        return "Welcome Here"

    @app.route("/data", methods=['GET'])
    def get():
        return jsonify(data)

    ###End###

    bcs_data.shape

    ###Derive Target Variable###
    pd.crosstab(bcs_data['Final_Decision'], bcs_data['Current_Delinquency_status'])
    pd.crosstab(bcs_data['Final_Decision'].fillna(-99), bcs_data['Current_Delinquency_status'].fillna(-99),
                margins="Total")

    print(colored('Crossed Final Decision and Delinquency Status', 'green'))
    print(pd.crosstab(bcs_data['Final_Decision'].fillna(-99), bcs_data['Current_Delinquency_status'].fillna(-99),
                      margins="Total"))

    ###target###
    bcs_data['target'] = (
        np.select(
            condlist=[((bcs_data['Current_Delinquency_status'].isna()) & (bcs_data['Final_Decision'] == 'Accept')),
                      ((bcs_data['Current_Delinquency_status'].isna()) & (bcs_data['Final_Decision'] == 'Decline')),
                      bcs_data['Current_Delinquency_status'] < 2,
                      bcs_data['Current_Delinquency_status'] == 2,
                      bcs_data['Current_Delinquency_status'] > 2,
                      ],
            choicelist=['Non-taken up', 'Rejects', 'Good', 'Indeterminate', 'Bad']))

    print(colored('Target', 'green'))
    print(bcs_data['target'].value_counts(dropna=False))

    print(colored('The Bad Rate Is', 'green'))
    print(round(1130 / (16838 + 1130) * 100, 2), "%")

    bcs_data = bcs_data[((bcs_data['target'] == 'Good') | (bcs_data['target'] == 'Bad'))]

    bcs_data['num_target'] = np.where(bcs_data['target'] == "Good", 1, 0)
    bcs_data.shape

    ###Loan To Income###
    bcs_data['loan_to_income_classing'] = pd.cut(bcs_data['Loan_to_income'],
                                                 [-9999998.00, -9999997.00, 0, 10, 30, 60, 100, pd.np.inf], right=False)

    print(colored('Loan To Income Classing', 'green'))
    print(bcs_data['loan_to_income_classing'].value_counts(dropna=False).sort_index())

    ###Bureau Score###
    bcs_data['Bureau_Score_classing'] = pd.cut(bcs_data['Bureau_Score'],
                                               [-np.inf, 764, 803, 844, 859, 877, 911, 941, 961, 974, 1001,
                                                1012, 1025, np.inf], right=False)

    print(colored('Bureau Score Classing', 'green'))
    print(bcs_data['Bureau_Score_classing'].value_counts(dropna=False).sort_index())

    ###Residential Status###
    bcs_data['Residential_Status_classing'] = np.where(bcs_data['Residential_Status'] == "Homeowner", 'H', 'L|O|T')



    ###Create Dummies###
    bcs_data_mod = bcs_data[['target', 'num_target', 'Loan_to_income', 'loan_to_income_classing', 'Residential_Status',
                             'Residential_Status_classing',
                             'Bureau_Score', 'Bureau_Score_classing']].copy()

    bcs_data_mod = pd.concat([bcs_data_mod,
                              pd.get_dummies(bcs_data_mod['loan_to_income_classing'], prefix='loan_to_income',
                                             dummy_na=False),
                              pd.get_dummies(bcs_data_mod['Residential_Status_classing'], prefix='Residential_Status',
                                             dummy_na=False),
                              pd.get_dummies(bcs_data_mod['Bureau_Score_classing'], prefix='Bureau_Score',
                                             dummy_na=False)], axis=1, ignore_index=False, join='outer')

    ###Model Development###
    X_train, X_test, y_train, y_test = train_test_split(bcs_data_mod, bcs_data_mod['num_target'], test_size=0.3,
                                                        random_state=42)

    ###new data sample###
    X_train['sample'] = 'Training'
    X_test['sample'] = 'Testing'

    bcs_model = pd.concat([X_train, X_test], ignore_index=False, sort=False)
    bcs_model = bcs_model.reset_index(drop=True)

    y = bcs_model[bcs_model['sample'] == 'Training']['num_target']
    X = bcs_model[bcs_model['sample'] == 'Training'][['loan_to_income_[0.0, 10.0)', 'loan_to_income_[30.0, 60.0)',
                                                      'loan_to_income_[60.0, 100.0)', 'loan_to_income_[100.0, inf)',
                                                      'Residential_Status_L|O|T',
                                                      'Bureau_Score_[-inf, 764.0)', 'Bureau_Score_[764.0, 803.0)',
                                                      'Bureau_Score_[803.0, 844.0)', 'Bureau_Score_[844.0, 859.0)',
                                                      'Bureau_Score_[859.0, 877.0)', 'Bureau_Score_[877.0, 911.0)',
                                                      'Bureau_Score_[941.0, 961.0)', 'Bureau_Score_[961.0, 974.0)',
                                                      'Bureau_Score_[974.0, 1001.0)',
                                                      'Bureau_Score_[1001.0, 1012.0)',
                                                      'Bureau_Score_[1012.0, 1025.0)', 'Bureau_Score_[1025.0, inf)']]

    X = sm.tools.tools.add_constant(X)
    model_1 = sm.GLM(y, X, family=sm.genmod.families.Binomial(link=sm.genmod.families.links.logit))
    model_final = model_1.fit()
    print(colored('Final Model', 'green'))
    print(model_final.summary())
    model_final



    X['Prediction'] = model_final.predict()

    print(colored('New X Column', 'green'))
    print(X)
    y.mean()

    print(X.columns)


    ###bcs_model.to_pickle(projpath + r"\loan_model.pkl")

    model_coefs = {"loan_to_income_[0.0, 10.0)": 0.5523,
                   "loan_to_income_[30.0, 60.0)": -0.1620,
                   "loan_to_income_[60.0, 100.0)": -0.1995,
                   "loan_to_income_[100.0, inf)": -0.2967,
                   "Residential_Status_L|O|T": 2.6772,
                   "Bureau_Score_[-inf, 764.0)": -1.4985,
                   "Bureau_Score_[764.0, 803.0)": -1.5282,
                   "Bureau_Score_[803.0, 844.0)": -0.9224,
                   "Bureau_Score_[844.0, 859.0)": -0.5833,
                   "Bureau_Score_[859.0, 877.0)": -0.5109,
                   "Bureau_Score_[877.0, 911.0)": -0.2412,
                   "Bureau_Score_[941.0, 961.0)": 0.4801,
                   "Bureau_Score_[961.0, 974.0)": 0.8607,
                   "Bureau_Score_[974.0, 1001.0)": 0.8993,
                   "Bureau_Score_[1001.0, 1012.0)": 1.0315,
                   "Bureau_Score_[1012.0, 1025.0)": 1.0915,
                   "Bureau_Score_[1025.0, inf)": 1.4786}

    def score(df, intercept, coefs):
        value_to_add = 0

        for name, coef in coefs.items():
            value_to_add += coef * (df[name])

        df["Score"] = round((intercept + value_to_add) * 100, 0)

    score(bcs_model, 2.7245, model_coefs)

    print(colored('Several Values of The Score', 'green'))
    print(bcs_model['Score'])

    print(bcs_model.columns)

    ###Building Score Distribution Report in bcs_model###
    bcs_dev = bcs_model[bcs_model['sample'] == 'Training']
    bcs_val = bcs_model[bcs_model['sample'] == 'Testing']

    for i in range(0, 101, 5):
        print(np.percentile(bcs_dev['Score'], i), " - ", i, "%")

    pd.crosstab(pd.cut(bcs_dev['Score'], bins=[82, 155, 183, 206, 221, 233, 249, 257, 272, 292, 307, 319, 333, 347,
                                               349, 361, 364, 400, 415, 472]), bcs_dev["target"])

    sdr = pd.crosstab(
        pd.cut(bcs_dev['Score'], bins=[82, 155, 183, 206, 221, 233, 249, 257, 272, 292, 307, 319, 333, 347,
                                       349, 361, 364, 400, 415, 472]), bcs_dev["target"])

    sdr['Bad Rate'] = round((sdr["Bad"] / (sdr["Bad"] + sdr["Good"])) * 100, 2)
    sdr['GB Odds'] = round(sdr["Good"] / sdr["Bad"], 2)
    sdr['% Total'] = round((sdr["Bad"] + sdr["Good"]) / (sdr["Bad"].sum() + sdr["Good"].sum()) * 100, 2)
    # - Reject - All customers with score less than 225 points
    # - Refer for further manual assessment - All customers with score greater or equal to 225 points, and less than 275 points
    # - Accept - All customers with score greater or equal to 275 points.

    print(colored('SDR Crosstable of The Score Binned at 5%', 'green'))
    print(sdr)

    ###Validation###
    print(colored('Number of Accounts in Training and Testing', 'green'))
    print(bcs_model['sample'].value_counts(dropna=False))

    validation_dev = pd.crosstab(
        pd.cut(bcs_dev['Score'], bins=[82, 155, 183, 206, 221, 233, 249, 257, 272, 292, 307, 319, 333, 347, 349,
                                       361, 364, 400, 415, 472]), bcs_dev["target"])

    validation_val = pd.crosstab(
        pd.cut(bcs_val['Score'], bins=[82, 155, 183, 206, 221, 233, 249, 257, 272, 292, 307, 319, 333, 347, 349,
                                       361, 364, 400, 415, 472]), bcs_val["target"])

    validation_total = pd.crosstab(
        pd.cut(bcs_model['Score'], bins=[82, 155, 183, 206, 221, 233, 249, 257, 272, 292, 307, 319, 333, 347, 349,
                                         361, 364, 400, 415, 472]), bcs_model["target"])

    validation_total.reset_index(inplace=True)
    validation_total.columns.name = 'index'
    validation_dev.reset_index(inplace=True)
    validation_dev.columns.name = 'index'
    validation_val.reset_index(inplace=True)
    validation_val.columns.name = 'index'

    validation_total['total'] = validation_total["Bad"] + validation_total["Good"]
    validation_dev['total'] = validation_dev["Bad"] + validation_dev["Good"]
    validation_val['total'] = validation_val["Bad"] + validation_val["Good"]

    validation_total

    df_combined = validation_dev.merge(right=validation_val, on='Score').merge(right=validation_total, on='Score')
    df_combined

    df_combined.columns
    renaming = {'Bad_x': 'bad_dev',
                'Bad_y': 'bad_val',
                'Good_x': 'good_dev',
                'Good_y': 'good_val',
                'Bad': 'bad_all',
                'Good': 'good_all',
                'total_x': 'total_dev',
                'total_y': 'total_val',
                'total': 'total_all'}

    df_combined = df_combined.rename(columns=renaming)
    print(colored('New Names with dev,val,all', 'green'))
    print(df_combined)

    df_combined.set_index('Score', inplace=True)

    df_combined = df_combined.cumsum()

    renaming_2 = {'bad_dev': 'cum_bad_dev',
                  'good_dev': 'cum_good_dev',
                  'total_dev': 'cum_total_dev',
                  'bad_val': 'cum_bad_val',
                  'good_val': 'cum_good_val',
                  'total_val': 'cum_total_val',
                  'bad_all': 'cum_bad_all',
                  'good_all': 'cum_good_all',
                  'total_all': 'cum_total_all'}

    df_combined = df_combined.rename(columns=renaming_2)
    print(colored('New Names with cum', 'green'))
    print(df_combined)

    df_combined['cum_%_bad_dev'] = round(df_combined['cum_bad_dev'] / df_combined.iloc[-1, 0] * 100, 2)
    df_combined['cum_%_bad_val'] = round(df_combined['cum_bad_val'] / df_combined.iloc[-1, 3] * 100, 2)
    df_combined['cum_%_bad_all'] = round(df_combined['cum_bad_all'] / df_combined.iloc[-1, 6] * 100, 2)

    df_combined['cum_%_good_dev'] = round(df_combined['cum_good_dev'] / df_combined.iloc[-1, 1] * 100, 2)
    df_combined['cum_%_good_val'] = round(df_combined['cum_good_val'] / df_combined.iloc[-1, 4] * 100, 2)
    df_combined['cum_%_good_all'] = round(df_combined['cum_good_all'] / df_combined.iloc[-1, 7] * 100, 2)

    df_combined['cum_%_total_dev'] = round(df_combined['cum_total_dev'] / df_combined.iloc[-1, 2] * 100, 2)
    df_combined['cum_%_total_val'] = round(df_combined['cum_total_val'] / df_combined.iloc[-1, 5] * 100, 2)
    df_combined['cum_%_total_all'] = round(df_combined['cum_total_all'] / df_combined.iloc[-1, 8] * 100, 2)

    print(colored('%%%%%%%%%', 'green'))
    print(df_combined)

    df_combined['dev_val_cum_%diff_bad'] = abs(df_combined['cum_%_bad_dev'] - df_combined['cum_%_bad_val'])
    df_combined['dev_all_cum_%diff_bad'] = abs(df_combined['cum_%_bad_dev'] - df_combined['cum_%_bad_all'])
    df_combined['val_all_cum_%diff_bad'] = abs(df_combined['cum_%_bad_val'] - df_combined['cum_%_bad_all'])

    df_combined['dev_val_cum_%diff_good'] = abs(df_combined['cum_%_good_dev'] - df_combined['cum_%_good_val'])
    df_combined['dev_all_cum_%diff_good'] = abs(df_combined['cum_%_good_dev'] - df_combined['cum_%_good_all'])
    df_combined['val_all_cum_%diff_good'] = abs(df_combined['cum_%_good_val'] - df_combined['cum_%_good_all'])

    df_combined['dev_val_cum_%diff_total'] = abs(df_combined['cum_%_total_dev'] - df_combined['cum_%_total_val'])
    df_combined['dev_all_cum_%diff_total'] = abs(df_combined['cum_%_total_dev'] - df_combined['cum_%_total_all'])
    df_combined['val_all_cum_%diff_total'] = abs(df_combined['cum_%_total_val'] - df_combined['cum_%_total_all'])

    print(colored('%Diff', 'green'))
    print(df_combined)

    KS_dev_val_bad = round(1.358 * np.sqrt((df_combined.iloc[-1, 0] + df_combined.iloc[-1, 3]) / (
            df_combined.iloc[-1, 0] * df_combined.iloc[-1, 3])) * 100, 2)
    KS_dev_all_bad = round(1.358 * np.sqrt((df_combined.iloc[-1, 0] + df_combined.iloc[-1, 6]) / (
            df_combined.iloc[-1, 0] * df_combined.iloc[-1, 6])) * 100, 2)
    KS_val_all_bad = round(1.358 * np.sqrt((df_combined.iloc[-1, 3] + df_combined.iloc[-1, 6]) / (
            df_combined.iloc[-1, 3] * df_combined.iloc[-1, 6])) * 100, 2)

    KS_dev_val_good = round(1.358 * np.sqrt((df_combined.iloc[-1, 1] + df_combined.iloc[-1, 4]) / (
            df_combined.iloc[-1, 1] * df_combined.iloc[-1, 4])) * 100, 2)
    KS_dev_all_good = round(1.358 * np.sqrt((df_combined.iloc[-1, 1] + df_combined.iloc[-1, 7]) / (
            df_combined.iloc[-1, 1] * df_combined.iloc[-1, 7])) * 100, 2)
    KS_val_all_good = round(1.358 * np.sqrt((df_combined.iloc[-1, 4] + df_combined.iloc[-1, 7]) / (
            df_combined.iloc[-1, 4] * df_combined.iloc[-1, 7])) * 100, 2)

    KS_dev_val_total = round(1.358 * np.sqrt((df_combined.iloc[-1, 2] + df_combined.iloc[-1, 5]) / (
            df_combined.iloc[-1, 2] * df_combined.iloc[-1, 5])) * 100, 2)
    KS_dev_all_total = round(1.358 * np.sqrt((df_combined.iloc[-1, 2] + df_combined.iloc[-1, 8]) / (
            df_combined.iloc[-1, 2] * df_combined.iloc[-1, 8])) * 100, 2)
    KS_val_all_total = round(1.358 * np.sqrt((df_combined.iloc[-1, 5] + df_combined.iloc[-1, 8]) / (
            df_combined.iloc[-1, 5] * df_combined.iloc[-1, 8])) * 100, 2)

    test = {'dev_val_cum_%diff_bad': KS_dev_val_bad,
            'dev_all_cum_%diff_bad': KS_dev_all_bad,
            'val_all_cum_%diff_bad': KS_val_all_bad,

            'dev_val_cum_%diff_good': KS_dev_val_good,
            'dev_all_cum_%diff_good': KS_dev_all_good,
            'val_all_cum_%diff_good': KS_val_all_good,

            'dev_val_cum_%diff_total': KS_dev_val_total,
            'dev_all_cum_%diff_total': KS_dev_all_total,
            'val_all_cum_%diff_total': KS_val_all_total}

    validation = {}
    for key, value in test.items():
        if df_combined[key].max() < value:
            validation[key] = 'Valid'
        else:
            validation[key] = 'Invalid'

    print(colored('Valid or Invalid', 'green'))
    for key, value in validation.items():
        print(f'{key} is {value}!')

    app.run(debug=True)

if __name__ == "__main__":
    main()
