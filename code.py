import pandas as pd
import numpy as np
from scipy.stats import ttest_ind

# Use this dictionary to map state names to two letter acronyms
states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}

def get_list_of_university_towns():
    '''Returns a DataFrame of towns and the states they are in from the 
    university_towns.txt list. The format of the DataFrame should be:
    DataFrame( [ ["Michigan", "Ann Arbor"], ["Michigan", "Yipsilanti"] ], 
    columns=["State", "RegionName"]  )
    
    The following cleaning needs to be done:

    1. For "State", removing characters from "[" to the end.
    2. For "RegionName", when applicable, removing every character from " (" to the end.
    3. Depending on how you read the data, you may need to remove newline character '\n'. '''
    
    unitowns = pd.read_table("university_towns.txt", header=None)
    RegionName = pd.Series(unitowns.iloc[:,0], name = 'RegionName')

    def is_state(string):
        return string[-6::] == '[edit]'

    def find_state(data):
        states = []
        for i in range(len(data)):
            j = i
            while not is_state(data[j]):
                j = j-1
            states.append(data[j])
        return states

    def clean(string):
        cleaned = ''
        for c in string:
            if c not in '[(':
                cleaned = cleaned + c
            else:
                if cleaned[-1] == ' ':
                    return cleaned[:-1]
                else:
                    return cleaned
        return cleaned

    states = find_state(RegionName)
    states = list(map(clean, states))
    RegionName = list(map(clean,RegionName))
    unitowns['State'] = states
    unitowns['RegionName'] = RegionName
    unitowns = unitowns.iloc[:,1:]
    unitowns = unitowns[unitowns['State'] != unitowns['RegionName']]
    return unitowns
#get_list_of_university_towns()


def get_recession_start():
    '''Returns the year and quarter of the recession start time as a 
    string value in a format such as 2005q3'''
    GDP = pd.read_excel("gdplev.xls", skiprows = 4, header = 1)
    GDP = GDP.iloc[2:, 4:7]
    GDP = GDP[GDP['Unnamed: 4']>='2000q1']
    for i in range(1,GDP.shape[0]-1):
        d1 = GDP.iloc[i-1,2] > GDP.iloc[i,2]
        d2 = GDP.iloc[i,2] > GDP.iloc[i+1,2]
        if d1 and d2:
            return GDP.iloc[i,0]
    return None
#get_recession_start()

def get_recession_end():
    '''Returns the year and quarter of the recession end time as a 
    string value in a format such as 2005q3'''
    GDP = pd.read_excel("gdplev.xls", skiprows = 4, header = 1)
    GDP = GDP.iloc[2:, 4:7]
    GDP = GDP[GDP['Unnamed: 4']>='2000q1']
    for i in range(2, GDP.shape[0]):
        i1 = GDP.iloc[i-2,2] < GDP.iloc[i-1,2]
        i2 = GDP.iloc[i-1,2] < GDP.iloc[i,2]
        if i1 and i2 and GDP.iloc[i,0] > get_recession_start():
            return GDP.iloc[i,0]
    return None
get_recession_end()

def get_recession_bottom():
    '''Returns the year and quarter of the recession bottom time as a 
    string value in a format such as 2005q3'''
    GDP = pd.read_excel("gdplev.xls", skiprows = 4, header = 1)
    GDP = GDP.iloc[2:, 4:7]
    GDP = GDP[GDP['Unnamed: 4']>='2000q1']
    start = get_recession_start()
    end = get_recession_end()
    recession = GDP[(GDP['Unnamed: 4'] >= start)]
    recession = recession[recession['Unnamed: 4'] <= end]
    recession.head()
    bottom = recession[recession.iloc[:,2] == min(recession.iloc[:,2])]
    return bottom.iloc[0,0]
get_recession_bottom()

def convert_housing_data_to_quarters():
    '''Converts the housing data to quarters and returns it as mean 
    values in a dataframe. This dataframe should be a dataframe with
    columns for 2000q1 through 2016q3, and should have a multi-index
    in the shape of ["State","RegionName"].
    
    Note: Quarters are defined in the assignment description, they are
    not arbitrary three month periods.
    
    The resulting dataframe should have 67 columns, and 10,730 rows.
    '''
    housing = pd.read_csv("City_Zhvi_AllHomes.csv")
    names = ['State', 'RegionName']
    dates = list(housing.columns[51:])
    for date in dates:
        names.append(date)
    housing = housing[names]
    
    def start_end(tcode):
        year = tcode[:4]
        q = tcode[-1]
        if q =='1':
            start = year+'-01'
            end = year+'-03'
        elif q =='2':
            start = year+'-04'
            end = year+'-06'
        elif q =='3':
            start = year+'-07'
            end = year+'-09'
        else:
            start = year+'-10'
            end = year+'-12'
        return start, end

    cols = list(housing.columns)
    new_housing = housing[['State','RegionName']]

    for year in range(2000, 2017):
        for q in range(1,5):
            if year == 2016 and q == 4:
                break
            tcode = str(year)+'q'+str(q)
            start, end = start_end(tcode)
            sel = [col for col in cols if col >= start and col <= end]
            if year == 2016 and q == 3:
                new_housing[tcode] = list(map(np.mean, zip(housing[sel[0]], housing[sel[1]])))
            else:
                new_housing[tcode] = list(map(np.mean, zip(housing[sel[0]], housing[sel[1]], housing[sel[2]])))
    new_housing['State'] = list(map(lambda x: states[x], new_housing['State']))
    new_housing = new_housing.set_index(['State','RegionName'])

    return new_housing

convert_housing_data_to_quarters()

def run_ttest():
    '''First creates new data showing the decline or growth of housing prices
    between the recession start and the recession bottom. Then runs a ttest
    comparing the university town values to the non-university towns values, 
    return whether the alternative hypothesis (that the two groups are the same)
    is true or not as well as the p-value of the confidence. 
    
    Return the tuple (different, p, better) where different=True if the t-test is
    True at a p<0.01 (we reject the null hypothesis), or different=False if 
    otherwise (we cannot reject the null hypothesis). The variable p should
    be equal to the exact p value returned from scipy.stats.ttest_ind(). The
    value for better should be either "university town" or "non-university town"
    depending on which has a lower mean price ratio (which is equivilent to a
    reduced market loss).'''
    
    new_housing = convert_housing_data_to_quarters()
    start = get_recession_start()
    bottom = get_recession_bottom()
    ratio = []
    for i in range(new_housing.shape[0]):
        ratio.append(new_housing[start][i]/new_housing[bottom][i])
    new_housing['ratio'] = ratio
    unitowns = get_list_of_university_towns()
    ratio_univ = []
    ratio_non_univ = []
    for i in range(new_housing.shape[0]):
        state, town = new_housing.iloc[i,:].name
        if town in list(unitowns[unitowns['State'] == states[state]]['RegionName']):
            ratio_univ.append(new_housing['ratio'][i])
        else:
            ratio_non_univ.append(new_housing['ratio'][i])
    T, p = ttest_ind(ratio_univ, ratio_non_univ, nan_policy='omit')
    difference = p < 0.01
    if T < 0:
        better = 'university town'
    else:
        better = 'non-university town'
    
    return (difference, p, better)

run_ttest()



