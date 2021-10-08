# # Experian workshop - Scorecard Development

# In this notebook you will find an example of how to develop a scorecard using Linear Regression, how to explore and validate the results. Based on these results you can determine if the model will perform well on previously unseen data. You can alse decide at what score thresholds to Reject or Accept a customer, or Refer it for further manual assessment. 
# 
# This is only an example. You can base your work on this example, but it is not a final model appropriate for implementation. It is up to you to create a better model, that will differentiate between Good and Bad customers well enough to be implemented in a live environment. 
# 
# What constitutes a good model?
#  At minimum:
#  - There must be no inversions in the coefficients of the dummy variables
#  - The model must validate when using the Kolmogorov–Smirnov test
#  
# A good model would also meet these requirements:
#  - It will contain between 7 and 15 variables
#  - There is a good score distribution, without large clusters of the population receiving the same or very similar score (e.g. 5% of the population all receiving 274 points)
#  - The Gini coefficient of the model is as high as possible. For an application model, like the one produced here, you should aim for a Gini coefficient of at least 50-60 points. 
#  
# These points are explored in more detail further on in the code. However, you can and should explore other sources of information as well, including but not limitted to pandas technical documentation and statistical concepts explanations.

# # Scorecard: Linear Regression

# Import needed python libraries and set project path

# In[1]:


import pandas as pd
import numpy as np
import os


# In[2]:


#import the train_test_split functionallity from package sklearn, section model_selection. 
#This will alow us to create a random split of the sample so we can have a holdout sample to validate the model on
from sklearn.model_selection import train_test_split


# In[3]:


#Import statsmodels.api needed for the model development
import statsmodels.api as sm


# In[4]:


# Define the project path:
projpath = r"C:\Users\Experian workshop"


# Make sure you have placed the **data_dictionary.py** and the **BankCaseStudy.csv** file in the projpath directory.
# data_dictionary.py contains a mapping of the values in the data to more meaningful and easy-to-read strings. For example, in variable 'Occupation_Code', value "B" is mapped to its meaning "Self-employed".

# In[5]:


# Apply data dictionary provided by client
get_ipython().run_line_magic('run', '"C:\\Users\\Experian workshop\\data_dictionary.py"')


# ## Importing data

# After data supply by the client, initial data investigation comes in place and the data is prepared for modelling.
# This stage is called data preparation and it includes performing data quality check, data auditing, deriving variables, clarifying Good/Bad flag definition and exclusions, and choosing a sample window for modelling. The result of this data preparation is the file BankCaseStudyData.csv.

# In[6]:


#Read in the data from the project directory; the data is represented as a table, here refered to as dataframe
ds = os.path.join(projpath, r"BankCaseStudyData.csv")
bcs_data = pd.read_csv(ds)


# In[7]:


#Check the shape of the dateframe. The shape is shown in the format (rows, columns)
#Each row is one observation
#Each column is one variable
bcs_data.shape


# Please refer to the Pandas documentation on reading data from csv and carefully parse any dates and any numeric columns which might contain decimal/thousand separators different from the default.
# 
# 
# https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html

# In[8]:


#List all variables contained in the file
bcs_data.columns


# In[9]:


#Check if there are observations with missing Current_Delinquency_status
bcs_data[pd.isna(bcs_data['Current_Delinquency_status'])].shape


# In[10]:


#List all columns that contain the string "App" in their name
for x in bcs_data.columns:
    if "App" in x:
        print(x)


# In[11]:


#Print all values of the variable Application_Month, including missing values. 
bcs_data['Application_Month'].value_counts(dropna=False)


# Values are listed based on number of occurrences.

# In[12]:


#List all columns that contain the string "Delinq" in their name
for x in bcs_data.columns:
    if "Delinq" in x:
        print(x)


# In[13]:


#Print all values of the variable Current_Delinquency_status, including missing values. 
#Print the values sorted by the value of the variable
bcs_data['Current_Delinquency_status'].value_counts(dropna=False).sort_index()


# In[14]:


#check the shape of all cases with duplicated Account_Number
bcs_data[bcs_data.duplicated('Account_Number') == True].shape


# There are no cases with duplicated account number.

# In[15]:


#Print all values of account number
bcs_data['Account_Number'].value_counts(dropna=False)


# As the account number is unique, there are 24 859 unique values. Only a limited number of rows is printed by default.
# This setting can be changed using the command:
# 
# pd.options.display.max_rows = N
# 
# Where N is the number of rows you want to print. This is a general settings change and it will affect the whole notebook/py script. 

# In[16]:


#Print the first rows of the dataframe. 
#By default, 5 rows are printed. This can be changed by addin a number in the brackets
bcs_data.head()


# In[17]:


# Apply the data dictionary to the ds
data_dictionary(bcs_data)

#Print the first 7 rows of the dataframe. 
bcs_data.head(7)


# In[18]:


#Print descriptive statistics for variable Time_at_Address
bcs_data['Time_at_Address'].describe()


# The logical expectation for a "time" variable is to be days, months or years. In this case we can see that we have an average of 1017 and values like 211, 700 and 1506 which are obviously not months or years (1506 months would mean a person living at this address for 125.5 years. We also do not expect time at address to be recorded in days.In such a case we would need further information from the data provider. 
# 
# In our case, the last two digits of the value show the number of months, and the preceeding digits show the number of months. So 1506 means 15 years 6 months. This is the same for the other time variables.

# # Derive Target Variable

# We create a target variable, also referred to as Good/Bad flag. This is the outcome that we are trying to predict. Our target variable is derived on the following logic:
# ![image.png](attachment:image.png)

# In[19]:


#Print all values sorted by index again, for easier access while defining the target variable 
bcs_data['Current_Delinquency_status'].value_counts(dropna=False).sort_index()


# In[20]:


#Check the type of variable Current_Delinquency_status
bcs_data['Current_Delinquency_status'].dtype


# String variables are shown as Object, or dtype('O')
# 
# NB: Pandas allows for a single variable to contain both string and numeric variables. These columns are referred to as "Mixed type columns". They are also shown as Object columns.

# In[21]:


#Create a crosstable between variables Final_Decision and Current_Delinquency_status
pd.crosstab(bcs_data['Final_Decision'],bcs_data['Current_Delinquency_status'])


# pd.crosstab prints only the non-missing values for the included variables. In order to add the missing values we can fill them with a special value for the execution of this crosstab. You can read about more options in the official documentation for Pandas crosstab.

# In[22]:


#Repeat the crosstable, this time filling in the missing values and adding the total counts
pd.crosstab(bcs_data['Final_Decision'].fillna(-99),bcs_data['Current_Delinquency_status'].fillna(-99), margins="Total")


# In[23]:


#Derive the target variable 

bcs_data['target'] = (
        np.select(
        condlist=[((bcs_data['Current_Delinquency_status'].isna()) & (bcs_data['Final_Decision'] == 'Accept')),
                  ((bcs_data['Current_Delinquency_status'].isna()) & (bcs_data['Final_Decision'] == 'Decline')),
                  bcs_data['Current_Delinquency_status'] < 2,
                  bcs_data['Current_Delinquency_status'] == 2,
                  bcs_data['Current_Delinquency_status']  > 2,
                  ],
        choicelist=['NTU', 'Rejects', 'Good', 'Indeterminate', 'Bad']))


# Cases that meet the first condition in the condlist take the first value in the choicelist. 
# So if 'Current_Delinquency_status' is missing and 'Final_Decision' is 'Accept', then this observation will receive the value "NTU" (or "Non-taken up") for the 'target' variable. "NTU"s are customers who were accepted by the bank but decided not to take the credit.
# 
# The rest of the condlist/choicelist matches follow the same logic.

# In[24]:


#Print the values of the newly derived target variable
bcs_data['target'].value_counts(dropna=False)


# In[25]:


#Calculate the Bad Rate of the sample as 
# [N Bad Accounts]/([N Good Accounts]+[N Bad Accounts])
print("The Bad rate is ", round(1130/(16838+1130)*100,2), "%")


# # Take only Good and Bad observations and continue with them

# In[26]:


bcs_data = bcs_data[((bcs_data['target'] == 'Good') | (bcs_data['target'] == 'Bad'))]


# In[27]:


# creating numeric binary flag for various calculations: 
#If variable 'target' = 'Good', then variable 'num_target' = 1, otherwise 'num_target'=0
bcs_data['num_target'] = np.where(bcs_data['target'] =="Good", 1, 0)


# In[28]:


bcs_data.shape


# 
# # Classing / Binning
# 
# We are going to transorm the variables from vaues to ranges or lists of values. Our goal is to group customers with similar expected behaviour in one bin. When binning numeric variables, these values must be continuous. I.e. we can bin together 1 - 5, 6 - 10, but we can NOT bin together (1,3,5,7,9) and (2,4,6,8,10).
# 
# It is up to you to decide which variables to use and how to bin their values for you model. You can base that on data exploration that you carry out, on research you conduct from other sources or by any method you see fit. 

# Note: Variable SP_ER_Reference shows information about UK Electoral Roll Reference. 

# ## Loan to income

# This variable shows the loan amount as a percentage of the gross annual income. We can expect values between 0 and 100 if the loan is less than the gross annual income, and larger than 100 if the loan is more than the gross annual income. A value of -9999998 means that the loan amount value is 0 (data error); a value of -9999997 means that the gross annual income is 0 (possible data error, or the customer did not state their income, or they don't have any officially declared income). It is up to you as an analyst to decide how to treat these values.

# In[29]:


#Print the values of variable loan_to_income
bcs_data['loan_to_income'].value_counts(dropna=False)


# In[30]:


#Create classing for loan_to_income by specifying the borders of the ranges
bcs_data['loan_to_income_classing'] = pd.cut(bcs_data['loan_to_income'],[-9999998.00,-9999997.00, 0, 10, 30, 60, 100,pd.np.inf],right=False)


# In[31]:


#Print the values of variable loan_to_income_classing sorted by index

bcs_data['loan_to_income_classing'].value_counts(dropna=False).sort_index()


# In[32]:


# Visualizing the probability of being Good for each class
bcs_data.groupby(['loan_to_income_classing'])['num_target'].mean()


# We can see that the higher the value of the loan_to_income variable is, the lower the probability of the customer being Good. This is logical and we can confirm that the data are showing a logical relationship between the predictor and the target variable. If, for exampl, the data show that low income is related to higher probability of paying the loan, this is not logical and we shoul not use this variable in our model. We should always check that the trend in the data is logical.

# ## Bureau Score

# Bureau score comes from the Experian bureau where data from different financtial institutions is collected and analyzed.

# In[33]:


#Print the values of variable Bureau_Score
bcs_data['Bureau_Score'].value_counts(dropna=False).sort_index()


# In[34]:


#Create classing for Bureau_Score by specifying the borders of the ranges
bcs_data['Bureau_Score_classing'] = pd.cut(bcs_data['Bureau_Score'],[-np.inf, 764, 803, 844, 859, 877, 911, 941, 961, 971, 978, 
                                                                     990, 1012, 1025, np.inf],right=False)


# In[35]:


#Print the values of variable Bureau_Score_classing sorted by index

bcs_data['Bureau_Score_classing'].value_counts(dropna=False).sort_index()


# In[36]:


# Visualizing the probability of being Good for each class
bcs_data.groupby(['Bureau_Score_classing'])['num_target'].mean()


# ## Residential Status

# In[37]:


#Check for observations with missing Residential_Status
bcs_data[pd.isna(bcs_data['Residential_Status'])].shape


# In[38]:


#Print the values of variable Residential_Status
bcs_data['Residential_Status'].value_counts()


# In[39]:


#Create classing for Residential_Status using an if/else structure
# if Residential_Status = H, then Residential_Status_classing = H, else Residential_Status_classing = 'L|O|T'

bcs_data['Residential_Status_classing'] = np.where(bcs_data['Residential_Status'] =="Homeowner", 'H', 'L|O|T')


# In[40]:


bcs_data['Residential_Status_classing'].value_counts(dropna=False)


# In[41]:


# Visualizing the probability of being Good for each class
bcs_data.groupby(['Residential_Status_classing'])['num_target'].mean()


# In[42]:


#Check the columns contained in the dataframe. We can see the new variables we created
bcs_data.columns


# # Create Dummies
# In the regression model we will use variables that have values of 1 or 0. To do that, we will transform the classed variables into dummies. For example, Residential_Status_classing contains values 'H' and 'L|O|T'. It will be transformed into two new variables: Residential_Status_H and Residential_Status_L|O|T. If an observation had a value of H, it will now have Residential_Status_H = 1 and Residential_Status_L|O|T = 0

# In[43]:


#Create a new frame keeping only the variables needed for the modelling process
bcs_data_mod = bcs_data[['target','num_target','loan_to_income','loan_to_income_classing','Residential_Status','Residential_Status_classing',
                         'Bureau_Score' ,'Bureau_Score_classing']].copy()


# In[44]:


#Transform the variables into dummies
#by using pd.get_dummies we create a dataframe with the transformed variable
#by using pd.concat we combine these new dataframes with the initial one
#we can incorporate the pd.get_dummies step within the pd.concatenate one
bcs_data_mod = pd.concat([bcs_data_mod,
                    pd.get_dummies(bcs_data_mod['loan_to_income_classing'],prefix ='loan_to_income',dummy_na= False),
                    pd.get_dummies(bcs_data_mod['Residential_Status_classing'],prefix ='Residential_Status',dummy_na= False),
                    pd.get_dummies(bcs_data_mod['Bureau_Score_classing'],prefix ='Bureau_Score',dummy_na= False)], axis=1,ignore_index=False,join='outer')


# # Model Development

# In[45]:


#Check the shape of the modelling dataframe
bcs_data_mod.shape


# In[46]:


#Create a holdout sample of 30% of the populaiton (test_size = 0.3)
#This will create two dataframes with variables X_train and X_test, and two with the target variable -  y_train,y_test
X_train, X_test,y_train,y_test = train_test_split(bcs_data_mod,bcs_data_mod['num_target'],test_size = 0.3,random_state=42)


# In[47]:


#Create a new variable 'sample' in the two dataframes created by the train_test_split
X_train['sample'] = 'Training'
X_test['sample'] = 'Testing'


# In[48]:


#Check the shape of X_train, containing the dummy variables and the train population on which we will create the model
X_train.shape


# In[49]:


#Combine the train and test dataframes back into one. 
#We will be able to identify if the observation is in train or test population by the new variable - sample
bcs_model = pd.concat([X_train,X_test],ignore_index=False,sort=False)
bcs_model = bcs_model.reset_index(drop=True)
bcs_model.shape


# In[50]:


#Check the distribution of the "sample" variable. 
#The number of observations with value "Training" should match the number of rows from X_train.shape
bcs_model['sample'].value_counts(dropna=False)


# In[51]:


bcs_model.head()


# In[52]:


bcs_model.columns


# In[53]:


#Define the X and y parameters needed for running the model. 
#X will contain all predictors/dummies from the Training subpopulation. y will contain the respective target variable
#In order to avoin perfect correlation, we must select a "null band" which will not be used as a predictor. 
#That is why one band is missing from each of the 3 variables
y = bcs_model[bcs_model['sample']=='Training']['num_target']
X = bcs_model[bcs_model['sample']=='Training'][['loan_to_income_[0.0, 10.0)','loan_to_income_[30.0, 60.0)',
                                                'loan_to_income_[60.0, 100.0)', 'loan_to_income_[100.0, inf)',
                                                'Residential_Status_L|O|T',
                                               'Bureau_Score_[-inf, 764.0)', 'Bureau_Score_[764.0, 803.0)',
                                               'Bureau_Score_[803.0, 844.0)', 'Bureau_Score_[844.0, 859.0)',
                                               'Bureau_Score_[859.0, 877.0)', 'Bureau_Score_[877.0, 911.0)',
                                               'Bureau_Score_[941.0, 961.0)','Bureau_Score_[961.0, 971.0)', 
                                               'Bureau_Score_[971.0, 978.0)','Bureau_Score_[978.0, 990.0)', 
                                               'Bureau_Score_[990.0, 1012.0)','Bureau_Score_[1012.0, 1025.0)', 
                                               'Bureau_Score_[1025.0, inf)']]


# You can find more information about the Generalized Linear Models here:
# https://www.statsmodels.org/stable/glm.html

# In[54]:


#Define the model parameters and fit it to the data, print a summary of the model
X = sm.tools.tools.add_constant(X)
model_1 = sm.GLM(y,X,family=sm.genmod.families.Binomial(link=sm.genmod.families.links.logit))
model_final = model_1.fit()
print(model_final.summary())


# In order to know that all bands are statistically significant, the P>|z| value must be less than 0.05 
# 
# Moreover, the points assigned to each band should follow a linear trend. For example, the higher the Bureau score is, the higher the points they should receive. However, we can see that in customers with Bureau score between 978 and 990 are assigned less points (have a lower coefficient) than Bureau score 971 to 978. This inversion is incorrect and should be fixed in order to produce a proper model. There are several ways to correct an inversion:
# - merge bands together
# - distribute the band with the inversion into the neighbouring bands; e.g. create two new bands: [971 : 985),[985 : 1012)
# - remove the variable if the inversion cannot be corrected

# In[55]:


#the model is saved as python object
model_final


# In[56]:


#Create a new variable with the prediction from the model 
X['Prediction'] = model_final.predict()


# In[57]:


#by printing the X dataframe we can see the new column
X


# In[58]:


y.mean()


# In[59]:


#Save as pickle file
bcs_model.to_pickle(projpath + r"\loan_model.pkl")


# In[60]:


bcs_model.columns


# In[61]:


bcs_model.head()


# In[62]:


X.columns.values


# In[63]:


#create a new dictionary containing the dummy and its coefficient from the model
model_coefs = {"loan_to_income_[0.0, 10.0)" :        0.5665,     
        "loan_to_income_[30.0, 60.0)" :     -0.1566 ,     
        "loan_to_income_[60.0, 100.0)" :      -0.1924,   
        "loan_to_income_[100.0, inf)" :      -0.2832,
        "Residential_Status_L|O|T" :         -0.1193,
        "Bureau_Score_[-inf, 764.0)" :      -1.4556,
        "Bureau_Score_[764.0, 803.0)" :     -1.5022,
        "Bureau_Score_[803.0, 844.0)" :      -0.8944,
        "Bureau_Score_[844.0, 859.0)" :       -0.5752,
        "Bureau_Score_[859.0, 877.0)" :       -0.5074,
        "Bureau_Score_[877.0, 911.0)" :       -0.2342,
        "Bureau_Score_[941.0, 961.0)" :        0.4668,
        "Bureau_Score_[961.0, 971.0)" :        0.7499,
        "Bureau_Score_[971.0, 978.0)" :        0.9180,
        "Bureau_Score_[978.0, 990.0)" :        0.8559,
        "Bureau_Score_[990.0, 1012.0)" :       0.9188,
        "Bureau_Score_[1012.0, 1025.0)" :      1.0444,
        "Bureau_Score_[1025.0, inf)" :         1.4282}


# In[64]:


#Define a function that takes the dataframe, value of the intercept from the model and 
#     the dictionary of dummy - coefficient and creates a new variable - score

def score(df, intercept, coefs):
    value_to_add = 0
   
    for name, coef in coefs.items():
        value_to_add += coef*(df[name])
       
    df["Score"] = round((intercept + value_to_add)*100,0)


# In[65]:


#Execute the fucnction on the full dataframe containing both Training and Testing populations
score(bcs_model, 2.7245, model_coefs)


# # Building SDR

# The SDR, or Score Distribution Report, shows us how the score is distributed throughout the population. We want to have a good spread without clusters in a specific score. Having clusters would mean that the scorecard does not recognize the differences between customers well enough.

# In[66]:


#Print several values of the score
bcs_model['Score']


# In[67]:


#Split the dataframe into Training (aka Development) and Testing(aka Validation)
bcs_dev = bcs_model[bcs_model['sample'] == 'Training']
bcs_val = bcs_model[bcs_model['sample'] == 'Testing']


# In[68]:


#We want to see the score distribution at every 5% of the score. To do that,first we check the value at each 5th percentile
for i in range(0,101,5):
    print(np.percentile(bcs_dev['Score'],i), ",")


# In[69]:


#We can also check the max value of the score
max(bcs_dev['Score'])


# In[70]:


bcs_dev['Score'].describe()


# In[71]:


#We create a crosstable of the score binned at 5% and the target variable 
pd.crosstab(pd.cut(bcs_dev['Score'],bins=[82 ,
                                            155 ,
                                            183 ,
                                            206 ,
                                            221 ,
                                            233 ,
                                            249 ,
                                            257 ,
                                            272 ,
                                            292 ,
                                            307 ,
                                            319 ,
                                            333 ,
                                            347 ,
                                            349 ,
                                            361 ,
                                            364 ,
                                            400 ,
                                            415 ,
                                            472]), bcs_dev["target"])


# In[72]:


#Run the table again, saving it as an object
sdr = pd.crosstab(pd.cut(bcs_dev['Score'],bins=[82 ,
                                                155 ,
                                                183 ,
                                                206 ,
                                                221 ,
                                                233 ,
                                                249 ,
                                                257 ,
                                                272 ,
                                                292 ,
                                                307 ,
                                                319 ,
                                                333 ,
                                                347 ,
                                                349 ,
                                                361 ,
                                                364 ,
                                                400 ,
                                                415 ,
                                                472]), bcs_dev["target"])


# In[73]:


#Calculate the Bad rate at each row, present it as a percent in format NN.NN%
sdr['Bad Rate'] = round((sdr["Bad"]/(sdr["Bad"] + sdr["Good"]))*100,2)


# In[74]:


#Calculate the Good to Bad rate at each row, showing how many Good accounts we have for 1 Bad account
sdr['GB Odds'] = round(sdr["Good"]/sdr["Bad"],2)


# In[75]:


#Calculate the percent of the total population at each row
sdr['% Total'] = round((sdr["Bad"] + sdr["Good"])/(sdr["Bad"].sum() + sdr["Good"].sum())*100,2)


# In[76]:


sdr


# Based on the score distribution report and the Bad rate of each band, you can decide the thresholds for Rejecting,Referring or Accepting a customer.
# 
# For example:
# - Reject - All customers with score less than 200 points
# - Refer for further manual assessment - All customers with score greater or equal to 200 points, and less than 250 points
# - Accept - All customers with score greater or equal to 250 points. 
# 
# The decision and thresholds depend entirely on what strategy you as the bank want to adopt. This is only an example and you should determine these thresholds for your particular model and considerations.

# # Validation

# In order to know that the model will perform equally well on new data that the bank will use it on, we must perform a validation test. To see if the model performs as well on data different from the one it was developped on, we will use the Kolmogorov–Smirnov test on two samples. Previously we split the data into Development and Validation. We used the Development sample to create the model. We then scored the full dataframe and split it again into Development and Validation. Now we will perform the KS validation test which compares the distribution of the cumulative number of Goods, Bads and Total in the samples. In order to confirm that the model works well, we must confirm that the distributions are not statistically different when comparing the three populations - Development, Validation and the Full sample. This results in 9 comparisons of maximum difference of cumulative numbers:
# 
# Development and Validation popultions - Bad accounts
# 
# Development and Full populations - Bad accounts
# 
# Validation and Full populations - Bad accounts
#     
#     
# Development and Validation popultions - Good Accounts
# 
# Development and Full populations - Good Accounts
# 
# Validation and Full populations - Good Accounts
#     
#     
# Development and Validation popultions - Total accounts
# 
# Development and Full populations - Total accounts
# 
# Validation and Full populations - Total accounts

# In[77]:


#Print the number of accounts in Training and Testing again 
bcs_model['sample'].value_counts(dropna=False)


# We already created a 5% SDR on the Development population. Now we apply these bands to the Development, Validation and Full populations and save them as new dataframes. The 5% bands are created based on the Development population and then used on the other two populations without changing them.

# In[78]:


validation_dev = pd.crosstab(pd.cut(bcs_dev['Score'],bins=[82 ,
                                                                155 ,
                                                                183 ,
                                                                206 ,
                                                                221 ,
                                                                233 ,
                                                                249 ,
                                                                257 ,
                                                                272 ,
                                                                292 ,
                                                                307 ,
                                                                319 ,
                                                                333 ,
                                                                347 ,
                                                                349 ,
                                                                361 ,
                                                                364 ,
                                                                400 ,
                                                                415 ,
                                                                472]), bcs_dev["target"])


# In[79]:


validation_val = pd.crosstab(pd.cut(bcs_val['Score'],bins=[82 ,
                                                            155 ,
                                                            183 ,
                                                            206 ,
                                                            221 ,
                                                            233 ,
                                                            249 ,
                                                            257 ,
                                                            272 ,
                                                            292 ,
                                                            307 ,
                                                            319 ,
                                                            333 ,
                                                            347 ,
                                                            349 ,
                                                            361 ,
                                                            364 ,
                                                            400 ,
                                                            415 ,
                                                            472]), bcs_val["target"])


# In[80]:


validation_total = pd.crosstab(pd.cut(bcs_model['Score'],bins=[82 ,
                                                                155 ,
                                                                183 ,
                                                                206 ,
                                                                221 ,
                                                                233 ,
                                                                249 ,
                                                                257 ,
                                                                272 ,
                                                                292 ,
                                                                307 ,
                                                                319 ,
                                                                333 ,
                                                                347 ,
                                                                349 ,
                                                                361 ,
                                                                364 ,
                                                                400 ,
                                                                415 ,
                                                                472]), bcs_model["target"])


# In[81]:


validation_total.reset_index(inplace = True)
validation_total.columns.name = 'index'
validation_dev.reset_index(inplace = True)
validation_dev.columns.name = 'index'
validation_val.reset_index(inplace = True)
validation_val.columns.name = 'index'


# In[82]:


validation_total['total'] = validation_total["Bad"] + validation_total["Good"]
validation_dev['total'] = validation_dev["Bad"] + validation_dev["Good"]
validation_val['total'] = validation_val["Bad"]  + validation_val["Good"]


# In[83]:


validation_total


# In[84]:


df_combined = validation_dev.merge(right=validation_val, on='Score').merge(right=validation_total, on='Score')
df_combined


# In[85]:


df_combined.columns


# In[86]:


renaming = {'Bad_x': 'bad_dev', 
            'Bad_y': 'bad_val', 
            'Good_x': 'good_dev', 
            'Good_y': 'good_val', 
            'Bad': 'bad_all', 
            'Good': 'good_all',
            'total_x': 'total_dev',
            'total_y': 'total_val',
            'total': 'total_all'}


# In[87]:


df_combined = df_combined.rename(columns = renaming)
df_combined


# In[88]:


#Set the Score variable as an indef for the dataframe
df_combined.set_index('Score',inplace=True)


# All of the following steps can also be conducted in excel. Please refer to the excel file "Excel validation test.xlsx"

# In[89]:


#Export the above table in order to continue work in excel (if you choose to conduct this test in Excel)
df_combined.to_csv(os.path.join(projpath,"Combined_frequencies_per_subpopulation.csv"))


# In[90]:


#Transform the number of accounts per row into cummulative number of accounts
df_combined = df_combined.cumsum()


# In[91]:


renaming_2 = {'bad_dev': 'cum_bad_dev', 
              'good_dev': 'cum_good_dev', 
              'total_dev': 'cum_total_dev', 
              'bad_val': 'cum_bad_val', 
              'good_val': 'cum_good_val', 
              'total_val': 'cum_total_val',
              'bad_all': 'cum_bad_all',
              'good_all': 'cum_good_all',
              'total_all': 'cum_total_all'}


# In[92]:


df_combined = df_combined.rename(columns = renaming_2)
df_combined


# In[93]:


#Calculate the cumulative percent for good,bad,total for the 3 populations
df_combined['cum_%_bad_dev'] = round(df_combined['cum_bad_dev']/df_combined.iloc[-1,0]*100,2)
df_combined['cum_%_bad_val'] = round(df_combined['cum_bad_val']/df_combined.iloc[-1,3]*100,2)
df_combined['cum_%_bad_all'] = round(df_combined['cum_bad_all']/df_combined.iloc[-1,6]*100,2)

df_combined['cum_%_good_dev'] = round(df_combined['cum_good_dev']/df_combined.iloc[-1,1]*100,2)
df_combined['cum_%_good_val'] = round(df_combined['cum_good_val']/df_combined.iloc[-1,4]*100,2)
df_combined['cum_%_good_all'] = round(df_combined['cum_good_all']/df_combined.iloc[-1,7]*100,2)

df_combined['cum_%_total_dev'] = round(df_combined['cum_total_dev']/df_combined.iloc[-1,2]*100,2)
df_combined['cum_%_total_val'] = round(df_combined['cum_total_val']/df_combined.iloc[-1,5]*100,2)
df_combined['cum_%_total_all'] = round(df_combined['cum_total_all']/df_combined.iloc[-1,8]*100,2)


# In[94]:


df_combined


# In[95]:


#Calculate the differences between the cumulative values for each row
df_combined['dev_val_cum_%diff_bad'] = abs(df_combined['cum_%_bad_dev'] - df_combined['cum_%_bad_val'])
df_combined['dev_all_cum_%diff_bad'] = abs(df_combined['cum_%_bad_dev'] - df_combined['cum_%_bad_all'])
df_combined['val_all_cum_%diff_bad'] = abs(df_combined['cum_%_bad_val'] - df_combined['cum_%_bad_all'])

df_combined['dev_val_cum_%diff_good'] = abs(df_combined['cum_%_good_dev'] - df_combined['cum_%_good_val'])
df_combined['dev_all_cum_%diff_good'] = abs(df_combined['cum_%_good_dev'] - df_combined['cum_%_good_all'])                                             
df_combined['val_all_cum_%diff_good'] = abs(df_combined['cum_%_good_val'] - df_combined['cum_%_good_all'])

df_combined['dev_val_cum_%diff_total'] = abs(df_combined['cum_%_total_dev'] - df_combined['cum_%_total_val'])
df_combined['dev_all_cum_%diff_total'] = abs(df_combined['cum_%_total_dev'] - df_combined['cum_%_total_all'])
df_combined['val_all_cum_%diff_total'] = abs(df_combined['cum_%_total_val'] - df_combined['cum_%_total_all'])


# In[96]:


df_combined


# You can read more about the KS test here:
# https://en.wikipedia.org/wiki/Kolmogorov%E2%80%93Smirnov_test .
# Take note of the formula for a two-sample KS test and the value of c(alpha) at 5% confidence interval.

# In[97]:


#Calculate the critical KS value for each set of population and good/bad/total.
#We will perform the test at 5% confidence interval
KS_dev_val_bad = round(1.358*np.sqrt((df_combined.iloc[-1,0] + df_combined.iloc[-1,3])/(df_combined.iloc[-1,0]*df_combined.iloc[-1,3]))*100,2)
KS_dev_all_bad = round(1.358*np.sqrt((df_combined.iloc[-1,0] + df_combined.iloc[-1,6])/(df_combined.iloc[-1,0]*df_combined.iloc[-1,6]))*100,2)
KS_val_all_bad = round(1.358*np.sqrt((df_combined.iloc[-1,3] + df_combined.iloc[-1,6])/(df_combined.iloc[-1,3]*df_combined.iloc[-1,6]))*100,2)

KS_dev_val_good = round(1.358*np.sqrt((df_combined.iloc[-1,1] + df_combined.iloc[-1,4])/(df_combined.iloc[-1,1]*df_combined.iloc[-1,4]))*100,2)
KS_dev_all_good = round(1.358*np.sqrt((df_combined.iloc[-1,1] + df_combined.iloc[-1,7])/(df_combined.iloc[-1,1]*df_combined.iloc[-1,7]))*100,2)
KS_val_all_good = round(1.358*np.sqrt((df_combined.iloc[-1,4] + df_combined.iloc[-1,7])/(df_combined.iloc[-1,4]*df_combined.iloc[-1,7]))*100,2)

KS_dev_val_total = round(1.358*np.sqrt((df_combined.iloc[-1,2] + df_combined.iloc[-1,5])/(df_combined.iloc[-1,2]*df_combined.iloc[-1,5]))*100,2)
KS_dev_all_total = round(1.358*np.sqrt((df_combined.iloc[-1,2] + df_combined.iloc[-1,8])/(df_combined.iloc[-1,2]*df_combined.iloc[-1,8]))*100,2)
KS_val_all_total = round(1.358*np.sqrt((df_combined.iloc[-1,5] + df_combined.iloc[-1,8])/(df_combined.iloc[-1,5]*df_combined.iloc[-1,8]))*100,2)


# In[98]:


#Define the sets of values that are going to be compared. 
#E.g. The maximum difference between bad accounts in the Development and Validation samples will be compared 
#     to the critical value calculated in KS_dev_val_bad 
test = {'dev_val_cum_%diff_bad': KS_dev_val_bad,
        'dev_all_cum_%diff_bad': KS_dev_all_bad,
        'val_all_cum_%diff_bad': KS_val_all_bad, 
        
        'dev_val_cum_%diff_good':KS_dev_val_good, 
        'dev_all_cum_%diff_good': KS_dev_all_good, 
        'val_all_cum_%diff_good': KS_val_all_good,
        
        'dev_val_cum_%diff_total': KS_dev_val_total, 
        'dev_all_cum_%diff_total':KS_dev_all_total, 
        'val_all_cum_%diff_total':KS_val_all_total}


# In[99]:


#Carry out the comparison by taking the maximum difference and comparing it to the critical value
#If the maximum difference is lower than the critical value, that means that the distributions are not statistically different
#    and the model validates successfully
#All 9 points of comparison must validate in order to confirm that the model is valid as a whole

validation = {}
for key, value in test.items():
    if df_combined[key].max() < value:
        validation[key] = 'Valid'
    else:
        validation[key] = 'Invalid'  


# In[100]:


for key, value in validation.items():
    print(f'{key} is {value}!')


# There are two tests that fail which means that the difference in the distributions is statistically significant and the model will not perform as well on new data as it does on the development population. 
# If a model is not valid / is not expected to perform well on new data, we can:
# 
# - Change the classing in one or more variables
# - Remove one or more variables from the model
# - Add one or more new variables to the model

# In addition to the example tests performed here, you are also encouraged to learn more about and calculate the Gini coefficient which will show how well the model predicts the outcome.
