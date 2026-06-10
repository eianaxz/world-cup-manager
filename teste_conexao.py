from config.database import fetch_data

df = fetch_data("SHOW TABLES;")

print(df)

df = fetch_data("""
SELECT *
FROM selecoes
LIMIT 5;
""")

print(df)

df = fetch_data("""
SELECT * FROM jogadores;
""")

print(df)