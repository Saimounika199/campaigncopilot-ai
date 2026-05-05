import psycopg2

conn = psycopg2.connect(
    dbname="campaigncopilot",
    user="saimounika",
    port=5433
)

print("connected successfully")
conn.close()
