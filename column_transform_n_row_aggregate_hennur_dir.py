# from IPython.core.display import display, HTML
# display(HTML("<style>.container { width:100% !important; }</style>"))


import os
import pandas as pd
import numpy as np

# basic processing and checking
members = pd.read_csv('members.csv')
print(members[~members.famid.isin(members[members.rltshp == "Self"].famid.unique())])
members = members[members.famid != 122] # removing Jayashree duplicate

# ================================= Head of Family ==================================
mem = members.copy()
h = mem[mem.rltshp == "Self"][['famid', 'member_name', 'phone']].rename(columns={'member_name':'hof'})


# =================================== BIRTHDAYS =====================================
mem = members.copy()
# dup_count = mem.member_name.value_counts() 
# mem[mem.member_name.isin(dup_count[dup_count != 1].index.unique())]
mem = mem[~mem.dob.isin([" ", np.NaN])]
dob = pd.merge(left = mem[['famid', 'member_name', 'dob']], right=h[['famid', 'hof']], on='famid')[['famid', 'member_name', 'hof', 'dob']]
dmy = dob.dob.str.split('/', n=3, expand = True).rename(columns={i: j for i, j in zip(range(3), ['date', 'month', 'year'])}).astype('int')
dob = pd.concat([dob, dmy], axis=1)

# ================================= ANNIVERSARIES ===================================
mem = members.copy()
mem= mem[~mem.dom.isin([" ", np.NaN])] # removing records with no DOM

couples_col = mem.groupby(['famid'])['member_name'].transform(lambda x : ' & '.join(x)).to_frame().rename(columns={'member_name': 'couple'}) # couple column
c = pd.concat([couples_col,mem[['famid', 'member_name', 'dom']]], axis=1).drop_duplicates(subset=["couple"]).rename(columns={'member_name':'hof'}) # concat couple column with df

# getting date, month, year separately in columns by creating a new dataframe of dmy and concat with former dataframe
dmy = c.dom.str.split('/', n=3, expand = True).rename(columns={i: j for i, j in zip(range(3), ['date', 'month', 'year'])}).astype('int')
dom = pd.concat([c, dmy], axis=1)[['famid', 'couple', 'hof', 'dom', 'date', 'month', 'year']]

#--->>>> ADDRESS THE ISSUE OF MORE THAN 2 MEMBERNAMES IN single family ID

# ====================== MASTER - hof_phone_address =================================
ca = pd.read_csv("cur_addr.csv")
ca.fillna(' ', inplace=True)
# ca['pin'] = ca.pin.astype('str')
# ca.agg(lambda x: ','.join(x.values), axis=1).T
ca['address'] = ca[ca.columns[ca.columns != "famid"]].agg(lambda x: ', '.join([val for val in x.values if val != " "]), axis=1)
addr = ca[['famid', 'address']]
hof_with_address = pd.merge(left=h, right=addr, how='left', on="famid")

# -----------------------------------------------------------------------------------
# writing dataframes to excel different worksheets
writer = pd.ExcelWriter('directory_processed.xlsx', engine='openpyxl') 
dob.to_excel(writer, sheet_name="birthdays", index=False)
dom.to_excel(writer, sheet_name="Anniversarys", index=False)
hof_with_address.to_excel(writer, sheet_name="Master", index=False)
writer.save()
