import pandas as pd
import pandasql as psql
import matplotlib.pyplot as plt
import json
import seaborn as sns 

def load_clean_data(filepath="../../data/clean_data/frostAPI_clean_data.json"):
    """
    Leser inn rengjorte værdata fra angitt JSON-fil.

    Args:
        filepath (str): Filsti til JSON-data.

    Returns:
        pd.DataFrame: DataFrame med værdata, eller tom hvis feil oppstår.
    """
    try:
        df = pd.read_json(filepath)
        return df
    except Exception as e:
        print(f"Feil ved lesing av fil '{filepath}': {e}")
        return pd.DataFrame()
    
def analyze_hottest_days(df, date_col, temp_col, precip_col, n_days):
    """
    Analyserer de varmeste dagene basert på temperatur, visualiserer sammenhengen 
    med nedbør og lager et kakediagram for fordeling per år.

    Args:
        df (pd.DataFrame): DataFrame med værdata.
        date_col (str): Navn på kolonnen som inneholder dato.
        temp_col (str): Navn på kolonnen som inneholder temperaturverdier.
        precip_col (str): Navn på kolonnen som inneholder nedbørverdier.
        n_days (int): Antall varmeste dager som skal analyseres.

    Returns:
        pd.DataFrame: DataFrame med de varmeste dagene.
    """
    try:
        # SQL-spørring for å hente de n varmeste dagene
        query = f"""
        SELECT *
        FROM df
        ORDER BY {temp_col} DESC
        LIMIT {n_days}
        """
        hottest_days = psql.sqldf(query, locals())

        # Legger til kolonne med år basert på datokolonnen
        hottest_days['År'] = pd.to_datetime(hottest_days[date_col]).dt.year

    except Exception as e:
        print(f"Feil under dataanalyse: {e}")
        return pd.DataFrame()  # Returnerer tomt DataFrame ved feil

    # Visualisering: Temperatur og nedbør med scatterplot
    try:
        plt.figure(figsize=(6, 3))
        x = range(len(hottest_days))
        plt.scatter(x, hottest_days[temp_col], color='red', label=f'{temp_col} (°C)', s=100)
        plt.scatter(x, hottest_days[precip_col], color='blue', label=f'{precip_col} (mm)', s=100)
        plt.title(f'{temp_col} (°C) vs {precip_col} (mm) for de {n_days} varmeste dagene')
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()
    except Exception as e:
        print(f"Feil under scatterplot-visualisering: {e}")

    # Visualisering: Kakediagram etter år 
    try:
        # Teller antall dager per år
        year_counts = hottest_days['År'].value_counts()

        plt.figure(figsize=(6, 6))
        plt.pie(
            year_counts,
            labels = year_counts.index,
            autopct = '%1.1f%%',
            colors = plt.cm.Set3.colors
        )
        plt.title(f"De {n_days} varmeste dagene fordelt på år")
        plt.axis('equal')
        plt.show()
    except Exception as e:
        print(f"Feil under kakediagram-visualisering: {e}")

    return hottest_days

def analyze_frost_api_clean_data():
    """
    Leser inn rengjorte værdata fra Frost API og analyserer de varmeste dagene
    basert på temperatur og nedbør ved å kalle analyze_hottest_days.

    Returns:
        pd.DataFrame: DataFrame med de varmeste dagene.
    """
    df = load_clean_data()
    if df.empty:
        return df

    # Kaller analysefunksjonen med relevante kolonnenavn
    return analyze_hottest_days(
        df = df,
        date_col = "Dato",
        temp_col = "Temperatur",
        precip_col = "Nedbør",
        n_days = 10
    )

def analyze_coldest_days(df, date_col, temp_col, n_days):
    """
    Analyserer de kaldeste dagene i et datasett, og visualiserer fordelingen
    av disse dagene etter år i et kakediagram.

    Args:
        df (pd.DataFrame): DataFrame med værdata.
        date_col (str): Navn på kolonnen med dato.
        temp_col (str): Navn på kolonnen med temperatur.
        n_days (int): Antall kaldeste dager som skal analyseres.

    Returns:
        pd.DataFrame: DataFrame med de kaldeste dagene og tilhørende år.
    """
    try:
        # SQL-spørring for å hente de n kaldeste dagene
        query = f"""
            SELECT {date_col}, {temp_col}
            FROM df 
            ORDER BY {temp_col} ASC 
            LIMIT {n_days}
        """
        coldest_days = psql.sqldf(query, locals())

        # Legger til kolonne med år fra dato
        coldest_days['År'] = pd.to_datetime(coldest_days[date_col]).dt.year

    except Exception as e:
        print(f"Feil under henting eller bearbeiding av data: {e}")
        return pd.DataFrame()

    # Visualisering: kakediagram som viser fordeling etter år
    try:
        # Teller antall dager per år
        year_counts = coldest_days['År'].value_counts()

        plt.figure(figsize=(6, 6))
        plt.pie(
            year_counts,
            labels=year_counts.index,
            autopct='%1.1f%%',
            colors=plt.cm.Set3.colors
        )
        plt.title(f"De {n_days} kaldeste dagene fordelt på år")
        plt.axis('equal')
        plt.show()

    except Exception as e:
        print(f"Feil under visualisering: {e}")

    return coldest_days

def analyze_coldest_frost_api_data():
    """
    Leser inn rengjorte værdata fra Frost API og analyserer de kaldeste dagene
    ved hjelp av analyze_coldest_days-funksjonen.

    Returns:
        pd.DataFrame: DataFrame med de kaldeste dagene og tilhørende år.
    """
    # Rengjorte data fra Frost API
    df = load_clean_data()
    if df.empty:
        return df
    
    # Kaller analysefunksjonen med relevante kolonnenavn
    return analyze_coldest_days(
        df=df,
        date_col="Dato",
        temp_col="Temperatur",
        n_days=10
    )


def analyze_avg_temperature_per_year(df, date_col, temp_col):
    """
    Beregner og visualiserer gjennomsnittlig temperatur per år basert på en DataFrame med værdata.

    Args:
        df (pd.DataFrame): DataFrame med værdata.
        date_col (str): Kolonnenavn for dato.
        temp_col (str): Kolonnenavn for temperatur.

    Returns:
        pd.DataFrame: DataFrame med gjennomsnittlig temperatur per år.
    """
    try:
        # SQL-spørring for å finne gjennomsnittlig temperatur per år
        query = f"""
            SELECT strftime('%Y', {date_col}) AS År,
                   AVG({temp_col}) AS Gjennomsnitt_temperatur
            FROM df
            GROUP BY År
            ORDER BY År
        """
        result = psql.sqldf(query, locals())

    except Exception as e:
        print(f"Feil under aggregering av temperaturdata: {e}")
        return pd.DataFrame()

    # Visualisering av gjennomsnittstemperatur per år
    try:
        plt.figure(figsize=(10, 5))
        plt.plot(result['År'], result['Gjennomsnitt_temperatur'],
                 marker='o', color='blue', linestyle='-')
        plt.title("Gjennomsnittlig temperatur per år")
        plt.xlabel("År")
        plt.ylabel("Temperatur (°C)")
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    except Exception as e:
        print(f"Feil under visualisering: {e}")

    return result

def analyze_avg_temp_frost_api_data():
    """
    Leser inn rengjorte værdata fra Frost API og analyserer gjennomsnittstemperatur per år.

    Returns:
        pd.DataFrame: DataFrame med gjennomsnittlig temperatur per år.
    """
    df = load_clean_data()
    if df.empty:
        return df

    # Kaller analysefunksjonen med relevante kolonnenavn
    return analyze_avg_temperature_per_year(
        df=df,
        date_col="Dato",
        temp_col="Temperatur"
    )

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

    try:
        # SQL-spørring for å beregne ukentlig gjennomsnitt
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
    except Exception as e:
        print(f"Feil under SQL-spørring: {e}")
        return pd.DataFrame()
    
    try:
        # Visualisering av gjennomsnittlig nedbør, temperatur og vindhastighet per uke
        plt.figure(figsize=(14, 7))
        plt.plot(result['Uke'], result['Avg_Temperatur'], label='Temperatur (°C)', color='red', marker='o')
        plt.plot(result['Uke'], result['Avg_Nedbør'], label='Nedbør (mm)', color='blue', marker='s')
        plt.plot(result['Uke'], result['Avg_Vindhastighet'], label='Vindhastighet (m/s)', color='green', marker='^')

        plt.xlabel('Uke')
        plt.ylabel('Gjennomsnitt per uke')
        plt.title('Gjennomsnittlig Nedbør, Temperatur og Vindhastighet per uke')
        plt.xticks(result['Uke'][::24], rotation=45)
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()
    except Exception as e:
        print(f"Feil ved visualisering: {e}")

    return result

def analyze_weekly_avg_frost_api_data():
    """
    Leser inn rengjorte værdata fra frostAPI og analyserer ukentlig gjennomsnitt for nedbør, temperatur og vindhastighet 
    ved å kalle den generelle funksjonen "analyze_weekly_avg_data".

    Returns:
        pd.DataFrame: DataFrame med ukentlig gjennomsnitt for nedbør, temperatur og vindhastighet.
    """
    df = load_clean_data()
    if df.empty:
        return df
    
    # Kaller analysefunksjonen med relevante kolonnenavn
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
    try:
    # SQL-spørring for å beregne standardavvik
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
    except Exception as e:
        print(f"Feil ved SQL-beregning av standardavvik: {e}")
        return pd.DataFrame()

def calculate_std_frost_data():
    """
    Leser inn rengjorte værdata fra Frost API og beregner standardavvik for nedbør, temperatur og vindhastighet.

    Returns:
        pd.DataFrame: DataFrame med standardavvik for nedbør, temperatur og vindhastighet.
    """
    df = load_clean_data()
    if df.empty:
        return df

    # Kaller den generelle funksjonen for å beregne standardavvik
    return calculate_std_dev(df, "Nedbør", "Temperatur", "Vindhastighet")


def calculate_weekly_std_dev(df, date, group, col1, col2, col3):
    """
    Beregner ukentlig standardavvik for tre kolonner i et datasett ved hjelp av pandas.

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
    try:
        # Konverterer dato-kolonnen til datetime og lager en uke-kolonne
        df[date] = pd.to_datetime(df[date])
        df[group] = df[date].dt.strftime('%Y-U%U') 
        
        # Beregner ukentlig standardavvik
        result = df.groupby(group)[[col1, col2, col3]].std().reset_index()
        result.columns = [group, f'StdDev_{col1}', f'StdDev_{col2}', f'StdDev_{col3}']
        return result
    except Exception as e:
        print(f"Feil ved beregning av ukentlig standardavvik: {e}")
        return pd.DataFrame()

def calculate_std_frost_weekly():
    """
    Leser inn rengjorte værdata fra Frost API og beregner ukentlig standardavvik for nedbør, temperatur og vindhastighet 
    ved å kalle den generelle funksjonen "calculate_weekly_std_dev".

    Returns:
        pd.DataFrame: DataFrame med ukentlig standardavvik for nedbør, temperatur og vindhastighet.
    """
    df = load_clean_data()
    if df.empty:
        return df

    # Kaller den generelle funksjonen for å beregne ukentlig standardavvik
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
    
    # Merger DataFrames på dato
    try:
        merged_df = pd.merge(df1, df2, on=date, how="inner")  
    except Exception as e:
        raise RuntimeError(f"Feil under sammenslåing av DataFrames: {e}")

    try:
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
    
    except Exception as e:
        print(f"Feil under SQL-spørringer: {e}")
        return None, None

    try:
        # Pearson-korrelasjon
        # Lager ny df med relevante kolonner og dropper NaN-verdier
        df_analyse = merged_df[[weather1, airquality1, weather2, airquality2]].dropna()
        # Beregner korrelasjonene
        korrelasjon_1= df_analyse[weather1].corr(df_analyse[airquality1], method='pearson')
        korrelasjon_2 = df_analyse[weather2].corr(df_analyse[airquality2], method='pearson')
    except Exception as e:
        print(f"Feil under beregning av korrelasjon: {e}")
        return None, None
        
    print(f"Korrelasjon mellom {weather1} og {airquality1}: {korrelasjon_1}")
    print(f"Korrelasjon mellom {weather2} og {airquality2}: {korrelasjon_2}")

    #Visualisering av korrelasjonen 
    plt.figure(figsize = (12, 6))

    plt.subplot(1, 2, 1)
    sns.regplot(x = weather1, y = airquality1, data = df_analyse, line_kws={"color": "red"})
    plt.title(f"{weather1} vs {airquality1}")
    plt.xlabel(f"{weather1}")
    plt.ylabel(f"{airquality1}")

    plt.subplot(1, 2, 2)
    sns.regplot(x = weather2, y = airquality2, data = df_analyse, line_kws={"color": "red"})
    plt.title(f"{weather2} vs {airquality2}")
    plt.xlabel(f"{weather2}")
    plt.ylabel(f"{airquality2}")

    plt.tight_layout()
    plt.show()


def analyze_frost_nilu():
    """
    Leser inn rengjorte værdata fra frostAPI og luftkvalitetsdata fra niluAPI,
    og analyserer korrelasjonen mellom disse ved å bruke funksjonen 
    'analyze_correlation_between_weather_and_air_quality'.

    Returns:
        tuple: Resultater fra korrelasjonsanalyse.
    """
    # Leser inn ferdig rensede data ved hjelp av gjenbrukbar funksjon
    df_frost = load_clean_data("../data/clean_data/frostAPI_clean_data.json")
    df_nilu = load_clean_data("../data/clean_data/niluAPI_clean_data.json")

    # Sjekk om dataene er lastet inn riktig
    if df_frost.empty or df_nilu.empty:
        print("En eller begge DataFrames er tomme. Avbryter analyse.")
        return None, None

    # Kjør korrelasjonsanalyse
    return analyze_correlation_between_weather_and_air_quality(
        df_frost, df_nilu,
        date="Dato",
        weather1="Temperatur",
        airquality1="Verdi_O3",
        weather2="Vindhastighet",
        airquality2="Verdi_NO2"
    )


def analyze_monthly_avg_pollution_data(df, date_col, no2_col, o3_col, so2_col):
    """
    Beregner og visualiserer månedlig gjennomsnitt for NO2, O3 og SO2 basert på luftkvalitetsdata.

    Args:
        df (pd.DataFrame): DataFrame med luftkvalitetsdata.
        date_col (str): Kolonnenavn for dato.
        no2_col (str): Kolonnenavn for NO2-verdier.
        o3_col (str): Kolonnenavn for O3-verdier.
        so2_col (str): Kolonnenavn for SO2-verdier.

    Returns:
        pd.DataFrame: DataFrame med månedlig gjennomsnitt for NO2, O3 og SO2.
    """
    try:
        df_copy = df.copy()
        df_copy["Dato"] = pd.to_datetime(df_copy[date_col])

        # SQL-spørring for å gruppere på måned og beregne gjennomsnitt
        query = f"""
        SELECT 
            strftime('%Y-%m', Dato) AS Måned, 
            AVG({no2_col}) AS Snitt_NO2,
            AVG({o3_col}) AS Snitt_O3,
            AVG({so2_col}) AS Snitt_SO2,
            COUNT(*) AS AntallDager
        FROM df_copy
        GROUP BY Måned
        ORDER BY Måned
        """
        monthly_stats = psql.sqldf(query, locals())
    except Exception as e:
        print(f"Feil ved behandling av data eller SQL-spørring: {e}")
        return None

    try:
        # Visualisering av månedlig gjennomsnitt
        sns.set(style="whitegrid")
        plt.figure(figsize=(14, 7))

        # Plotter linjeplot for hver forurensningstype
        sns.lineplot(data=monthly_stats, x="Måned", y="Snitt_NO2", label="NO2", marker="o")
        sns.lineplot(data=monthly_stats, x="Måned", y="Snitt_O3", label="O3", marker="o")
        sns.lineplot(data=monthly_stats, x="Måned", y="Snitt_SO2", label="SO2", marker="o")

        # Setter tittel og akseetiketter
        plt.title("Månedlig gjennomsnitt for NO2, O3 og SO2", fontsize=16)
        plt.xlabel("Måned")
        plt.ylabel("Gjennomsnittlig verdi (μg/m³)")
        # Roterer x-aksen for bedre lesbarhet
        plt.xticks(rotation=45)
        # Setter x-ticks med jevne mellomrom for bedre oversikt
        plt.gca().set_xticks(monthly_stats['Måned'][::3])
        plt.legend()
        plt.tight_layout()
        plt.show()
    except Exception as e:
        print(f"Feil ved plotting: {e}")

    return monthly_stats


def analyze_monthly_avg_nilu_data():
    """
    Leser inn rengjorte NILU-data og analyserer månedlig gjennomsnitt for NO2, O3 og SO2
    ved å kalle den generelle funksjonen "analyze_monthly_avg_pollution_data".

    Returns:
        pd.DataFrame: DataFrame med månedlig gjennomsnitt for NO2, O3 og SO2.
    """
    # Rengjorte data fra NILU API
    file_path = "../../data/clean_data/niluAPI_clean_data.json"

    df = load_clean_data(file_path)
    if df.empty:
        return df

    # Kaller funksjonen for å beregne og visualisere månedlig gjennomsnitt
    return analyze_monthly_avg_pollution_data(
        df,
        date_col="Dato",
        no2_col="Verdi_NO2",
        o3_col="Verdi_O3",
        so2_col="Verdi_SO2"
    )
