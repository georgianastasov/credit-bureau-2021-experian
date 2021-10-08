def data_dictionary(df):
    df['Account_Type'] = df['Account_Type'].map(
            {'FL': 'Fixed Loan',
             'VL': 'Variable Loan'})

    df['Cheque_Card_Flag'] = df['Cheque_Card_Flag'].map(
            {'': 'N/A',
             'Y': 'Yes',
             'N': 'No'})

    df['Existing_Customer_Flag'] = df['Existing_Customer_Flag'].map(
            {'Y': 'Yes',
             'N': 'No',
             '': 'N/A'})

    df['Home_Telephone_Number'] = df['Home_Telephone_Number'].map(
            {'Y': 'Yes',
             'N': 'No',
             '': 'N/A'})

    df['Insurance_Required'] = df['Insurance_Required'].map(
            {'Y': 'Yes',
             'N': 'No',
             '': 'N/A'})

    df['Loan_Payment_Frequency'] = df['Loan_Payment_Frequency'].map(
            {'': 'N/A',
             'F': 'Two times per month',
             'M': 'Monthly',
             'W': 'Weekly',
             'X': 'Not given'})

    df['Loan_Payment_Method'] = df['Loan_Payment_Method'].map(
            {'': 'N/A',
             'B': 'Bank Payment',
             'Q': 'Cheque',
             'S': 'Standing Order',
             'X': 'Not given'})

    df['Marital_Status'] = df['Marital_Status'].map(
            {'D': 'Divorced',
             'M': 'Married',
             'S': 'Single',
             'W': 'Widow',
             'Z': 'Not given'})

    df['Occupation_Code'] = df['Occupation_Code'].map(
            {'O': 'Other',
             'P': 'Pensioner',
             'B': 'Self-employed',
             'M': 'Employee'})

    df['Residential_Status'] = df['Residential_Status'].map(
            {'H': 'Homeowner',
             'L': 'Living with parents',
             'O': 'Other',
             'T': 'Tenant'})

    df['SP_ER_Reference'] = df['SP_ER_Reference'].map(
            {1: 'Confirmed',
             2: 'Confirmed as previous occupant',
             3: 'Not confirmed',
             4: 'No trace for block and address supplied',
             5: 'No trace block and no address supplied'})
