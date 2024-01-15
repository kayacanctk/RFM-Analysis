import datetime as dt
import pandas as pd
pd.set_option('display.max_columns', None)#None ifadesi burada sütunların sınırlamasının olmadığını belirtir, onun yerine 10 yazsaydı ilk 10 sütun gözükürdü
pd.set_option('display.max_rows',None)
pd.set_option('display.float_format',lambda x: '%3f' %x) # Lambda ifadesi isimsiz bir fonksiyon tanımlar. x burada lambda fonksiyonunun parametresidir.
# "%" format belirleyiciyi başlatır. String içindeki değer tutuculara değer eklemek için kullanılır. %x ile x değeri içeri aktarılır.
df_ = pd.read_excel("/Users/VATAN/OneDrive/Masaüstü/online_retail_II.xlsx", sheet_name="Year 2009-2010")

#print(df.head())
#df.shape
#print(df.isnull().sum())
#print(df["Description"].value_counts().head())#description sütunundaki değerleri sayar.
#print(df.groupby("Description").agg({"Quantity":"sum"}).sort_values("Quantity",ascending=False).head())
#df["Invoice"].nunique()
#df["Total Price"] = df["Quantity"]*df["Price"]
#print(df.groupby("Invoice").agg({"Total Price":"sum"}).head())
#print(df[df["Invoice"].str.contains("C",na=False)])
#df.dropna(inplace=True)#bu işlem ile orijinal data frame üzerinde güncelleme yapılır null olan değerler  atılır.
#print(df["InvoiceDate"].max())
#today_date =dt.datetime(2010,12,11)
#rfm = df.groupby("Customer ID").agg({'InvoiceDate':lambda InvoiceDate:(today_date-InvoiceDate.max()).days ,
#                                     'Invoice': lambda Invoice : Invoice.nunique(),
#                                     'Total Price': lambda TotalPrice: TotalPrice.sum()})
#print(rfm.head())
#rfm.columns =["recency","frequency","monetary"]
#print(rfm.head())
def create_rfm(dataframe,csv=False):
    #VERİYİ HAZIRLAMA
    dataframe["TotalPrice"] = dataframe["Quantity"]*dataframe["Price"]
    dataframe.dropna(inplace=True)
    dataframe=dataframe[~dataframe["Invoice"].str.contains("C",na=False)]

    #RFM METRİKLERİNİN HESAPLANMASI
    #Öncesinde en son fatura tarihi belirlenir.
    today_date = dt.datetime(2011,12,11)
    rfm = dataframe.groupby("Customer ID").agg({"InvoiceDate":lambda InvoiceDate:(today_date-InvoiceDate.max()).days,#recency
                                                "Invoice":lambda Invoice:Invoice.nunique(),#frequency
                                                "TotalPrice":lambda TotalPrice:TotalPrice.sum(),#monetary
                                                })
    rfm.columns =["recency","frequency","monetary"]
    rfm = rfm[rfm("monetary">0)]
    
    #RFM SKORLARININ BEİRLENMESİ
    rfm["RECENCY_SCORE"] = pd.qcut(rfm["recency"],5,labels=[5,4,3,2,1])
    rfm["FREQUENCY_SCORE"] = pd.qcut(rfm["frequency"].rank(method="first"),5,labels=[1,2,3,4,5])
    rfm["MONETARY_SCORE"] = pd.qcut(rfm["monetary"],5,labels=[1,2,3,4,5])

    #cltv_df skorları kategorik df ye dönüştürülüp df ye eklendi
    rfm["RFM_SCORE"]=rfm["RECENCY_SCORE"].astype(str) + rfm["FREQUENCY_SCORE"].astype(str)#score değerleri birleştirildi

    #SEGMENTLERE AYRILMASI
    seg_map = {
        r'[1-2][1-2]': 'hibernating',
        r'[1-2][3-4]': 'at_risk',
        r'[1-2]5': 'cant_loose',
        r'3[1-2]': 'about_to_sleep',
        r'33': 'need_attention',
        r'[3-4][4-5]':'loyal_customer',
        r'41': 'promising',
        r'51': 'new_customers',
        r'[4-5][2-3]': 'potential_loyalists',
        r'5[4-5]':'champion'
    }

    rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map,regex=True)
    rfm = rfm[["recency","frequency","monetary","segment"]]
    rfm.index=rfm.index.astype(int)

    if csv:
        rfm.to_csv("rfm.csv")

    return rfm
df=df_.copy()
rfm_new=create_rfm(df,csv=True)
