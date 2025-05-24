import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.linear_model import LinearRegression
from sklearn.base import clone
from lightgbm import LGBMRegressor
import plotly.graph_objects as go


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



def load_merge_and_plot_no2_temp():
    """
    Leser inn frost- og nilu-data fra JSON-filer, slår sammen på 'Dato',
    og plotter NO2 og temperatur over tid med to y-akser.

    """
    # Last inn JSON-data
    with open("../data/clean_data/frostAPI_clean_data.json", "r", encoding="utf-8") as file:
        data_frost = json.load(file)

    with open("../data/clean_data/niluAPI_clean_data.json", "r", encoding="utf-8") as file:
        data_nilu = json.load(file)

    # Konverter til DataFrames
    frost_df = pd.DataFrame(data_frost)
    nilu_df = pd.DataFrame(data_nilu)

    # Sørg for at 'Dato' er datetime
    frost_df['Dato'] = pd.to_datetime(frost_df['Dato'])
    nilu_df['Dato'] = pd.to_datetime(nilu_df['Dato'])

    # Slå sammen på 'Dato'
    merged_df = pd.merge(frost_df, nilu_df, on='Dato', how='inner')

    # Kall på plottefunksjonen
    plot_no2_with_temperature(merged_df)

def kombinere_df(file1_path, file2_path, kombineringspunkt):
    """
    Leser og slår sammen to JSON-filer, og returnerer et kombinert flat DataFrame.
    
    Argumenter:
    - file1_path: sti til første JSON-fil
    - file2_path: sti til andre JSON-fil
    - kombineringspunkt: kolonnenavn for å merge (f.eks. 'Dato')
    """
    #Les og normaliser første fil
    with open(file1_path, "r", encoding="utf-8") as f1:
        json1 = json.load(f1)
    df1 = pd.json_normalize(json1)

    #Les og normaliser andre fil
    with open(file2_path, "r", encoding="utf-8") as f2:
        json2 = json.load(f2)
    df2 = pd.json_normalize(json2)

    #Kombiner data
    df_combined = pd.merge(df1, df2, on=kombineringspunkt, how='inner')

    #Konverter til datetime
    df_combined[kombineringspunkt] = pd.to_datetime(df_combined[kombineringspunkt])


    return df_combined

def legg_til_sesongvariabler(df, datokolonne="Dato"):
    """
    Legger til sesongbaserte variabler i datasettet basert på en datokolonne.

    Args:
        df (pd.DataFrame): Datasettet som inneholder en datokolonne.
        datokolonne (str, optional): Navnet på kolonnen som inneholder datoer. 
                                     Standard er "Dato".

    Returns:
        pd.DataFrame: En kopi av datasettet med ekstra kolonner:
            - "måned": Måned (1–12)
            - "ukedag": Ukedag (0=mandag, 6=søndag)
            - "dag_i_året": Dagnummer i året (1–365)
            - "sin_dag": Sinus av dag_i_året (for å modellere sesonger)
            - "cos_dag": Cosinus av dag_i_året (for å modellere sesonger)
    """
    df = df.copy()
    df[datokolonne] = pd.to_datetime(df[datokolonne])
    df["måned"] = df[datokolonne].dt.month
    df["ukedag"] = df[datokolonne].dt.weekday
    df["dag_i_året"] = df[datokolonne].dt.dayofyear
    df["sin_dag"] = np.sin(2 * np.pi * df["dag_i_året"] / 365)
    df["cos_dag"] = np.cos(2 * np.pi * df["dag_i_året"] / 365)
    return df

def tren_modell(df, target_col, features, modell_objekt):
    """
    Trener en prediksjonsmodell basert på utvalgte inputvariabler og målvariabel.

    Args:
        df (pd.DataFrame): Datasettet som inneholder input- og målvariabler.
        target_col (str): Navnet på kolonnen som skal brukes som målvariabel (y).
        features (list of str): Liste over kolonner som skal brukes som input (X).
        modell_objekt (obj): Et modellobjekt som implementerer .fit(X, y),
                             f.eks. LinearRegression(), LGBMRegressor().

    Returns:
        modell_objekt: Den trenede modellen, klar for prediksjon med .predict().
    """
    X = df[features]
    y = df[target_col]
    modell_objekt.fit(X, y)
    return modell_objekt


def prediker_fremtid(df_siste, model, features, target_col, antall_dager, datokolonne="Dato"):
    """
    Genererer fremtidige prediksjoner basert på siste kjente rad i datasettet.

    Args:
        df_siste (pd.DataFrame): Det historiske datasettet som modellen baseres på.
        model (obj): En trent modell med støtte for .predict().
        features (list of str): Liste over feature-kolonner som brukes til prediksjon.
        target_col (str): Navnet på kolonnen som skal predikeres.
        antall_dager (int): Hvor mange dager frem i tid det skal predikeres.
        datokolonne (str, optional): Navnet på datokolonnen. Standard er "Dato".

    Returns:
        pd.DataFrame: En DataFrame med kolonnene:
            - "Dato": Fremtidige datoer
            - "predicted_<target_col>": Modellens predikerte verdier for hver dag
    """
    siste_dato = pd.to_datetime(df_siste[datokolonne].max())
    siste_rad = df_siste.iloc[-1]

    fremtidige_datoer = [siste_dato + pd.Timedelta(days=i) for i in range(1, antall_dager + 1)]
    base_data = {"Dato": fremtidige_datoer}

    sesong_features = {"måned", "ukedag", "dag_i_året", "sin_dag", "cos_dag"}
    for f in features:
        if f not in sesong_features and f in siste_rad:
            base_data[f] = siste_rad[f]
    df_fremtid = pd.DataFrame(base_data)
    df_fremtid = legg_til_sesongvariabler(df_fremtid, datokolonne)        

    X_fremtid = df_fremtid[features]
    df_fremtid[f"predicted_{target_col}"] = model.predict(X_fremtid)

    return df_fremtid[["Dato", f"predicted_{target_col}"]]


import plotly.graph_objects as go
import pandas as pd

def plot_prediksjon_interaktiv(y_train, y_test, y_pred, df_fremtid, target_col, dekningsgrad=None):
    """
    Interaktiv graf som viser treningsdata, testdata (faktisk og predikert), og fremtidige prediksjoner.

    Args:
        y_train (pd.Series): Faktiske verdier som modellen ble trent på.
        y_test (pd.Series): Faktiske verdier brukt for testing av modellen.
        y_pred (array-like): Modellens prediksjoner på testsettet.
        df_fremtid (pd.DataFrame): DataFrame med fremtidige prediksjoner.
                                   Må inneholde kolonnen "predicted_<target_col>".
        target_col (str): Navnet på målvariabelen (target) som visualiseres.
        dekningsgrad (pd.Series, optional): Serie med dekningsgrad.
    """

    forecast = df_fremtid[f"predicted_{target_col}"].values
    total_len = len(y_train) + len(y_test) + len(forecast)
    x_train = list(range(0, len(y_train)))
    x_test = list(range(len(y_train), len(y_train) + len(y_test)))
    x_fut = list(range(len(y_train) + len(y_test), total_len))

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=x_train, y=y_train, mode='lines', name='Treningsdata', line=dict(color='#FF69B4')))
    fig.add_trace(go.Scatter(x=x_test, y=y_test, mode='lines', name='Testdata (ekte)', line=dict(color='red')))
    fig.add_trace(go.Scatter(x=x_test, y=y_pred, mode='lines', name='Testdata (modell)', line=dict(color='orange', dash='dash')))
    fig.add_trace(go.Scatter(x=x_fut, y=forecast, mode='lines', name='Fremtidig prediksjon', line=dict(color='blue', dash='dot')))

    if dekningsgrad is not None:
        dekningsgrad = dekningsgrad.reset_index(drop=True)
        for idx, val in enumerate(dekningsgrad[:total_len]):
            if val == 0.0:
                fig.add_vrect(x0=idx-0.5, x1=idx+0.5, fillcolor="darkgray", opacity=0.4, line_width=0)
            elif 0.0 < val < 100.0:
                fig.add_vrect(x0=idx-0.5, x1=idx+0.5, fillcolor="lightgreen", opacity=0.4, line_width=0)

    fig.add_vline(x=len(y_train) + len(y_test) - 1, line=dict(color='gray', dash='dash'))

    fig.update_layout(
        title=f"{target_col} – Historikk, test og fremtid",
        xaxis_title="Tidsindeks",
        yaxis_title=target_col,
        legend=dict(font=dict(size=12)),
        template="plotly_white",
        height=500,
        width=1000
    )

    fig.show()


def prediksjon_med_fremtidige_verdier(df, target_col, features, model_objekt,
                                      antall_dager=365, test_size=0.2, dekningsgrad=None):
    """
    Trener og evaluerer en prediksjonsmodell, og bruker den til å forutsi fremtidige verdier.

    Args:
        df (pd.DataFrame): Datasettet som inneholder datokolonne, inputvariabler og target.
        target_col (str): Navn på målvariabelen (kolonnen som skal predikeres).
        features (list of str): Liste over kolonnenavn som brukes som input (X).
        model_objekt (obj): Et skalert/skalert modellobjekt med .fit() og .predict(), 
                            f.eks. LinearRegression(), LGBMRegressor(), Pipeline(...)
        antall_dager (int, optional): Hvor mange dager frem i tid det skal predikeres. Default er 365.
        test_size (float, optional): Andel av data som skal brukes som testsett. Default er 0.2.
        dekningsgrad (pd.Series, optional): En valgfri Series som markerer interpolerte/mangelfulle verdier 
                                            (brukes til fargelegging i plottet).

    Returns:
        Resultatet vises som evaluering i konsollen og som et plott med historikk, test og fremtid.
    """

    #Forbered data
    df = df.copy()
    df["Dato"] = pd.to_datetime(df["Dato"])
    df = legg_til_sesongvariabler(df)
    if isinstance(model_objekt, LGBMRegressor):
        model_objekt.set_params(verbose=-1)


    X = df[features]
    y = df[target_col]

    #Del opp i trenings- og testdata (behold rekkefølge)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, shuffle=False
    )

    #Tren på treningsdata
    model = model_objekt.fit(X_train, y_train)

    #Evaluer på testdata
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)

    print(f"\n🔍 Evaluering av modellen '{model_objekt.__class__.__name__}'for '{target_col}' (på testdata):")
    print(f"- R²-score: {r2:.4f}")
    print(f"- MSE: {mse:.4f}")

    #Tren ny modell på hele datasettet for fremtidsprediksjon
    model_full = clone(model_objekt) # kopi med samme innstillinger
    model_full = tren_modell(df, target_col, features, model_full)

    #Prediker fremtid
    df_fremtid = prediker_fremtid(df, model_full, features, target_col, antall_dager)

    #Visualiser historikk + fremtid
    plot_prediksjon_interaktiv(y_train, y_test, y_pred, df_fremtid, target_col, dekningsgrad)


def vis_koeffisienter_linærmodell(df, features, target_cols, datokolonne="Dato"):
    """
    Viser koeffisienter fra lineær regresjon for hver target-kolonne.

    Args:
        df (pd.DataFrame): Datasettet.
        features (list of str): Liste over inputvariabler.
        target_cols (list of str): Liste over målvariabler som skal evalueres.
        datokolonne (str): Navn på datokolonnen for sesongfeature-generering.
    """
    df = legg_til_sesongvariabler(df, datokolonne)

    for target in target_cols:
        f_clean = [f for f in features if f != target]

        model = tren_modell(df, target, f_clean, LinearRegression())

        # Hent og vis koeffisienter
        coeffs = pd.Series(model.coef_, index=f_clean)

        coeffs.plot(kind="bar", title=f"Koeffisienter for {target}", color="skyblue")
        plt.ylabel("Koeffisient")
        plt.tight_layout()
        plt.show()

def plot_polynomregresjon(X, y, grader, feature, target_col):
    """
    Lager et scatterplot og polynomkurver for gitt X og y.

    Args:
        X (np.ndarray): Inputvariabel (1D array).
        y (np.ndarray): Målvariabel.
        grader (list): Grader av polynomer som skal tegnes.
        feature (str): Navn på feature (for labels).
        target_col (str): Navn på target (for labels).
    """
    x_range = np.linspace(X.min(), X.max(), 300)

    plt.figure(figsize=(10, 5))
    plt.scatter(X, y, s=10, color="lightgray", label="Faktiske data")

    for deg in grader:
        model = np.poly1d(np.polyfit(X, y, deg))
        y_pred = model(X)
        r2 = r2_score(y, y_pred)
        plt.plot(x_range, model(x_range), label=f"{deg}. grad (R²={r2:.3f})")
    

    plt.xlabel(feature)
    plt.ylabel(target_col)
    plt.title(f"Polynomregresjon: {feature} → {target_col}")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def vis_polynomregresjon_for_feature(df, feature, target_col, grader=[1, 2, 3], datokolonne="Dato"):
    """
    Viser polynomregresjon mellom én feature og target med ulike grader.

    Args:
        df (pd.DataFrame): Datasettet.
        feature (str): Navnet på inputvariabelen (X).
        target_col (str): Navnet på målvariabelen (y).
        grader (list): Liste over grader som skal vises (default: [1, 2, 3]).
        datokolonne (str): Dato-kolonnen som brukes i sesongtransformasjon.
    """
    df = df.copy()
    df = legg_til_sesongvariabler(df, datokolonne)
    X = df[feature].values
    y = df[target_col].values

    plot_polynomregresjon(X, y, grader, feature, target_col)