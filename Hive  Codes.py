
#Q2
#2.1 ##
>>SELECT * FROM NSEDATA WHERE SERIES != 'EQ';
>>hive -e "SELECT * FROM NSEDATA WHERE SERIES != 'EQ'" > 
>>/home/hduser/hive/savefiles/stockstats/q2_1.csv

#2.2 ##
>>CREATE TABLE STOCKSTATS(SYMBOL STRING,MIN float,MAX FLOAT,MEAN float,
                          STD FLOAT,YEAR STRING);

SELECT MIN(CLOSE),MAX(CLOSE),AVG(CLOSE),STDDEV_POP(CLOSE),
        from_unixtime(unix_timestamp(MYDATE,'dd-MMM-yyyy'),'yyyy') 
        as md FROM NSEDATA GROUP BY SYMBOL,
        from_unixtime(unix_timestamp(MYDATE,'dd-MMM-yyyy'),'yyyy') 
        ORDER BY SYMBOL, MD DESC; 

insert overwrite table stockstats SELECT SYMBOL, 
        MIN(CLOSE),MAX(CLOSE),AVG(CLOSE),STDDEV_POP(CLOSE),
        from_unixtime(unix_timestamp(MYDATE,'dd-MMM-yyyy'),'yyyy') 
        as md FROM NSEDATA GROUP BY SYMBOL,
        from_unixtime(unix_timestamp(MYDATE,'dd-MMM-yyyy'),'yyyy') 
        ORDER BY SYMBOL, MD DESC; 

mkdir stockstats;
INSERT OVERWRITE LOCAL DIRECTORY '/home/hduser/hive/savefiles/stockstats' 
        row format delimited fields terminated by ',' 
        select * from stockstats;

hive -e "select * from stockstats" > /home/hduser/hive/savefiles/q2_2.csv


#3 ##
#year 2014
TRADE QTY >3 LAKH AND YEAR = 2013
SELECT * FROM NSEDATA WHERE TOTTRDQTY >= 300000 AND
         from_unixtime(unix_timestamp(MYDATE,'dd-MMM-yyyy'),'yyyy') = '2013' 
         LIMIT 25;
         
hive -e "SELECT * FROM NSEDATA WHERE TOTTRDQTY >= 300000 AND
         from_unixtime(unix_timestamp(MYDATE,'dd-MMM-yyyy'),'yyyy') = '2013'
         LIMIT 25" > /home/hduser/hive/savefiles/q2_3_1.csv


#Q3.2 ##
#CREATING TABLE WITH ITSTOCK FOR YEAR 2013
create table ITSTOCK(symbol STRING, series STRING, open float, 
                     high float, low float, close float, 
                     last float, prevclose float, tottrdqty INT, 
                     tottrdval float, mydate STRING, isin STRING, 
                     colm STRING) row format delimited fields terminated 
                     by ',' stored as TEXTFILE;


#INSERTING VALUES INTO ITSTOCK
INSERT OVERWRITE TABLE ITSTOCK select * from nsedata where symbol in
                                 ('HCLTECH','NIITTECH','TATAELXSI','TCS',
                                  'INFY','WIPRO','DATAMATICS','TECHM','
                                  MINDTREE','OFSS') AND TOTTRDQTY>300000 
                                  AND SERIES = 'EQ' AND 
            from_unixtime(unix_timestamp(MYDATE,'dd-MMM-yyyy'),'yyyy') = '2013';
            
#CREATE FILE
hive -e "select * FROM ITSTOCK" > /home/hduser/hive/savefiles/q2_3_2.csv



#Q3.3
#CREATE TABLE ITSTOCKS SORTED WITH CROSS JOINS FOR CORR CALCULATION
create table itstocksorted(symbol1 string,close1 float,symbol2 string,
                           close2 float,mydate string);

#INSERT INTO ITSTOCKSSORTED
INSERT OVERWRITE TABLE ITSTOCKSORTED select t1.SYMBOL,t1.CLOSE,t2.symbol,t2.close,
        from_unixtime(unix_timestamp(t1.mydate,'dd-MMM-yyyy'),'yyyy-MMM-dd')
        as md from ITSTOCK t1 cross join ITSTOCK t2 where t2.symbol>t1.symbol and 
        t1.mydate=t2.mydate and t1.series = 'EQ' order by t1.symbol asc,t2.symbol
        asc,from_unixtime(unix_timestamp(md,'yyyy-MMM-dd'),'yyyy-MM-dd') asc;

#CREATE TABLE TO STORE CORRELATION VALUES
create table pearsoncoritstock(symbol1 string,symbol2 string, corr float);

#INSERT CORRELATION VALUES INTO TABLE CORR
  insert overwrite table pearsoncoritstock select symbol1,symbol2 ,
  (Avg(Close1*Close2)-(Avg(Close1)*Avg(Close2)))/(Stddev_pop(Close1)*Stddev_pop(Close2))
  as PearsonCoefficient from itstocksorted group by symbol1, symbol2 
  order by PearsonCoefficient desc;

#MAKE FILE
hive -e "SELECT * FROM pearsoncoritstock" > /home/hduser/hive/savefiles/q2_3_3.csv



#q4 ##
import pandas as pd

df = pd.read_csv(r"C:\Users\Asus\Desktop\q2_2.csv",sep='\t')
df.columns = ['SYMBOL','MIN','MAX','AVG','STDEV','YEAR']

dfcor = pd.read_csv(r"C:\Users\Asus\Desktop\q2_3_3.csv",sep='\t',header=None)

l = []
lrate = []
for i in dfcor.iloc[:,0]:
    avg2011 = int(df[(df['SYMBOL'] == i) & (df['YEAR'] == 2011)]['AVG'])
    avg2013 = int(df[(df['SYMBOL'] == i) & (df['YEAR'] == 2013)]['AVG'])
    l.append(((avg2013-avg2011)/avg2011)*100)
    lrate.append()

dfcor.insert(1,'5',l)

dfcor.columns = ['SYMBOL1','%GROWTH',"SYMBOL2",'CORR_BW_S1andS2']

dfcor[dfcor['%GROWTH'] > 50].sort_values('%GROWTH')['SYMBOL1'].unique()
#Out[91]: array(['TCS', 'TECHM', 'HCLTECH', 'MINDTREE'], dtype=object)
#This list is in ascending order of GROWTH

dfcor[dfcor['%GROWTH'] > 50]
dfnse = pd.read_csv(r"C:\Users\Asus\Desktop\all.csv",
                    usecols=[0,1,2,3,4,5,6,7,8,9,10])

#LIST OF STOCKS THAT I WILL BUY
lbuy = ['MINDTREE','TCS','INFY','OFSS','TECHM' , 'HCLTECH']

lbuy2014JAN = []
lbuy2014DEC = []

for i in lbuy:
    jan2014 = int(dfnse[(dfnse['SYMBOL']==i) & 
                        (dfnse['TIMESTAMP'] == '01-JAN-2014')]['CLOSE'])
    
    dec2014 = int(dfnse[(dfnse['SYMBOL']==i) & 
                        (dfnse['TIMESTAMP'] == '01-DEC-2014')]['CLOSE'])
    lbuy2014JAN.append(jan2014)
    lbuy2014DEC.append(dec2014)

lbuy
#Out[115]: ['MINDTREE', 'TCS', 'INFY', 'OFSS', 'TECHM', 'HCLTECH']


lbuy2014JAN
#Out[116]: [1549, 2153, 3468, 3274, 1828, 1258]

lbuy2014DEC
#Out[117]: [1244, 2692, 4349, 3444, 2653, 1671]






