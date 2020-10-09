import os
import numpy as np
import pandas as pd
import sqlite3
import re
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.types import Integer, Text, String, DateTime
from models import BranchProduct, Product

pd.set_option('display.max_columns', None)

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
ASSETS_DIR = os.path.join(PROJECT_DIR, "assets")
PRODUCTS_PATH = os.path.join(ASSETS_DIR, "PRODUCTS.csv")
PRICES_STOCK_PATH = os.path.join(ASSETS_DIR, "PRICES-STOCK.csv")
DB_PATH = os.path.join(PROJECT_DIR, "db.sqlite")
STORE_NAME = "Richart's"
INTEREST_BRANCHES = ['RHSM', 'MM']

def process_csv_files():

    products_df = pd.read_csv(filepath_or_buffer=PRODUCTS_PATH, sep="|",)
    prices_stock_df = pd.read_csv(filepath_or_buffer=PRICES_STOCK_PATH, sep="|",)

    #filtra los items con stock mayor a 0 y los itmes en las Branch's de interes
    products_stock_greater_zero = prices_stock_df[prices_stock_df.STOCK > 0]
    prducts_in_interest_branches_df = products_stock_greater_zero[products_stock_greater_zero.BRANCH.isin(INTEREST_BRANCHES)]

    #filtra los productos que tienen stock en los branches de interes
    interest_products_SKU = prducts_in_interest_branches_df['SKU'].to_list()
    interest_products = products_df[products_df.SKU.isin(interest_products_SKU)]

    #remove columns that we dont need
    del interest_products['DESCRIPTION_STATUS']
    del interest_products['ORGANIC_ITEM']
    del interest_products['KIRLAND_ITEM']
    del interest_products['FINELINE_NUMBER']

    #remove html tags from description
    def remove_tags(string):
        result = re.sub('<.*?>','',string)
        return result

    DESCRIPTION=interest_products['DESCRIPTION'].apply(lambda cw : remove_tags(cw))
    interest_products['DESCRIPTION']=DESCRIPTION
    interest_products['package'] = None

    # Takes the package info to a package column, could still be improved for rare cases, bot works fine for most of them
    def separete_package(string):
        try:
            GRS = interest_products[interest_products['DESCRIPTION'].str.endswith(string)]['DESCRIPTION']
            GRS = GRS.str.rsplit(' ', 2)
            package = GRS.str[1] + ' ' + GRS.str[2]
            DESCRIPTION = GRS.str[0]
            index = interest_products[interest_products['DESCRIPTION'].str.endswith(string)].index
            interest_products.loc[index, 'DESCRIPTION'] = DESCRIPTION
            interest_products.loc[index, 'package'] = package
        except:
            pass


    def separete_package_2(string):
        try:
            ML = interest_products[interest_products['DESCRIPTION'].str.endswith(string)]['DESCRIPTION']
            ML = ML.str.rsplit(' ', 1)
            package = ML.str[1]
            DESCRIPTION = ML.str[0]
            index = interest_products[interest_products['DESCRIPTION'].str.endswith(string)].index
            interest_products.loc[index, 'DESCRIPTION'] = DESCRIPTION
            interest_products.loc[index, 'package'] = package
        except:
            pass


    Packages_kind_1 = [' GRS', ' ML.',' ML', ' KG',' KG.', ' PZA', ' PZA.', ' CC', ' CC.', ' UN', ' UN.', ' LT', ' LT.', ' GAL', ' GAL.', ' GR']
    for w in Packages_kind_1:
        separete_package(w)

    Packages_kind_2 = ['GRS', 'ML.','ML', 'KG','KG.', 'PZA', 'PZA.', 'CC', 'CC.', 'UN', 'UN.', 'LT', 'LT.', 'GAL', 'GAL.' , 'GR']
    for w in Packages_kind_2:
        separete_package_2(w)

    # print(interest_products['DESCRIPTION'])
    # print(interest_products['package'])

    #add column store filled with the name of the store
    interest_products['store'] = 'Richarts'

    #combine columns of category
    interest_products['CATEGORY'] = interest_products['CATEGORY'] + ' | ' + interest_products['SUB_CATEGORY'] + ' | ' + interest_products['SUB_SUB_CATEGORY']
    del interest_products['SUB_CATEGORY']
    del interest_products['SUB_SUB_CATEGORY']
    del interest_products['BUY_UNIT']

    # Change columns name to match database

    prducts_in_interest_branches_df.rename(columns={
        'BRANCH': 'branch',
        'PRICE': 'price',
        'STOCK': 'stock',
        'SKU': 'sku',
    }, inplace=True)

    interest_products.rename(columns={
        'SKU': 'sku',
        'BARCODES': 'barcodes',
        'NAME': 'name',
        'DESCRIPTION': 'description',
        'IMAGE_URL': 'image_url',
        'CATEGORY': 'category',
        'BRAND': 'brand',
    }, inplace=True)

    print(interest_products)

    engine = create_engine("sqlite:///" + DB_PATH)
    print(engine.table_names())

    interest_products.to_sql(
        name='products',
        con=engine,
        index=False,
        if_exists='append',
    )
    prducts_in_interest_branches_df.to_sql(
        name='branchproducts',
        con=engine,
        index=False,
        if_exists='append'
    )

    if __name__ == "__main__":
        process_csv_files()
