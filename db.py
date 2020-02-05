from sqlalchemy import create_engine
import pandas as pd

class DataManager:
    def __init__(self):
        self.databases = ["GJ_20Sept",
                          "GJ_20Sept_17nov",
                          "GJ_20Sept_AB",
                          "GJ_20Sept_Carburant",
                          "GJ_20Sept_Frouges",
                          "GJ_20Sept_GDN",
                          "GJ_20Sept_NewHashtags",
                          "GJ_20Sept_more",
                          "GJ_Sept20_International"]

    def create_url_df(self):
        dataframes = []
        for db in self.databases:
            engine = create_engine("postgresql+psycopg2://" +
                                           "pg:LooPhahph9aciesa@cat-01.h.k39.us:5432/%s" % (db))
            df = pd.read_sql("SELECT natural_key, author_id, body " +
                             "FROM document " +
                             "WHERE document.language = 'fr' AND document.author_id IS NOT NULL " +
                             "AND document.body IS NOT NULL", engine)
            dataframes.append(df)
        res = pd.concat(dataframes)
        res.to_csv("data/df_url.csv", index=False, encoding='utf-8')

    def create_hashtag_df(self):
        dataframes = []
        for db in self.databases:
            engine = create_engine("postgresql+psycopg2://" +
                                               "pg:LooPhahph9aciesa@cat-01.h.k39.us:5432/%s" % (db))
            df = pd.read_sql("SELECT author_id, body, hashtag " +
                             "FROM document join document_hashtag on id = document_id " +
                             "WHERE document.language = 'fr' AND document.author_id IS NOT NULL " +
                             "AND document.body IS NOT NULL", engine)
            dataframes.append(df)
        res = pd.concat(dataframes)
        res.to_csv("data/df_hashtag.csv", index=False, encoding='utf-8')

    def create_created_at_df(self):
        dataframes = []
        for db in self.databases:
            engine = create_engine("postgresql+psycopg2://" +
                                               "pg:LooPhahph9aciesa@cat-01.h.k39.us:5432/%s" % (db))
            df = pd.read_sql("SELECT natural_key, author_id, publishing_date " +
                             "FROM document " +
                             "WHERE document.language = 'fr' AND document.author_id IS NOT NULL " +
                             "AND document.publishing_date IS NOT NULL ", engine)
            dataframes.append(df)
        res = pd.concat(dataframes)
        res.to_csv("data/df_created_at.csv", index=False, encoding='utf-8')

    def create_id_df(self):
        dataframes = []
        for db in self.databases:
            engine = create_engine("postgresql+psycopg2://" +
                                               "pg:LooPhahph9aciesa@cat-01.h.k39.us:5432/%s" % (db))
            df = pd.read_sql("SELECT natural_key, body " +
                             "FROM document " +
                             "WHERE document.language = 'fr' AND document.author_id IS NOT NULL " +
                             "AND document.publishing_date IS NOT NULL AND document.body IS NOT NULL ", engine)
            dataframes.append(df)
        res = pd.concat(dataframes)
        res.to_csv("data/df_id.csv", index=False, encoding='utf-8')
