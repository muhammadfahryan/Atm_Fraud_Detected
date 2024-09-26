SET 'auto.offset.reset'='earliest';


------------- stream pertama
CREATE STREAM ATM_TXNS (
              account_id     VARCHAR, 
              atm            VARCHAR, 
              location       MAP<STRING, DOUBLE>,
              amount         INT, 
              timestamp      VARCHAR, 
              transaction_id VARCHAR) 
         WITH (
              KAFKA_TOPIC='ATM_TRANSACTION', 
              VALUE_FORMAT='AVRO', 
              TIMESTAMP='timestamp', 
              TIMESTAMP_FORMAT='yyyy-MM-dd HH:mm:ss X');

------ Query Check 
SELECT TIMESTAMPTOSTRING(ROWTIME, 'yyyy-MM-dd HH:mm:ss Z'), timestamp FROM ATM_TXNS;


----- Qeury Persisntent (Stream kedua)
CREATE STREAM ATM_TRANSACTION_02 WITH (PARTITIONS=3) AS SELECT * FROM ATM_TXNS;

----- Query Final Result JSON (Stream ketiga)
# ngecek account id 
CREATE STREAM ATM_FRAUD_DETECTED AS
SELECT 
  T1.ROWTIME AS T1_TIMESTAMP, 
  T2.ROWTIME AS T2_TIMESTAMP, 
  GEO_DISTANCE(
    T1.location['lat'], 
    T1.location['lon'], 
    T2.location['lat'], 
    T2.location['lon'], 
    'KM'
  ) AS DISTANCE_BETWEEN_TXN_KM, 
  (T2.ROWTIME - T1.ROWTIME) AS MILLISECONDS_DIFFERENCE, 
  (
    CAST(T2.ROWTIME AS DOUBLE) - CAST(T1.ROWTIME AS DOUBLE)
  ) / 1000 / 60 AS MINUTES_DIFFERENCE, 
  GEO_DISTANCE(
    T1.location['lat'], 
    T1.location['lon'], 
    T2.location['lat'], 
    T2.location['lon'], 
    'KM'
  ) / (
    (
      CAST(T2.ROWTIME AS DOUBLE) - CAST(T1.ROWTIME AS DOUBLE)
    ) / 1000 / 60 / 60
  ) AS KMH_REQUIRED, 
  T1.ACCOUNT_ID AS T1_ACCOUNT_ID, 
  T2.ACCOUNT_ID AS T2_ACCOUNT_ID, 
  T1.TRANSACTION_ID AS T1_TRANSACTION_ID, 
  T2.TRANSACTION_ID AS T2_TRANSACTION_ID, 
  T1.AMOUNT AS T1_AMOUNT, 
  T2.AMOUNT AS T2_AMOUNT, 
  T1.ATM AS T1_ATM, 
  T2.ATM AS T2_ATM, 
  CAST(T1.location['lat'] AS STRING) + ',' + CAST(T1.location['lon'] AS STRING) AS T1_LOCATION, 
  CAST(T2.location['lat'] AS STRING) + ',' + CAST(T2.location['lon'] AS STRING) AS T2_LOCATION 
FROM 
  ATM_TXNS T1 
  INNER JOIN ATM_TRANSACTION_02 T2 WITHIN (0 MINUTES, 5 MINUTES) 
  GRACE PERIOD 1 MINUTES
  ON T1.ACCOUNT_ID = T2.ACCOUNT_ID 
WHERE 
  T1.TRANSACTION_ID != T2.TRANSACTION_ID 
  AND (
    T1.location['lat'] != T2.location['lat'] 
    OR T1.location['lon'] != T2.location['lon']
  ) 
  AND T2.ROWTIME != T1.ROWTIME;




SELECT T1_ACCOUNT_ID,T2_ACCOUNT_ID,
TIMESTAMPTOSTRING(T1_TIMESTAMP, 'yyyy-MM-dd HH:mm:ss'), TIMESTAMPTOSTRING(T2_TIMESTAMP, 'HH:mm:ss'),
T1_ATM, T2_ATM, DISTANCE_BETWEEN_TXN_KM, MINUTES_DIFFERENCE
FROM ATM_FRAUD_DETECTED EMIT CHANGES;


PUT /atm_fraud_detected
{
  "mappings": {
    "properties": {
      "T1_LOCATION": {
        "type": "geo_point"
      },
      "T2_LOCATION": {
        "type": "geo_point"
      }
    }
  }
}