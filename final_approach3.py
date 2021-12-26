import pandas as pd
import numpy as np

#Functions

def frequency_group_table(df,start,end,interval):
    group=pd.cut(df.to_numpy(),bins=list(range(start,end+1,interval)),right=False).value_counts().to_frame()
    group.reset_index(level=0, inplace=True)
    group=group.rename(columns={"index": "group", 0: "frequency"})
    return group

def cum_freq_table(df):
    #Cum frequency from frequency
    df['cum_freq'] = df['frequency'].cumsum()
    #Add left and right boundary
    df['left_boundary']=df['group'].apply(lambda x: x.left)
    df['right_boundary']=df['group'].apply(lambda x: x.right)
    #Discarding the group with zero frequency to make calculation more easier
    df=df[df['frequency']!=0]
    return df

def ith_value_finder(percentile,N):
    return (percentile*N)/100

def percentile_calculator(cum_freq,ithvalue,interval): 
    
    '''
        Pj class = (jn/100)th value of the observation
        Pj=L+((jn/100)-cff/f)⋅i
        where, 
                n= no. of observation
                Pj= locate the jth percentile group.
                L= lower class boundary of the class containing the jth percentile
                cff = cumulative frequency of the class immediately preceding to the class containing Pj
                f= frequency of that group
                i= interval

    '''
    if len([d for d in cum_freq if d['cum_freq'] <= ithvalue])==0:
        cff=0
    else:
        cff=[d for d in cum_freq if d['cum_freq'] <= ithvalue][-1]['cum_freq']
    result=[d for d in cum_freq if d['cum_freq'] >= ithvalue][0]
    L=result['left_boundary']
    f=result['frequency']
    i=interval
    return round(L+((ithvalue-cff)/f)*i,2)

def percentile_main(cum_freq,interval,percentile,actual):
    result={}
    ithvalue=ith_value_finder(percentile,cum_freq['frequency'].sum())
    approx=percentile_calculator(cum_freq.to_dict('records'),ithvalue,interval)
    difference=round(abs(actual-approx),2)
    result['approx_percentile']=approx
    result['actual_percentile']=actual
    result['error_per']=error_per(actual,approx)
    result['difference']=difference
    return result

def error_per(actual,approx):
    '''
        Percentage Error:|Approximate Value − Actual Value|/Actual Value  × 100%

    '''
    return round(abs(approx-actual)/actual*100,2)
    



data= pd.read_csv('sampledata.csv')


#Config
percentile=99
interval=5
df_tobe_calculated=data['Sample1']
df_tobe_added=data['Delta1']

#For actual
combined_array=np.append(df_tobe_calculated.to_numpy(),df_tobe_added.to_numpy(), axis=0)
combined_array = combined_array[~np.isnan(combined_array)]

oldfreq=frequency_group_table(df_tobe_calculated,0,100,interval)
print(oldfreq)
newfreq=frequency_group_table(df_tobe_added,0,100,interval)
print(newfreq)
oldfreq['frequency']=oldfreq['frequency']+newfreq['frequency']
freq=oldfreq

#We need combined frequency to start our calculation
cum_freq=cum_freq_table(freq)
print(cum_freq)
actual=round(np.quantile(combined_array,percentile/100),2)
print(percentile_main(cum_freq,interval,percentile,actual))
