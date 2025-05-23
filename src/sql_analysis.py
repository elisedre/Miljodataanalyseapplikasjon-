import pandas as pd
import pandasql as psql
import matplotlib.pyplot as plt
import json
import seaborn as sns 

def analyze_hottest_days(df, date, temp, precip, n_days):
    """
    Analyserer de varmeste dagene basert på temperatur, visualiserer sammenhengen 
    med nedbør, og lager et kakediagram for å vise fordeling på år.

    Args:
        df (pd.DataFrame): DataFrame med værdata.
        date (str): Kolonnenavn for dato.
        temp (str): Kolonnenavn for temperatur.
        precip (str): Kolonnenavn for nedbør.
        n_days (int): Antall varmeste dager å analysere.
    
    Returns:
        pd.DataFrame: DataFrame med de varmeste dagene.
    """

    # SQL-spørring for å hente n varmeste dager 
    query = f"""
    SELECT *
    FROM df
    ORDER BY {temp} DESC
    LIMIT {n_days}
"""
    result = psql.sqldf(query, locals())

    # Visualisering med scatterplot av temp vs nedbør
    plt.figure(figsize=(6, 3))
    x = range(len(result))
    plt.scatter(x, result[temp], color='red', label=f'{temp} (°C)', s=100)
    plt.scatter(x, result[precip], color='blue', label=f'{precip} (mm)', s=100)
    plt.title(f'{temp} (°C) vs {precip} (mm) for de {n_days} Varmeste Dagene')
    plt.grid(True)
    plt.tight_layout()
    plt.show()


    # Kakediagram for å vise fordelingen av vamrme dager etter år 
    # Legger til en kolonne med år
    result['År'] = pd.to_datetime(result[date]).dt.year

    # Teller hvor mange ganger hvert år forekommer
    år_telling = result['År'].value_counts()

    plt.figure(figsize=(6, 6))
    plt.pie(
        år_telling,
        labels=år_telling.index,
        autopct='%1.1f%%',
        colors=plt.cm.Set3.colors 
    )
    plt.title(f"De {n_days} varmeste dagene fordelt på år")
    plt.axis('equal')
    plt.show()

    return result 

def analyze_frost_api_clean_data():
    """
    Leser inn rengjorte værdata fra frostAPI og kaller den generelle funksjonen "analyze_hottest_days
    for å analysere de varmeste dagene med hensyn på temperatur og nedbør. 

    Returns:
        pd.DataFrame: DataFrame med de varmeste dagene.
    """
   
    # Leser inn rengjort værdata fra frostAPI
    file_name = "../../data/clean_data/frostAPI_clean_data.json"  
    df = pd.read_json(file_name)
    # Kaller den generelle analysen med spesifikke kolonnenavn
    return analyze_hottest_days(df, date="Dato", temp="Temperatur", precip="Nedbør", n_days=10)



def analyze_coldest_days(df, date, temp, n_days):
    """
    Analyserer de kaldeste dagene i et datasett.

    Args:
        df (pd.DataFrame): DataFrame med værdata.
        date (str): Kolonnenavn for dato.
        temp (str): Kolonnenavn for temperatur.
        n_days (int): Antall kaldeste dager å analysere.
    
    Returns:
        pd.DataFrame: DataFrame med de kaldeste dagene og deres år.
    """
    
    # SQL-spørring for å finne de 10 dagene med lavest temperatur
    query = f"""
        SELECT {date}, {temp}
        FROM df 
        ORDER BY {temp} ASC 
        LIMIT {n_days}
    """
    result = psql.sqldf(query, locals())

    # Kakediagram for å vise fordelingen av de kaldeste dagene etter år
    # Legger til en kolonne med år
    result['År'] = pd.to_datetime(result[date]).dt.year

    # Teller hvor mange ganger hvert år forekommer blant de kaldeste dagene
    år_telling = result['År'].value_counts()


    plt.figure(figsize=(6, 6))
    plt.pie(
        år_telling,
        labels=år_telling.index,
        autopct='%1.1f%%',
        colors=plt.cm.Set3.colors 
    )
    plt.title(f"De {n_days} kaldeste dagene fordelt på år")
    plt.axis('equal')
    plt.show()

    return result 

def analyze_coldest_frost_api_data():
    """
    Leser inn værdata fra frostAPI og analyserer de kaldeste dagene ved å kalle 
    den generelle funksjonen "analyze_coldest_days".
    
    Returns:
        pd.DataFrame: DataFrame med de kaldeste dagene og deres år.
    """
    
    file_name = "../../data/clean_data/frostAPI_clean_data.json"
    df = pd.read_json(file_name)
    return analyze_coldest_days(df, date="Dato", temp="Temperatur", n_days=10)


def analyze_avg_temperature_per_year(df, date, temp):
    """
    Beregner gjennomsnittlig temperatur per år og visualiserer resultatet basert på en DataFrame med værdata.
    
    Args:
        df (pd.DataFrame): DataFrame med værdata.
        date (str): Kolonnenavn for dato.
        temp (str): Kolonnenavn for temperatur.
    
    Returns:
        result (pd.DataFrame): DataFrame med gjennomsnittlig temperatur per år.
    """
    
    # SQL-spørring for å finne gjennomsnittlig temperatur per år
    query = f"""
        SELECT strftime('%Y', {date}) AS År,
            AVG({temp}) AS Gjennomsnitt_temperatur
        FROM df
        GROUP BY År
        ORDER BY År
    """
    result = psql.sqldf(query, locals())

    # Visualisering av gjennomsnittlig temperatur per år
    plt.figure(figsize=(10, 5))
    plt.plot(result['År'], result['Gjennomsnitt_temperatur'], marker='o', color='blue', linestyle='-')
    plt.title("Gjennomsnittlig temperatur per år")
    plt.xlabel("År")
    plt.ylabel("Temperatur (°C)")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    return result 

def analyze_avg_temp_frost_api_data():
    """
    Leser inn rengjorte værdata fra frostAPI og analyserer gjennomsnittlig temperatur per år 
    ved å kalle den generelle funksjonen "analyze_avg_temperature_per_year".

    Returns: 
        result (pd.DataFrame): DataFrame med gjennomsnittlig temperatur per år.
    """
    
    file_name = "../../data/clean_data/frostAPI_clean_data.json"
    df = pd.read_json(file_name)
    return analyze_avg_temperature_per_year(df, date="Dato", temp="Temperatur")


def analyze_weekly_avg_data(df, date, precip, temp, wind):
    """
    Beregner og visualiserer ukentlig gjennomsnitt for nedbør, temperatur og vindhastighet basert på værdata.

    Args:
        df (pd.DataFrame): DataFrame med værdata.
        date (str): Kolonnenavn for dato.
        precip (str): Kolonnenavn for nedbør.
        temp (str): Kolonnenavn for temperatur.
        wind (str): Kolonnenavn for vindhastighet.
    
    Returns:
        pd.DataFrame: DataFrame med ukentlig gjennomsnitt for nedbør, temperatur og vindhastighet.
    """

    # Legger til en kolonne for uke
    df['Uke'] = pd.to_datetime(df[date]).dt.strftime('%Y-U%U')

    # SQL-spørring for å beregne gjennomsnitt per uke
    query = f"""
        SELECT
            Uke,
            AVG({precip}) AS Avg_Nedbør,
            AVG({temp}) AS Avg_Temperatur,
            AVG({wind}) AS Avg_Vindhastighet
        FROM df
        GROUP BY Uke
        ORDER BY Uke
    """
    result = psql.sqldf(query, locals())

    # Plotter resultatet 
    plt.figure(figsize=(14, 7))

    # Plot temperatur (rød)
    plt.plot(result['Uke'], result['Avg_Temperatur'], label='Temperatur (°C)', color='red', marker='o')
    # Plot nedbør (blå)
    plt.plot(result['Uke'], result['Avg_Nedbør'], label='Nedbør (mm)', color='blue', marker='s')
    # Plot vindhastighet (grønn)
    plt.plot(result['Uke'], result['Avg_Vindhastighet'], label='Vindhastighet (m/s)', color='green', marker='^')

    plt.xlabel('Uke')
    plt.ylabel('Gjennomsnitt per uke')
    plt.title('Gjennomsnittlig Nedbør, Temperatur og Vindhastighet per uke')
    plt.xticks(result['Uke'][::24], rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    return result

def analyze_weekly_avg_frost_api_data():
    """
    Leser inn rengjorte værdata fra frostAPI og analyserer ukentlig gjennomsnitt for nedbør, temperatur og vindhastighet 
    ved å kalle den generelle funksjonen "analyze_weekly_avg_data".

    Returns:
        pd.DataFrame: DataFrame med ukentlig gjennomsnitt for nedbør, temperatur og vindhastighet.
    """
    
    file_name = "../../data/clean_data/frostAPI_clean_data.json"
    df = pd.read_json(file_name)
    return analyze_weekly_avg_data(
        df,
        date="Dato",
        precip="Nedbør",
        temp="Temperatur",
        wind="Vindhastighet"
    )

def calculate_std_dev(df, col1, col2, col3):
    """
    Beregner standardavvik for tre kolonner i et datasett ved hjelp av SQL-spørring.

    Args:
        df (pd.DataFrame): DataFrame med værdata.
        col1 (str): Kolonnenavn for første kolonne.
        col2 (str): Kolonnenavn for andre kolonne.
        col3 (str): Kolonnenavn for tredje kolonne.
    
    Returns:
        pd.DataFrame: DataFrame med standardavvik for col1, col2 og col3.
    """

    # SQL-spørring for å beregne standardavvik for hele datasettet
    query = f"""
        SELECT
            SQRT(SUM(({col1} - (SELECT AVG({col1}) FROM df)) * 
                     ({col1} - (SELECT AVG({col1}) FROM df))) / 
                     (COUNT({col1}) - 1)) AS StdDev_{col1},
            SQRT(SUM(({col2} - (SELECT AVG({col2}) FROM df)) * 
                     ({col2} - (SELECT AVG({col2}) FROM df))) / 
                     (COUNT({col2}) - 1)) AS StdDev_{col2},
            SQRT(SUM(({col3} - (SELECT AVG({col3}) FROM df)) * 
                     ({col3} - (SELECT AVG({col3}) FROM df))) / 
                     (COUNT({col3}) - 1)) AS StdDev_{col3}
        FROM df
    """

    result = psql.sqldf(query, locals())
    return result

def calculate_std_frost_data():
    """
    Leser inn rengjorte værdata fra frostAPI og beregner standardavviket for nedbør, temperatur og vindhastighet 
    ved å kalle den generelle funskjonen "calculate_std_dev".

    Returns:
        pd.DataFrame: DataFrame med standardavvik for nedbør, temperatur og vindhastighet.
    """

    file_name = "../../data/clean_data/frostAPI_clean_data.json"  
    data = pd.read_json(file_name)
    df = pd.DataFrame(data)
    return calculate_std_dev(df, "Nedbør", "Temperatur", "Vindhastighet")


def calculate_weekly_std_dev(df, date, group, col1, col2, col3):
    """
    Beregner ukentlig standardavvik for tre kolonner i et datasett ved hjelp av SQL-spørring.

    Args:
        df (pd.DataFrame): DataFrame med værdata.
        date (str): Kolonnenavn for dato.
        group (str): Kolonnenavn for gruppe (f.eks. uke).
        col1 (str): Kolonnenavn for første kolonne.
        col2 (str): Kolonnenavn for andre kolonne.
        col3 (str): Kolonnenavn for tredje kolonne.

    Returns:
        pd.DataFrame: DataFrame med ukentlig standardavvik for col1, col2 og col3.
    """
           
    df[group] = pd.to_datetime(df[date]).dt.strftime('%Y-U%U')
    
    query = f"""
        SELECT
            {group},
            SQRT(SUM(({col1} - (SELECT AVG({col1}) FROM df WHERE {group} = df.{group})) * 
                      ({col1} - (SELECT AVG({col1}) FROM df WHERE {group} = df.{group}))) / 
                      (COUNT({col1}) - 1)) AS StdDev_{col1},
            SQRT(SUM(({col2} - (SELECT AVG({col2}) FROM df WHERE {group} = df.{group})) * 
                      ({col2} - (SELECT AVG({col2}) FROM df WHERE {group} = df.{group}))) / 
                      (COUNT({col2}) - 1)) AS StdDev_{col2},
            SQRT(SUM(({col3} - (SELECT AVG({col3}) FROM df WHERE {group} = df.{group})) * 
                      ({col3} - (SELECT AVG({col3}) FROM df WHERE {group} = df.{group}))) / 
                      (COUNT({col3}) - 1)) AS StdDev_{col3}
        FROM df
        GROUP BY {group}
        ORDER BY {group}
    """
    result = psql.sqldf(query, locals())
    return result

def calculate_std_frost_weekly():
    """
    Leser inn rengjorte værdata fra frostAPI og beregner ukentlig standardavvik for nedbør, temperatur og vindhastighet 
    ved å kalle den generelle funksjonen "calculate_weekly_std_dev".
    
    Returns:
        pd.DataFrame: DataFrame med ukentlig standardavvik for nedbør, temperatur og vindhastighet.
    """
    file_name = "../../data/clean_data/frostAPI_clean_data.json"  
    data = pd.read_json(file_name)
    df = pd.DataFrame(data)
    
    return calculate_weekly_std_dev(
        df,
        date="Dato",
        group="Uke",
        col1="Nedbør",
        col2="Temperatur",
        col3="Vindhastighet"
    )

def analyze_correlation_between_weather_and_air_quality(
        df1, df2, date, weather1, airquality1, weather2, airquality2
):
    """
    Fletter sammen vær- og luftkvalitetsdata på dato, og analyserer Pearson-korrelasjonen mellom to par av variabler.
    Resultatene visualiseres med scatter plots og korrelasjonskoeffisientene beregnes.

    Args:
        df1 (pd.DataFrame): DataFrame med værdata.
        df2 (pd.DataFrame): DataFrame med luftkvalitetsdata.
        date (str): Kolonnenavn for dato.
        weather1 (str): Kolonnenavn for første værparameter.
        airquality1 (str): Kolonnenavn for første luftkvalitetsparameter.
        weather2 (str): Kolonnenavn for andre værparameter.
        airquality2 (str): Kolonnenavn for andre luftkvalitetsparameter.
    
    Returns:
        tuple: Resultater fra SQL-spørringer og korrelasjonsberegninger.
    """
    
    # Merge DataFrames på dato
    merged_df = pd.merge(df1, df2, on=date, how="inner")  

    # SQL-spørring for å undersøke sammenhengen mellom første par 
    query1 = f"""
    SELECT {weather1}, {airquality1}
    FROM merged_df
    WHERE {weather1} IS NOT NULL AND {airquality1} IS NOT NULL
    ORDER BY {weather1} DESC
    """
    result1 = psql.sqldf(query1, locals())
 

    # SQL-spørring for å undersøke sammenhengen mellom andre par 
    query2 = f"""
    SELECT {weather2}, {airquality2}
    FROM merged_df
    WHERE {weather2} IS NOT NULL AND {airquality2} IS NOT NULL
    ORDER BY {weather2} DESC
    """
    result2 = psql.sqldf(query2, locals())
   
    # Pearson-korrelasjon
    # Lager ny df med relevante kolonner og dropper NaN-verdier
    df_analyse = merged_df[[weather1, airquality1, weather2, airquality2]].dropna()
    # Beregner korrelasjonene
    korrelasjon_1= df_analyse[weather1].corr(df_analyse[airquality1], method='pearson')
    korrelasjon_2 = df_analyse[weather2].corr(df_analyse[airquality2], method='pearson')

    print(f"Korrelasjon mellom {weather1} og {airquality1}: {korrelasjon_1}")
    print(f"Korrelasjon mellom {weather2} og {airquality2}: {korrelasjon_2}")


    #Visualisering av korrelasjonen 
    plt.figure(figsize = (12, 6))

    plt.subplot(1, 2, 1)
    sns.scatterplot(x = weather1, y = airquality1, data = df_analyse)
    plt.title(f"{weather1} vs {airquality1}")
    plt.xlabel(f"{weather1}")
    plt.ylabel(f"{airquality1}")

    plt.subplot(1, 2, 2)
    sns.scatterplot(x = weather2, y = airquality2, data = df_analyse)
    plt.title(f"{weather2} vs {airquality2}")
    plt.xlabel(f"{weather2}")
    plt.ylabel(f"{airquality2}")

    plt.tight_layout()
    plt.show()


def analyze_frost_nilu():
    """
    Leser inn rengjorte værdata fra frostAPI og luftkvalitetsdata fra niluAPI, og
    analyserer korrelasjonen mellom værdata og luftkvalitetsdata ved å kalle den generelle 
    funksjonen "analyze_correlation_between_weather_and_air_quality".

    Returns:
        tuple: Resultater fra SQL-spørringer og korrelasjonsberegninger.
    """
    
    with open("../data/clean_data/frostAPI_clean_data.json", "r") as frost_file, \
         open("../data/clean_data/niluAPI_clean_data.json", "r") as nilu_file:
        data_frost = json.load(frost_file)
        data_nilu = json.load(nilu_file)
    df_frost = pd.json_normalize(data_frost)
    df_nilu = pd.json_normalize(data_nilu)

    return analyze_correlation_between_weather_and_air_quality(
        df_frost, df_nilu,
        date="Dato",
        weather1="Temperatur",
        airquality1="Verdi_O3",
        weather2="Vindhastighet",
        airquality2="Verdi_NO2"
    )


