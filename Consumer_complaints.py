# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.4.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# Data.gov
# Source: https://catalog.data.gov/dataset/consumer-complaint-database#topic=consumer_navigation

# # Purpose of analysis: 
# ### Determine which products consumers complaina bout the most, according to the Bureau of Consumer Financial Protection.
#
# ### Project type: Data cleaning & investigation

# +
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# %matplotlib inline



# +
"""  Used to see all rows of a data frame without permanently resetting maximum displayed rows."""

def print_full(x):
    pd.set_option('display.max_rows', len(x)) 
    print(x)
    pd.reset_option('display.max_rows')

def print_len(data, int):
    pd.set_option('display.max_rows', int)
    print(data)
    pd.reset_option('display.max_rows')


# -

complaints = pd.read_csv('Consumer_Complaints.csv')

print( len(complaints))
complaints.head()

# ## Clean Data (A):
# * Drop unnecessary columns. This analysis will focus on product/sub-products that received the most complaints,and the issue/sub-issue related to those products.
# * Rename columns for ease of use.
# * Convert dates to date_time type.
#
# [To Do:] Check for null values

# +
cols_dropped = ['Consumer complaint narrative', 'Company public response', 'Tags', 
                'Consumer consent provided?', 'Submitted via', 'Date sent to company', 'Timely response?', 
                'Complaint ID']

complaints.drop(cols_dropped, axis = 1, inplace = True)
# -

# Reference: https://www.dataquest.io/blog/pandas-cheat-sheet/
complaints.columns = ['date_received', 'product', 'sub_product', 
                      'issue', 'sub_issue', 
                      'company', 'state', 'zip', 
                      'comp_response_to_consumer',
                      'disputed']


complaints['date_received'] = pd.to_datetime(complaints['date_received'], format = '%m/%d/%Y') 


# ## Investigate Data (1)
# * Review column names and object types (all 'object' are strings, and therefore could require additional cleaning).
# * Identify number of products (18) and subproducts (77).
# * Identify most complained about products and subproducts.
#

print( complaints.info() )
print( '\n')
print( complaints.dtypes)

# +
""" Check total number of products and sub-products. """

print("Products: ", len(complaints['product'].unique()))
print("Sub-products: ", len(complaints['sub_product'].unique() ))

# +
""" Display products sorted by # of complaints """
products = complaints['product'].value_counts()

print(complaints['product'].value_counts())
print('\n')

complaints['product'].value_counts().plot(kind='bar')

# +
""" Review all sub-products
Recall: print_full defined above, to display all rows """

print_full(complaints['sub_product'].value_counts())

# +
""" Check which products the 'I do not know' sub_product is most found in """

idk_bool = complaints['sub_product'] == 'I do not know' # Bool for all sub_products with "I do not know" as answer
print( complaints['product'][idk_bool].value_counts() )

""" Check what other sub_products exist within the 'Debt collection' product """
print( complaints['sub_product'][complaints['product'] == 'Debt collection'].value_counts())

# +
""" Check in which product categories the sub_product 'Other (i.e. phone, health club, etc.) exists.
Result: only in 'Debt collection'
"""

complaints[complaints['sub_product'] == 'Other (i.e. phone, health club, etc.)']['product'].value_counts()
# -

# ## Observations:
# * "I do not know" is the 5th most answered sub-product. All of these are part of the "debt collection" product.
# * There are two 'other' subproducts within the 'Debt collection' product. 
#
#
# Three other product categories have overlaps that must be re-sorted:
# * Credit card / credit card or prepaid card / prepaid card
# * Money transfers / money transfer, virtual currency, or money service / virtual currency
# * Payday loan / payday loan, title loan, orpersonal loan / consumer loan
#
# ## Clean Data (B):
# * Rename and consolidate 'I do not know' and 'Other (i.e.phone, health club, etc.)' sub_product into 'Other debt' within
#     the 'Debt collection' product.

# +
complaints['sub_product'] = complaints['sub_product'].str.replace('I do not know', 'Other debt')
complaints['sub_product'] = complaints['sub_product'].str.replace('Other (i.e. phone, health club, etc.)', 'Other debt', 
                                                                 regex = False) 

"""
Note: str.replace(regex = False) will treat the string being replace as a literal rather than a regex expression. 
Necessary to parse the parantheses in 'Other (i.e. phone, health club, etc.)', which would otherwise be
treated as capture groups.
see: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.str.replace.html 
"""

# Confirm subproducts have been renamed in 'Debt collection product'
print_full(complaints[complaints['product'] == 'Debt collection']['sub_product'].value_counts())
# -

# [SHOULD THIS GO SOMEWHERE ELSE?]
complaints.loc[complaints['product'] == 'Consumer Loan'] = 'Consumer loan' # for consistency's sake

# ## Clean Data (C):
# Rename & resort product categories for overlapping/redundant sub-category names 
#
# 1) Credit cards / prepaid cards / credit or prepaid cards
#
# 2) Money transfer / Virtual currency / Money transfer, virtual currency, or money service sub_products
#
# 3) Payday loan / consumer loan / Payday loan, title loan, or personal loan                                        
#

# ### Investigate product groups that have overlapping sub_product gruops:
# 1. Credit card or prepaid card / credit card / prepaid card
# 2. Money transfer, virtual currency, or money service / Money transfer / Virtual currency 
# 3. Payday, title or personal loan / Payday loan / consumer loan 
#

# +
""" 1. Credit card or prepaid card / credit card / prepaid card """

# Credit card or prepaid card
credit_or_prepaid_bool = complaints['product'] == 'Credit card or prepaid card'
credit_or_prepaid_cards = complaints[credit_or_prepaid_bool]
print("Credit or prepaid card sub_products:", 
      '\n', 
      credit_or_prepaid_cards['sub_product'].value_counts(),
     '\n')

# Credit cards
credit_card_bool = complaints['product'] == 'Credit card'
credit_cards = complaints[credit_card_bool]

print("Credit cards sub_products:", 
      '\n', 
      credit_cards['sub_product'].value_counts(),
     '\n')

# Prepaid cards
prepaid_bool = complaints['product'] == 'Prepaid card'
prepaid_cards = complaints[prepaid_bool]
print("Prepaid cards sub_products:",
      '\n',
      prepaid_cards['sub_product'].value_counts(),
      '\n')



# +
""" 2. Money transfer, virtual currency, or money service / Money transfer / Virtual currency  """

# Money transfer, virtual currency, or money service
mt_vc_ms_bool = complaints['product'] == 'Money transfer, virtual currency, or money service'
mt_vc_ms_subproducts = complaints[mt_vc_ms_bool]
print("Money transfer, virtual currency, or money service sub_products:", 
      '\n', 
      mt_vc_ms_subproducts['sub_product'].value_counts(),
     '\n')

# Money transfer
mt_bool = complaints['product'] == 'Money transfer'
mt_subproducts = complaints[mt_bool]
print("Money transfer sub_products:", 
      '\n', 
      mt_subproducts['sub_product'].value_counts(),
     '\n')

# Virtual currency
vc_bool = complaints['product'] == 'Virtual currency'
vc_subproducts = complaints[vc_bool]
print("Virtual currency sub_products:", 
      '\n', 
      vc_subproducts['sub_product'].value_counts(),
     '\n')

# +
""" 3. Payday, title or personal loan / Payday loan / consumer loan """

# Payday loan, title loan, or personal loan                                        
pl_tl_pl_bool = complaints['product'] == 'Payday loan, title loan, or personal loan'
pl_tl_pl_subproducts = complaints[pl_tl_pl_bool]
print("Payday loan, title loan, or personal sub_products:", 
      '\n', 
      pl_tl_pl_subproducts['sub_product'].value_counts(),
     '\n')

# Payday loan
pl_bool = complaints['product'] == 'Payday loan'
pl_subproducts = complaints[pl_bool]
print("Payday loan sub_products:", 
      '\n', 
      pl_subproducts['sub_product'].value_counts(),
     '\n')

# Consumer loan 
cl_bool = complaints['product'] == 'Consumer loan'
cl_subproducts = complaints[cl_bool]
print("Consumer loan sub_products:", 
      '\n', 
      cl_subproducts['sub_product'].value_counts(),
     '\n')

# -

# ### Resort overlapping product and sub_product categories

# +
""" 
Initially, ran into issues with settingiwthcopywarning in this cell, due to chained indexing.
Accurate syntax for fixing this was found at: https://www.dataquest.io/blog/settingwithcopywarning/
"""

""" Resort 'Credit card or prepaid card' product group into either 'credit card' or 'prepaid card' """
# Resort the following into 'Credit card' product
complaints.loc[complaints['sub_product'] == 'General-purpose credit card or charge card', 'product'] = 'Credit card'
complaints.loc[complaints['sub_product'] == 'Store credit card', 'product'] = 'Credit card'

# Resort the following into 'Prepaid card' product group
complaints.loc[complaints['sub_product'] == 'General-purpose prepaid card', 'product'] = 'Prepaid card'
complaints.loc[complaints['sub_product'] == 'Government benefit card', 'product'] = 'Prepaid card'
complaints.loc[complaints['sub_product'] == 'Payroll card', 'product'] = 'Prepaid card'
complaints.loc[complaints['sub_product'] == 'Gift card', 'product'] = 'Prepaid card'
complaints.loc[complaints['sub_product'] == 'Student prepaid card', 'product'] = 'Prepaid card'



# -

complaints.loc[complaints['sub_product'] == 'Virtual currency', 'product'].value_counts()

complaints.loc[complaints['product'] == 'Virtual currency', 'sub_product'].value_counts()

# ### Observations:
# * All "Virtual currency" products have a sub_product that fits more appropriately in a "Money Transfer" product
# * All "Virtual currency" sub_products currently fall within the "Money transfer, Virtual currency, or money service" product

# +
""" Re-sort Money transfers, virtual currency, or money service / money transfers / virtual currency """

# All 'virtual currency' sub_product sorted into the 'virtual currency' product group
complaints.loc[complaints['sub_product'] == 'Virtual currency', 'product'] = 'Virtual currency'
complaints.loc[complaints['sub_product'] == 'Mobile or digital wallet', 'product'] = 'Virtual currency'

# All 'Money transfers', which originally were in 'Virtual currency' product group, 
# sorted into 'Money transfer' product group
complaints.loc[complaints['sub_product'] == 'Domestic (US) money transfer', 'product'] = 'Money transfers'
complaints.loc[complaints['sub_product'] == 'International money transfer', 'product'] = 'Money transfers'
complaints.loc[complaints['sub_product'] == 'Foreign currency exchange', 'product'] = 'Money transfers'


# Rename trimmed product group 
complaints.loc[complaints['product'] == 'Money transfer, virtual currency, or money service', 'product'] = 'Money service'



# +
""" Re-sort Payday, title, personal loans / payday loans / consumer loans """

# Payday loans
complaints.loc[(complaints['sub_product'] == 'Payday loan') &  
               (complaints['product'] == 'Payday loan, title loan, or personal loan'), 'product'] = 'Payday loan'

# Consumer loans
complaints.loc[(complaints['sub_product'] == 'Personal line of credit') &  
               (complaints['product'] == 'Payday loan, title loan, or personal loan'), 'product'] = 'Consumer loan'

complaints.loc[(complaints['sub_product'] == 'Installment loan') &  
               (complaints['product'] == 'Payday loan, title loan, or personal loan'), 'product'] = 'Consumer loan'

complaints.loc[(complaints['sub_product'] == 'Title loan') &  
               (complaints['product'] == 'Payday loan, title loan, or personal loan'), 'product'] = 'Consumer loan'

complaints.loc[(complaints['sub_product'] == 'Pawn loan') &  
               (complaints['product'] == 'Payday loan, title loan, or personal loan'), 'product'] = 'Consumer loan'


# +
""" Shorten credit reporting product category name"""

complaints.loc[complaints['product'] == 'Credit reporting, credit repair services, or other personal consumer reports', 
               'product'] = 'Credit reporting'

# +
""" Review revised product/sub_category groups """


print ('Credit card: ', '\n', complaints.loc[complaints['product'] == 'Credit card', 'sub_product'].value_counts() )
print('\n')
print ('Prepaid card: ', '\n', complaints.loc[complaints['product'] == 'Prepaid card', 'sub_product'].value_counts() )
print('\n')
print ('Virtual currency: ', '\n', complaints.loc[complaints['product'] == 'Virtual currency', 'sub_product'].value_counts() )
print('\n')
print ('Money transfers: ', '\n', complaints.loc[complaints['product'] == 'Money transfers', 'sub_product'].value_counts() )
print('\n')
print ('Money service: ', '\n', complaints.loc[complaints['product'] == 'Money service', 'sub_product'].value_counts() )
print('\n')
print ('Payday loan: ', '\n', complaints.loc[complaints['product'] == 'Payday loan', 'sub_product'].value_counts() )
print('\n')
print ('Consumer loan: ', '\n', complaints.loc[complaints['product'] == 'Consumer loan', 'sub_product'].value_counts() )
print('\n')
print('Products: ', '\n', complaints['product'].value_counts())
# -

# ## Prepare data for presentation
# * Create container variables for sub_products for easy comparison & graphic creation.
# * Add % columns to product and sub_product dataframes for graphics.

# +
""" Create variables containing sub_products of each product """

credit_reporting_bool = complaints['product'] == 'Credit reporting'
credit_rep_subproducts = complaints[credit_reporting_bool]['sub_product'].value_counts()

mortgage_bool = complaints['product'] == 'Mortgage'
mortgage_subproducts = complaints[mortgage_bool]['sub_product'].value_counts()

debt_col_bool = complaints['product'] == 'Debt collection'
debt_col_subproducts = complaints[debt_col_bool]['sub_product'].value_counts()

credit_card_bool = complaints['product'] == 'Credit card'
credit_card_subproducts = complaints[credit_card_bool]['sub_product'].value_counts

bank_account_bool = complaints['product'] == 'Bank account or service'
bank_account_subproducts = complaints[bank_account_bool]['sub_product'].value_counts

student_loan_bool = complaints['product'] == 'Studen loan'
studen_loan_subproducts = complaints[student_loan_bool]['sub_product'].value_counts()

checking_savings_bool = complaints['product'] == 'Checking or savings account'
checking_savings_subproducts = complaints[checking_savings_bool]['sub_product'].value_counts()

consumer_loan_bool = complaints['product'] == 'Consumer Loan'
consumer_loan_subproducts = complaints[consumer_loan_bool]['sub_product'].value_counts()

vehicle_loan_bool = complaints['product'] == 'Vehicle loan or lease'
vehicle_loan_subproducts = complaints[vehicle_loan_bool]['sub_product'].value_counts()

mt_bool = complaints['product'] == 'Money transfers'
mt_subproducts = complaints[mt_bool]['sub_product'].value_counts()

payday_bool = complaints['product'] == 'Payday loan'
payday_subproducts = complaints[payday_bool]['sub_product'].value_counts()

prepaid_bool = complaints['product'] == 'Prepaid card'
prepaid_subproducts = complaints[prepaid_bool]['sub_product'].value_counts()

vc_bool = complaints['product'] == 'Virtual currency'
vc_subproducts = complaints[vc_bool]['sub_product'].value_counts()

ms_bool = complaints['product'] == 'Money service'
ms_subproducts = complaints[ms_bool]['sub_product'].value_counts()


mt_bool = complaints['product'] == 'Money transfers'
mt_subproducts = complaints[mt_bool]['sub_product'].value_counts()


other_bool = complaints['product'] == 'Other financial service'
other_subproducts = complaints[other_bool]['sub_product'].value_counts()






# +
products = complaints['product'].value_counts()
products = products.to_frame() # Otherwise 'products' is a series and additional column cannot be added

# Calculate number of complaints by % of total and add as separate column
products.columns = ['num_complaints']
products['perc_total'] = products['num_complaints']/sum(products['num_complaints'])

print(products)
print(sum(products['perc_total'])) # Check sum to 100%

# +
sub_products = complaints['sub_product'].value_counts()
sub_products = sub_products.to_frame() # Otherwise sub_products is a series and additional column cannot be added

# Calculate number of complaints by % of total
sub_products.columns = ['num_complaints']
sub_products['perc_total'] = sub_products['num_complaints']/sum(sub_products['num_complaints'])

print(sub_products)
print(sum(sub_products['perc_total'])) # Check sum to 100%

# +
""" Review most complained about sub_products in top 5 product groups"""
print('Credit report', '\n', complaints.loc[complaints['product'] == 'Credit reporting', 'sub_product'].value_counts() )
print('\n')

print('Mortgage', '\n', complaints.loc[complaints['product'] == 'Mortgage', 'sub_product'].value_counts() )
print('\n')

print('Debt collection', '\n', complaints.loc[complaints['product'] == 'Debt collection', 'sub_product'].value_counts() )
print('\n')

print('Credit card', '\n', complaints.loc[complaints['product'] == 'Credit card', 'sub_product'].value_counts() )
print('\n')

print('Bank account or service', '\n', complaints.loc[complaints['product'] == 'Bank account or service', 'sub_product'].value_counts() )
print('\n')

# I wonder why complaints for fixed mortgages are twice as high as ARMs?
# Difficult to know with the "other mortgage" category.
# -

# ## Observations:
# * Not enough sub_product detail in mortgage to attempt to understand why there are more 2x nire complaints for fixed rather than ARM. Since "Conventional home" and "other mortgage" are broad subcategories without more detail, there can be substantial overlap between the two, and original dataset from gov didn't provide much clarification here.
#

# ## Conclusions & visualizations

# +
""" Instructions for visualization"""

prod_greater_5 = products[products['perc_total'] > 0.05]
prod_less_5 = products[products['perc_total'] < 0.05]
prod_greater_5_type = prod_greater_5.index.values

fig, ax = plt.subplots()
ax.bar(prod_greater_5_type, prod_greater_5['perc_total'], color=[246/255, 168/255, 78/255])

ax.spines["left"].set_visible(False)
ax.spines["bottom"].set_visible(False)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)


# Function definition from: https://stackoverflow.com/questions/28931224/adding-value-labels-on-a-matplotlib-bar-chart
def add_value_labels(ax, spacing=5):
    """Add labels to the end of each bar in a bar chart.

    Arguments:
        ax (matplotlib.axes.Axes): The matplotlib object containing the axes
            of the plot to annotate.
        spacing (int): The distance between the labels and the bars.
    """

    # For each bar: Place a label
    for rect in ax.patches:
        # Get X and Y placement of label from rect.
        y_value = rect.get_height()
        x_value = rect.get_x() + rect.get_width() / 2

        # Number of points between bar and label. Change to your liking.
        space = spacing
        # Vertical alignment for positive values
        va = 'bottom'

        # If value of bar is negative: Place label below bar
        if y_value < 0:
            # Invert space to place label below
            space *= -1
            # Vertically align label at top
            va = 'top'

        # Use Y value as label and format number with one decimal place
        label = "{:.0f}%".format(y_value*100)

        # Create annotation
        ax.annotate(
            label,                      # Use `label` as label
            (x_value, y_value),         # Place label at end of the bar
            xytext=(0, space),          # Vertically shift label by `space`
            textcoords="offset points", # Interpret `xytext` as offset in points
            ha='center',                # Horizontally center label
            va=va)                      # Vertically align label differently for
                                        # positive and negative values.


# Call the function above. All the magic happens there.
add_value_labels(ax)

# Turn off tick labels
# Source: https://stackoverflow.com/questions/37039685/hide-axis-values-in-matplotlib
ax.set_yticklabels([])


plt.yticks([])

plt.title('Top 5 most complained about products', fontweight = 'bold', ha = 'center', pad = 25)
plt.xticks(rotation = 90)


plt.show()
# -

credit_rep_subproducts.plot(kind='bar')

print( complaints.loc[complaints['product'] == 'Credit reporting', 'issue'].value_counts() )
print('\n')
print( complaints.loc[complaints['product'] == 'Credit reporting', 'sub_issue'].value_counts() )
print('\n')
print( complaints.loc[complaints['product'] == 'Mortgage', 'issue'].value_counts() )
print('\n')
print( complaints.loc[complaints['product'] == 'Debt collection', 'issue'].value_counts() )
print('\n')
print( complaints.loc[complaints['product'] == 'Credit card', 'issue'].value_counts() )
print('\n')
print( complaints.loc[complaints['product'] == 'Bank account or service', 'issue'].value_counts() )


# Investigate largest issues & sub_issues in credit reporting
print( complaints.loc[complaints['sub_issue'] == 'Information belongs to someone else', 'issue'].value_counts() )
print('\n')
print( complaints.loc[complaints['sub_issue'] == 'Information belongs to someone else', 'product'].value_counts() )
print('\n')
print( complaints.loc[complaints['issue'] == 'Incorrect information on your report', 'sub_issue'].value_counts() )
print('\n')
print( complaints.loc[complaints['issue'] == 'Incorrect information on credit report', 'sub_issue'].value_counts() )


# # Conclusions and observations:
#
# * Consumers complain the most about companies that they do not have a choice in patroning; that is, credit reporting companies.
# * The single largest issue consumers report to the CFPB is incorrect data on their credit report. Yet even when credit reporting companies make these types of errors, consumers do not have the option to opt out.
# * The lack of consumer choice is opting in or out of their data being collected by credit reporting companies likely plays in a role in why they are the most complained about company type in America.

# Possible Next steps:
# * Basemap to display state with most complaints? What types of companies are most complained about by state?
#
# Basemap sources:
# * Tutorial with zip codes: http://www.jtrive.com/visualizing-population-density-by-zip-code-with-basemap.html
# * https://basemaptutorial.readthedocs.io/en/latest/
# * https://readthedocs.org/projects/basemaptutorial/downloads/pdf/latest/
# * https://rabernat.github.io/research_computing/intro-to-basemap.html
# * https://geoexamples.com/python/2014/11/26/basemap-tutorial.html
#
#
