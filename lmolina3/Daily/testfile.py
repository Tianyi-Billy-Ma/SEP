import pandas as pd 

# the path of XPT files in my computer 
file_path = "C:/Users/16822/OneDrive/Data Files for SER/2017_2020_NHANES.XPT"

# read_sas to load the data into a data frame 
df = pd.read_sas(file_path, format='xport')


# print the first six rows of the data frame and contine to the last row 
print(df.iloc[:,:6])
print(df.iloc[:, 7:13])
print(df.iloc[:,14:20])
print(df.iloc[:,21:26])
print(df.iloc[:,26:29])
# with open('c:\Users\16822\OneDrive\Data Files for SER\ACQ_G.XPT','rb') as f:
#     xpt_data = xport.load(f)


# df = xpt_data['ACQ_G.XPT']


# df.head(f)
