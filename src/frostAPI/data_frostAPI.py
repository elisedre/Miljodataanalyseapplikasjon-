import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.stats import pearsonr
from sklearn.preprocessing import PowerTransformer
import seaborn as sns
from sklearn.preprocessing import PowerTransformer, StandardScaler


def fetch_data_from_frostAPI(endpoint, parameters, client_id):
    """
    Henter rådata fra Frost API.

    Args:
        endpoint (str): API-endepunktet.
        parameters (dict): Parametere for API-kallet.
        client_id (str): Client ID for autentisering.

    Returns:
        list: Liste med data fra API-et, eller en tom liste hvis noe går galt.
    """
    response = requests.get(endpoint, params=parameters, auth=(client_id, ""))
    
    # Sjekk om forespørselen var vellykket
    if response.status_code != 200:
        print("Feil ved henting av data: Status Code:", response.status_code)
        print("Response Text:", response.text)
        return []
    
    # Returner data fra API-responsen
    return response.json().get("data", [])


def process_weather_data(data, elements):
    """
    Prosesserer rådata fra Frost API til en liste med dictionaries.

    Args:
        data (list): Liste med rådata fra API-et.
        elements (dict): Mapping av elementId til kolonnenavn.

    Returns:
        list: Liste med prosesserte data.
    """
    målinger = []  
    for måling in data:
        tidspunkt = måling["referenceTime"]
        stasjon = måling["sourceId"]

        måling_dict = {"Dato": tidspunkt[:10], "Stasjon": stasjon}
        
        for verdi in måling.get("observations", []):
            if verdi["elementId"] in elements:
                måling_dict[elements[verdi["elementId"]]] = verdi["value"]
        
        
        målinger.append(måling_dict)
    return målinger



def save_data_as_json(data, file, index_columns, value_columns, aggfunc="mean"):
    """
    Lagrer data som JSON-fil med fleksible kolonner og aggregeringsfunksjon.

    Args:
        data (list): Liste med prosesserte data.
        file (str): Filsti for lagring av data.
        index_columns (list): Kolonner som skal brukes som indeks i pivot-tabellen.
        value_columns (list): Kolonner som skal aggregeres.
        aggfunc (str or function): Aggregeringsfunksjon (f.eks. "mean", "sum").
    """

    df = pd.DataFrame(data)
    
    pivot_df = df.pivot_table(
        index=index_columns,  
        values=value_columns,  
        aggfunc=aggfunc       
    ).reset_index()
    
    # Lagre pivot-tabellen som en JSON-fil
    pivot_df.to_json(file, orient="records", indent=4, force_ascii=False)
    print(f"Gruppert data er lagret under {file}")


def fetch_weather_data_frostAPI(endpoint, parameters, file, client_id, elements):
    """
    Hovedfunksjon for å hente, prosessere og lagre værdata fra Frost API.

    Args:
        endpoint (str): API-endepunktet.
        parameters (dict): Parametere for API-kallet.
        file (str): Filsti for lagring av data.
        client_id (str): Client ID for autentisering.
        elements (dict): Mapping av elementId til kolonnenavn.
    """
    
    raw_data = fetch_data_from_frostAPI(endpoint, parameters, client_id)
    if not raw_data:
        print("Ingen data hentet.")
        return
    
    processed_data = process_weather_data(raw_data, elements)

    save_data_as_json(
        data=processed_data,
        file=file,
        index_columns=["Dato"],  
        value_columns=list(elements.values()),  
        aggfunc="mean"  
    )

    return processed_data 

#Spesiell funskjon for å bruke generell frostAPI funksjon for hente værdata 
def data_frostAPI(client_id):
    """
    Henter data fra Frost API ved hjelp av en klient-ID.

    Argumenter:
    - client_id (str): En streng som representerer klient-ID-en som brukes for autentisering mot Frost API.

    Returnerer:
    - dict: Data hentet fra Frost API i JSON-format.
    """

    endpoint = "https://frost.met.no/observations/v0.jsonld"
    parameters = {
        "sources": "SN18700",
        "elements": "mean(air_temperature P1D),sum(precipitation_amount P1D),mean(wind_speed P1D)",
        "referencetime": "2010-04-02/2016-12-31",
    }

    file = "../../data/raw_data/frostAPI_data.json"
    elements = {
        "mean(air_temperature P1D)": "Temperatur",
        "sum(precipitation_amount P1D)": "Nedbør",
        "mean(wind_speed P1D)": "Vindhastighet"
    }

    fetch_weather_data_frostAPI(endpoint, parameters, file, client_id, elements)


def get_info_frostAPI(endpoint, parameters, client_id):
    """
    Henter informasjon om tilgjengelige elementer fra Frost API.

    Args:
        endpoint (str): API-endepunktet.
        parameters (dict): Parametere for API-kallet.
        client_id (str): Client ID for autentisering.
    """
    response = requests.get(endpoint, params=parameters, auth=(client_id, ''))
    data = response.json()

    if response.status_code == 200:
        elements = data['data']
        for element in elements:
            print(f"ID: {element['id']}, Navn: {element.get('name', 'Ingen navn')}")
    else:
        print(f"Feil ved henting av stasjoner: {data}")


#Spesiell funksjon for å bruke generell funksjon for hente elementer fra frostAPI
def get_elements_frostAPI(client_id):
    """
    Bruker get_info_frostAPI til å hente elementer fra Frost API.

    Args:
        client_id (str): Client ID for autentisering.
    """
    parameters = None
    endpoint = 'https://frost.met.no/elements/v0.jsonld'
    get_info_frostAPI(endpoint, parameters, client_id)


#Spesiell funksjon for å bruke generell funksjon for hente stasjoner fra frostAPI
def get_stations_frostAPI(client_id):
    """
    Bruker get_info_frostAPI til å hente stasjoner fra Frost API.

    Args:
        client_id (str): Client ID for autentisering.
    """
    
    parameters = {
        'types': 'SensorSystem',  
        'country': 'NO',      
    }

    endpoint = 'https://frost.met.no/sources/v0.jsonld'
    get_info_frostAPI(endpoint, parameters, client_id)


def calculate_outliers(df, col, threshold=3):
    """
    Beregner outliers for en gitt kolonne basert på standardavvik.

    Args:
        df (pd.DataFrame): Datasettet.
        col (str): Kolonnenavn som skal analyseres.
        threshold (float): Antall standardavvik som definerer en outlier.

    Returns:
        tuple: Grenser for outliers (lower_limit, upper_limit) og en boolsk maske for outliers.
    """
    mean = df[col].mean()
    std = df[col].std()
    lower_limit = mean - threshold * std
    upper_limit = mean + threshold * std
    is_outlier = (df[col] < lower_limit) | (df[col] > upper_limit)
    return lower_limit, upper_limit, is_outlier


# Plot outliers
def analyze_and_plot_outliers(df, variables, threshold=3):
    """
    Analyserer og plott outliers for gitte variabler i en DataFrame.

    Args:
        df (pd.DataFrame): Datasettet.
        variables (list): Liste over kolonnenavn som skal analyseres.
        threshold (float): Antall standardavvik som definerer en outlier.
    """
    for var in variables:
        mean = df[var].mean()
        std = df[var].std()
        lower_limit = mean - threshold * std
        upper_limit = mean + threshold * std

        outliers = df[~df[var].between(lower_limit, upper_limit)]
        print(f"\nOutliers for {var}:")
        print(outliers[[var]].count())

        plot = sns.displot(data=df, x=var, kde=True)
        plot.set(title=f"Distribusjon av {var}", xlabel=var)

        for ax in plot.axes.flat:
            ax.axvline(lower_limit, color='r', linestyle='--', label='Lower Limit')
            ax.axvline(upper_limit, color='r', linestyle='--', label='Upper Limit')
            ax.legend()

        plt.show()

#Visualiserer outliers
def analyze_frost_data():
    """
    Leser Frost API-data fra en JSON-fil, analyserer og visualiserer outliers.

    Funksjonalitet:
    - Leser data fra "../../data/raw_data/frostAPI_data.json".
    - Analyserer outliers for variablene 'Nedbør', 'Temperatur', og 'Vindhastighet'.
    - Visualiserer distribusjonen av dataene og markerer outlier-grenser.

    Argumenter:
    - Ingen.

    Returnerer:
    - Ingen returverdi. Genererer grafer og skriver ut analyseresultater.
    """
    df_frost = pd.read_json("../../data/raw_data/frostAPI_data.json")
    variables = ['Nedbør', 'Temperatur', 'Vindhastighet']
    threshold = 3

    analyze_and_plot_outliers(df_frost, variables, threshold)

#
def interpolate_and_save_clean_data(pivot_df, clean_data_file, from_date, to_date):
    """
    Setter verdiene som mangler målinger fra til Nan, og interpolerer alle NaN-verdier med linær metode. 
    Lagre den rensede dataen som en JSON-fil.
    Args:
        pivot_df (pd.DataFrame): DataFrame med værdata med fjernet outliers.
        clean_data_file (str): Filsti for lagring av renset data.
        from_date (str): Startdato for interpolering i formatet 'YYYY-MM-DD'.
        to_date (str): Sluttdato for interpolering i formatet 'YYYY-MM-DD'.

    """
    # Konverterer datoer
    all_dates = pd.date_range(start=from_date, end=to_date).strftime('%Y-%m-%d')
    pivot_df["Dato"] = pd.to_datetime(pivot_df["Dato"])

    pivot_df.set_index("Dato", inplace=True)
    pivot_df = pivot_df.reindex(all_dates)
    pivot_df.reset_index(inplace=True)
    pivot_df.rename(columns={"index": "Dato"}, inplace=True)

    print("\nInterpolering av NaN-verdier:")
    for col in pivot_df.columns:
        if col != "Dato":

            
            interpolated_mask = pivot_df[col].isna()
            null_values = pivot_df[col].isna().sum()
            pivot_df[col] = pivot_df[col].interpolate(method='linear')
            
            interpolated_col_name = f"Interpolert_{col}"
            pivot_df[interpolated_col_name] = interpolated_mask.fillna(False)

            print(f"{col}: {null_values} verdier ble interpolert")

    # Lagre til JSON
    pivot_df.to_json(clean_data_file, orient="records", indent=4, force_ascii=False)
    print(f"\nGruppert data er lagret under {clean_data_file}")

# Interpolerer og lagrer data uten visualisering
def clean_data_frostAPI():
    """
    Leser rådata, analyserer og fjerner outliers, interpolerer manglende verdier,
    og lagrer den rensede dataen. Uten visualisering.
    """
    # Filer og parametere
    raw_data_file = "../../data/raw_data/frostAPI_data.json"
    clean_data_file = "../../data/clean_data/frostAPI_clean_data.json"
    from_date = "2010-01-01"
    to_date = "2016-12-31"
    cols = ["Nedbør", "Temperatur", "Vindhastighet"]
    threshold = 3

    # Last inn data
    try:
        df = pd.read_json(raw_data_file, orient="records", encoding="utf-8")
    except ValueError as e:
        print(f"Feil ved lesing av rådata-fil: {e}")
        return

    df["Dato"] = pd.to_datetime(df["Dato"])

    # Tekstlig outlier-analyse og fjerning
    print("Fjerning av outliers:")
    print(f"Outliers er mer enn {threshold} standardavvik unna gjennomsnittet")

    for col in cols:
        lower_limit, upper_limit, is_outlier = calculate_outliers(df, col, threshold=threshold)
        outlier_count = is_outlier.sum()
        mean = df[col].mean()
        std = df[col].std()

        print(f"\n{col}:")
        print(f"Fjernet {outlier_count} outliers")
        print(f"Standardavvik: {std:.2f}")
        print(f"Gjennomsnitt: {mean:.2f}")
        print(f"Grenser: [{lower_limit:.2f}, {upper_limit:.2f}]")

        df.loc[is_outlier, col] = np.nan

    # Interpoler og lagre data
    interpolate_and_save_clean_data(df, clean_data_file, from_date, to_date)




def analyse_and_fix_skewness(clean_data_file, analyzed_data_file, threshold, cols=None):
    """
    Leser JSON-fil og analyserer skjevhet i dataene med Yeo-Johnson transformasjon og/eller skalering.
    - Kolonner med skjevhet over ±threshold transformeres med Yeo-Johnson og deretter standardiseres.
    - Kolonner med lavere skjevhet standardiseres direkte.

    Args:
        clean_data_file (str): Filsti for input-data (renset).
        analyzed_data_file (str): Filsti for output-data (transformert).
        threshold (float): Grense for skjevhet. Kolonner med høyere skjevhet transformeres.
        cols (list): Valgfrie kolonnenavn for analyse. Hvis None, brukes alle numeriske kolonner.

    Returns:
        pd.DataFrame: DataFrame med transformerte data.
    """
    try:
        df = pd.read_json(clean_data_file, orient="records", encoding="utf-8")
    except ValueError as e:
        print(f"Feil ved lesing av fil: {e}")
        return
    
    df_transformed = df.copy()
    yeo_transformer = PowerTransformer(method='yeo-johnson')
    scaler = StandardScaler()

    if cols is None:
        cols = df_transformed.select_dtypes(include='number').columns

    print("Skjevhet før transformasjon:")
    for col in cols:
        skew_before = df_transformed[col].skew()
        print(f"→ {col}: {skew_before:.2f}")

    print(f"\nPåfører Yeo-Johnson eller standardisering basert på skjevhet (±{threshold}):")
    for col in cols:
        skew = df_transformed[col].skew()
        try:
            if abs(skew) > threshold:
                print(f" {col}: Skjevhet {skew:.2f} → bruker Yeo-Johnson + skalering")
                transformed = yeo_transformer.fit_transform(df_transformed[[col]])
                df_transformed[col] = scaler.fit_transform(transformed)
            else:
                print(f" {col}: Skjevhet {skew:.2f} → bruker kun standardisering")
                df_transformed[col] = scaler.fit_transform(df_transformed[[col]])
        except Exception as e:
            print(f"Feil ved transformasjon av {col}: {e}")

    print("\nSkjevhet etter transformasjon:")
    for col in cols:
        print(f"→ {col}: {df_transformed[col].skew():.2f}")

    df_transformed.to_json(analyzed_data_file, orient="records", indent=4, force_ascii=False)
    print(f"\nTransformert data lagret i {analyzed_data_file}")

    return df_transformed

def fix_skewness_data_frostAPI():
    """
    Wrapper for å transformere Frost-data basert på skjevhet.
    
    Returns:
        pd.DataFrame: Transformert DataFrame for videre analyse.
    """
    clean_data_file = "../../data/clean_data/frostAPI_clean_data.json"
    analyze_data_file = "../../data/analyzed_data/frostAPI_analyzed_data.json"
    threshold = 1.0
    cols = ["Nedbør", "Temperatur", "Vindhastighet"]

    return analyse_and_fix_skewness(clean_data_file, analyze_data_file, threshold, cols)
 
def analyse_correlation(data, x_var, y_var):
    """
    Undersøk sammenhengen mellom to variabler i værdata.
    
    Args:
        data (list of dict): Innholdet fra JSON-filen.
        x_var (str): Navnet på variabelen som skal brukes som X-akse.
        y_var (str): Navnet på variabelen som skal brukes som Y-akse.
        
    Printer korrelasjonskoeffisient og p-verdi, og viser scatterplot.
    """
    
    try:
        x = [entry[x_var] for entry in data if x_var in entry]
        y = [entry[y_var] for entry in data if y_var in entry]
        
        if len(x) != len(y):
            raise ValueError("Ulik lengde på x og y-data")
        
        r, p = pearsonr(x, y)
        print(f"Korrelasjonskoeffisient (r): {r:.3f}")
        print(f"P-verdi: {p:.3f}")

        plt.scatter(x, y, alpha=0.3, s=10)
        plt.xlabel(x_var)
        plt.ylabel(y_var)
        plt.title(f"Korrelasjon mellom {x_var} og {y_var}")
        plt.grid(True)
        plt.show()

    except KeyError as e:
        print(f"Feil: Fant ikke nøkkelen {e} i dataen.")
    except Exception as e:
        print(f"Noe gikk galt: {e}")


def get_season(date):
    """
    Bestemmer hvilken sesong en gitt dato tilhører.

    Argumenter:
    - date (datetime): En dato i datetime-format.

    Returnerer:
    - str: Navnet på sesongen ('Vår', 'Sommer', 'Høst', 'Vinter') som datoen tilhører.
    """
    if date.month in [3, 4, 5]:
        return 'Vår'
    elif date.month in [6, 7, 8]:
        return 'Sommer'
    elif date.month in [9, 10, 11]:
        return 'Høst'
    else:
        return 'Vinter'


def calculate_and_plot_seasonal_bars(data):
    """
    Beregner og visualiserer gjennomsnittlig temperatur og nedbør per sesong per år
    i form av søylediagrammer.

    Parametere:
    - data: DataFrame med minst kolonnene 'Dato', 'Temperatur', og 'Nedbør'.
    - sesonger: Liste med sesonger å vise (f.eks. ['Vår', 'Sommer']), eller None for å vise alle.
    """

    # Konverter og legg til sesong og år
    data['Dato'] = pd.to_datetime(data['Dato'])

    data['Sesong'] = data['Dato'].apply(get_season)
    data['År'] = data['Dato'].dt.year

    # Grupperer data etter år og sesong
    season_stats = data.groupby(['År', 'Sesong']).agg({
        'Temperatur': ['mean', 'std'],
        'Nedbør': ['mean', 'std']
    }).reset_index()

    season_stats.columns = [
        'År', 'Sesong',
        'Temperatur_Gjennomsnitt', 'Temperatur_Std',
        'Nedbør_Gjennomsnitt', 'Nedbør_Std'
    ]

    sesonger = ['Vår', 'Sommer', 'Høst', 'Vinter']

    for sesong in sesonger:
        data_sesong = season_stats[season_stats['Sesong'] == sesong]

        if data_sesong.empty:
            print(f"Ingen data for sesongen: {sesong}")
            continue

        # Temperatur søylediagram
        plt.figure(figsize=(10, 5))
        plt.bar(data_sesong['År'], data_sesong['Temperatur_Gjennomsnitt'], yerr=data_sesong['Temperatur_Std'],
                capsize=5, color='salmon', label='Temperatur')
        plt.title(f"Gjennomsnittstemperatur per år – {sesong}")
        plt.xlabel("År")
        plt.ylabel("Temperatur (°C)")
        plt.grid(axis='y', linestyle='--', alpha=0.6)
        plt.tight_layout()
        plt.show()

        # Nedbør søylediagram
        plt.figure(figsize=(10, 5))
        plt.bar(data_sesong['År'], data_sesong['Nedbør_Gjennomsnitt'], yerr=data_sesong['Nedbør_Std'],
                capsize=5, color='skyblue', label='Nedbør')
        plt.title(f"Gjennomsnittsnedbør per år – {sesong}")
        plt.xlabel("År")
        plt.ylabel("Nedbør (mm)")
        plt.grid(axis='y', linestyle='--', alpha=0.6)
        plt.tight_layout()
        plt.show()


def plot_no2_with_temperature(df):
    """
    Lager en linjegraf for Verdi_NO2 med temperatur og NO₂ på to forskjellige y-akser.
    
    Forventede kolonner: 'Dato', 'Temperatur', 'Verdi_NO2'
    """

    df['Dato'] = pd.to_datetime(df['Dato'])
    df = df.sort_values('Dato')

    fig, ax1 = plt.subplots(figsize=(14, 6))

    # Temperatur på venstre y-akse
    ax1.set_xlabel("Dato")
    ax1.set_ylabel("Temperatur (°C)", color='tab:blue')
    ax1.plot(df['Dato'], df['Temperatur'], color='tab:blue', label='Temperatur', linewidth=2)
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    # NO₂ på høyre y-akse
    ax2 = ax1.twinx()
    ax2.set_ylabel("NO₂ (μg/m³)", color='tab:orange')
    ax2.plot(df['Dato'], df['Verdi_NO2'], color='tab:orange', label='NO₂ (μg/m³)', linewidth=2)
    ax2.tick_params(axis='y', labelcolor='tab:orange')

    # tittel og rutenett
    ax1.set_title("Temperatur og NO₂ over tid")
    ax1.grid(True, linestyle='--', alpha=0.5)

    # Datoformat på x-aksen
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.xticks(rotation=45)

    sm = plt.cm.ScalarMappable(cmap='coolwarm', norm=plt.Normalize(vmin=df['Temperatur'].min(), vmax=df['Temperatur'].max()))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax1, orientation='vertical', label='Temperatur (°C)')

    plt.tight_layout()
    plt.show()



