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

def prepare_dataframe(df, date_col):
    """
    Gjør klar DataFrame ved å konvertere og sortere datokolonnen.

    Args:
        df (pd.DataFrame): Datasettet som skal behandles.
        date_col (str): Navnet på kolonnen som inneholder dato.

    Returns:
        pd.DataFrame: Sortert DataFrame med konvertert datokolonne.

    Raises:
        ValueError: Hvis datokolonnen mangler eller kan ikke konverteres.
    """
    df = df.copy()
    if date_col not in df.columns:
        raise ValueError(f"Kolonnen '{date_col}' finnes ikke i datasettet.")

    try:
        df[date_col] = pd.to_datetime(df[date_col])
    except Exception as e:
        raise ValueError(f"Kunne ikke konvertere '{date_col}' til dato: {e}")
    
    return df.sort_values(date_col)

def create_dual_axis_plot(df, date_col, y1_col, y2_col, y1_label, y2_label, y1_color, y2_color):
    """
    Lager et plott med to y-akser på samme tidsakse.

    Args:
        df (pd.DataFrame): Datasettet som skal plottes.
        date_col (str): Navnet på datokolonnen.
        y1_col (str): Kolonne for venstre y-akse.
        y2_col (str): Kolonne for høyre y-akse.
        y1_label (str): Etikett for venstre y-akse.
        y2_label (str): Etikett for høyre y-akse.
        y1_color (str): Farge for venstre linje.
        y2_color (str): Farge for høyre linje.

    Returns:
        tuple: (fig, ax1) – Matplotlib-figur og primærakse.
    
    Raises:
        ValueError: Hvis kolonner mangler.
    """
    for col in [y1_col, y2_col]:
        if col not in df.columns:
            raise ValueError(f"Mangler kolonne: '{col}'")
        
    fig, ax1 = plt.subplots(figsize=(14, 6))

    ax1.set_xlabel("Dato")
    ax1.set_ylabel(y1_label, color=y1_color)
    ax1.plot(df[date_col], df[y1_col], color=y1_color, linewidth=2)
    ax1.tick_params(axis='y', labelcolor=y1_color)
    ax1.grid(True, linestyle='--', alpha=0.5)

    ax2 = ax1.twinx()
    ax2.set_ylabel(y2_label, color=y2_color)
    ax2.plot(df[date_col], df[y2_col], color=y2_color, linewidth=2)
    ax2.tick_params(axis='y', labelcolor=y2_color)

    return fig, ax1

def plot_dual_time_series(df, date_col, y1_col, y2_col, y1_label, y2_label, title, y1_color,
                          y2_color, show_colorbar=True):
    """
    Visualiserer to tidsserier på samme graf med to y-akser.

    Args:
        df (pd.DataFrame): Datasettet som inneholder verdiene.
        date_col (str): Kolonnen med datoer.
        y1_col (str): Kolonnen for venstre y-akse.
        y2_col (str): Kolonnen for høyre y-akse.
        y1_label (str): Tekst for venstre y-akse.
        y2_label (str): Tekst for høyre y-akse.
        title (str): Tittel på figuren.
        y1_color (str): Farge for venstre dataserie.
        y2_color (str): Farge for høyre dataserie.
        show_colorbar (bool): Om fargeskala skal vises basert på y1_col.

    Returns:
        None: Visulaiserer graf.
    """

    df = prepare_dataframe(df, date_col)
    fig, ax1 = create_dual_axis_plot(df, date_col, y1_col, y2_col, y1_label, y2_label, y1_color, y2_color)
    

    
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.xticks(rotation=45)

    if show_colorbar and pd.api.types.is_numeric_dtype(df[y1_col]):
        sm = plt.cm.ScalarMappable(
            cmap='coolwarm',
            norm=plt.Normalize(vmin=df[y1_col].min(), vmax=df[y1_col].max())
        )
        sm.set_array([])
        plt.colorbar(sm, ax=ax1, orientation='vertical', label=y1_label)

    ax1.set_title(title)
    plt.tight_layout()
    plt.show()
    

def plot_temperature_no2(df):
    """
    Viser et ferdig oppsett for visualisering av temperatur og NO₂ over tid.

    Args:
        df (pd.DataFrame): Datasett med kolonnene 'Dato', 'Temperatur' og 'Verdi_NO2'.

    Returns:
        Visualisering av temperatur og NO₂ på to y-akser.
    """
    plot_dual_time_series(df=df, date_col="Dato", y1_col="Temperatur", y2_col="Verdi_NO2", y1_label="Temperatur (°C)",
                          y2_label="NO₂ (μg/m³)", title="Temperatur og NO₂ over tid", y1_color="tab:blue",
                          y2_color="tab:orange", show_colorbar=True)



def load_merge_and_plot_no2_temp():
    """
    Leser inn frost- og NILU-data fra JSON-filer, slår sammen på 'Dato',
    og plotter NO₂ og temperatur over tid.
    """
    merged_df = combine_df(
        "../data/clean_data/frostAPI_clean_data.json",
        "../data/clean_data/niluAPI_clean_data.json",
        "Dato"
    )
    if merged_df is not None and not merged_df.empty:
        plot_temperature_no2(merged_df)
    else:
        print("Klarte ikke å laste eller kombinere dataene.")
    

def combine_df(file1_path, file2_path, combining_point):
    """
    Leser og slår sammen to JSON-filer, og returnerer et kombinert flat DataFrame.
    
    Argumenter:
    - file1_path: sti til første JSON-fil
    - file2_path: sti til andre JSON-fil
    - combining_point: kolonnenavn for å merge (f.eks. 'Dato')

    Return:
    - pd.DataFrame: Kombinert DataFrame med flat struktur
    """
    try:
        with open(file1_path, "r", encoding="utf-8") as f1:
            df1 = pd.json_normalize(json.load(f1))
        with open(file2_path, "r", encoding="utf-8") as f2:
            df2 = pd.json_normalize(json.load(f2))
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Finner ikke fil: {e.filename}")
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON-feil i en av filene: {e}")

    if combining_point not in df1.columns or combining_point not in df2.columns:
        raise KeyError(f"Kolonnen '{combining_point}' finnes ikke i en av filene.")

    df_combined = pd.merge(df1, df2, on=combining_point, how="inner")
    df_combined[combining_point] = pd.to_datetime(df_combined[combining_point])
    return df_combined

    

def add_seasonal_features(df, date_col="Dato"):
    """
    Legger til sesongbaserte variabler i datasettet basert på en datokolonne.

    Args:
        df (pd.DataFrame): Datasettet som inneholder en datokolonne.
        date_col (str, optional): Navnet på kolonnen som inneholder datoer. 
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

    # Konverter kolonnen til datetime-format
    df=prepare_dataframe(df, date_col)
    
    # Legg til sesongbaserte variabler
    df["måned"] = df[date_col].dt.month
    df["ukedag"] = df[date_col].dt.weekday
    df["dag_i_året"] = df[date_col].dt.dayofyear

    # Sinus og cosinus brukes til å modellere sesongmessige mønstre
    df["sin_dag"] = np.sin(2 * np.pi * df["dag_i_året"] / 365)
    df["cos_dag"] = np.cos(2 * np.pi * df["dag_i_året"] / 365)

    return df

def train_model(df, target_col, features, model_object):
    """
    Trener en prediksjonsmodell basert på utvalgte inputvariabler og målvariabel.

    Args:
        df (pd.DataFrame): Datasettet som inneholder input- og målvariabler.
        target_col (str): Navnet på kolonnen som skal brukes som målvariabel (y).
        features (list of str): Liste over kolonner som skal brukes som input (X).
        model_object (obj): Et modellobjekt som implementerer .fit(X, y),
                             f.eks. LinearRegression(), LGBMRegressor().

    Returns:
        model_object: Den trenede modellen, klar for prediksjon med .predict().
    """

    X = df[features]
    y = df[target_col]
    model_object.fit(X, y)
    return model_object
    


def predict_feature_values(df, model, features, target_col, num_days, date_col="Dato"):
    """
    Genererer fremtidige prediksjoner basert på siste kjente rad i datasettet.

    Args:
        df (pd.DataFrame): Det historiske datasettet som modellen baseres på.
        model (obj): En trent modell med støtte for .predict().
        features (list of str): Liste over feature-kolonner som brukes til prediksjon.
        target_col (str): Navnet på kolonnen som skal predikeres.
        num_days (int): Hvor mange dager frem i tid det skal predikeres.
        date_col (str, optional): Navnet på datokolonnen. Standard er "Dato".

    Returns:
        pd.DataFrame: En DataFrame med kolonnene:
            - "Dato": Fremtidige datoer
            - "predicted_<target_col>": Modellens predikerte verdier for hver dag
    """
    
    # Hent siste dato og siste rad for baselineverdier
    last_date = pd.to_datetime(df[date_col].max())
    last_col = df.iloc[-1]

    # Generer fremtidige datoer
    future_dates = [last_date + pd.Timedelta(days=i) for i in range(1, num_days + 1)]
    base_data = {date_col: future_dates}

    # Kopier relevante verdier videre til fremtidsdata
    seasonal_features = {"måned", "ukedag", "dag_i_året", "sin_dag", "cos_dag"}
    for f in features:
        if f not in seasonal_features and f in last_col:
            base_data[f] = last_col[f]

    df_future = pd.DataFrame(base_data)

    # Legg til sesongbaserte variabler
    df_future = add_seasonal_features(df_future, date_col)

    # Prediker
    X_future = df_future[features]
    df_future[f"predicted_{target_col}"] = model.predict(X_future)

    return df_future[[date_col, f"predicted_{target_col}"]]


def plot_prediksjon_interaktiv(y_train, y_test, y_pred, df_future, target_col, coverage=None):
    """
    Lager en interaktiv visualisering av treningsdata, testdata og fremtidige prediksjoner.

    Args:
        y_train (pd.Series): Faktiske verdier som modellen ble trent på.
        y_test (pd.Series): Faktiske verdier brukt for testing.
        y_pred (array-like): Modellens prediksjoner på testsettet.
        df_future (pd.DataFrame): DataFrame med fremtidige prediksjoner.
                                  Må inneholde kolonnen "predicted_<target_col>".
        target_col (str): Navn på målvariabelen som skal vises i grafen.
        coverage (pd.Series, optional): Valgfri Series med dekningsgrad (f.eks. 0–100%).

    Return:
        Viser et interaktivt plot i nettleser / notebook med historiske og fremtidige verdier.
    """

    try:
        forecast = df_future[f"predicted_{target_col}"].values
    except KeyError:
        raise KeyError(f"Kolonnen 'predicted_{target_col}' finnes ikke i df_future.")

    # Definer x-verdier for de tre segmentene (historisk, test, fremtid)
    total_len = len(y_train) + len(y_test) + len(forecast)
    x_train = list(range(0, len(y_train)))
    x_test = list(range(len(y_train), len(y_train) + len(y_test)))
    x_fut = list(range(len(y_train) + len(y_test), total_len))

    fig = go.Figure()

    # Treningsdata
    fig.add_trace(go.Scatter(
        x=x_train, y=y_train, mode='lines', name='Treningsdata', line=dict(color='#FF69B4')
    ))

    # Testdata (faktiske verdier)
    fig.add_trace(go.Scatter(
        x=x_test, y=y_test, mode='lines', name='Testdata (ekte)', line=dict(color='red')
    ))

    # Testdata (modellens prediksjoner)
    fig.add_trace(go.Scatter(
        x=x_test, y=y_pred, mode='lines', name='Testdata (modell)', line=dict(color='orange', dash='dash')
    ))

    # Fremtidige prediksjoner
    fig.add_trace(go.Scatter(
        x=x_fut, y=forecast, mode='lines', name='Fremtidig prediksjon', line=dict(color='blue', dash='dot')
    ))

    # Valgfri fargelegging basert på dekningsgrad
    if coverage is not None:
        coverage = coverage.reset_index(drop=True)
        for idx, val in enumerate(coverage[:total_len]):
            if val == 0.0:
                fig.add_vrect(x0=idx - 0.5, x1=idx + 0.5, fillcolor="darkgray", opacity=0.4, line_width=0)
            elif 0.0 < val < 100.0:
                fig.add_vrect(x0=idx - 0.5, x1=idx + 0.5, fillcolor="lightgreen", opacity=0.4, line_width=0)

    # Visuell skillelinje mellom test og fremtid
    fig.add_vline(
        x=len(y_train) + len(y_test) - 1, line=dict(color='gray', dash='dash')
    )

    # Oppsett av layout og aksene
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

def evaluate_and_train_model(df, target_col, features, model_object, test_size=0.2):
    """
    Trener og evaluerer en modell på gitt datasett og returnerer treningsdata, testdata og prediksjoner.

    Args:
        df (pd.DataFrame): Datasett med input- og målvariabler.
        target_col (str): Navn på kolonnen som skal predikeres.
        features (list of str): Liste over kolonnenavn som brukes som input.
        model_object (obj): Modell som støtter fit() og predict().
        test_size (float): Andel som skal brukes til test. Default er 0.2.

    Returns:
        tuple: (model, X_train, X_test, y_train, y_test, y_pred)
    """
   
    X = df[features]
    y = df[target_col]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, shuffle=False)

    model = model_object.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    r2 = r2_score(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)

    print(f"\n🔍 Evaluering av modellen '{model_object.__class__.__name__}' for '{target_col}':")
    print(f"- R²-score: {r2:.4f}")
    print(f"- MSE: {mse:.4f}")

    return y_train, y_test, y_pred

    
def prediction_with_futurevalues(df, target_col, features, model_object,
                                      num_days=365, test_size=0.2, coverage=None):
    """
    Trener og evaluerer en prediksjonsmodell, og bruker den til å forutsi fremtidige verdier.

    Args:
        df (pd.DataFrame): Datasettet som inneholder datokolonne, inputvariabler og target.
        target_col (str): Navn på målvariabelen (kolonnen som skal predikeres).
        features (list of str): Liste over kolonnenavn som brukes som input (X).
        model_object (obj): Et skalert/skalert modellobjekt med .fit() og .predict(), 
                            f.eks. LinearRegression(), LGBMRegressor(), Pipeline(...)
        num_days (int, optional): Hvor mange dager frem i tid det skal predikeres. Default er 365.
        test_size (float, optional): Andel av data som skal brukes som testsett. Default er 0.2.
        coverage (pd.Series, optional): En valgfri Series som markerer interpolerte/mangelfulle verdier 
                                            (brukes til fargelegging i plottet).

    Returns:
        Resultatet vises som evaluering i konsollen og som et plott med historikk, test og fremtid.
    """

    #Forbered data
    df = df.copy()
    df = add_seasonal_features(df)

    #fjerner overflødig informasjon fra LGBMRegressor, om brukt
    if isinstance(model_object, LGBMRegressor):
        model_object.set_params(verbose=-1)


    y_train, y_test, y_pred = evaluate_and_train_model(df=df, target_col=target_col, features=features,
                                                       model_object=model_object, test_size=test_size)

    #Tren ny modell på hele datasettet for fremtidsprediksjon
    model_full = clone(model_object) # kopi med samme innstillinger
    model_full = train_model(df, target_col, features, model_full)

    #Prediker fremtid
    df_fremtid = predict_feature_values(df, model_full, features, target_col, num_days)

    #Visualiser historikk + fremtid
    plot_prediksjon_interaktiv(y_train, y_test, y_pred, df_fremtid, target_col, coverage)


def plot_linear_model_coefficients(df, features, target_cols, date_col="Dato"):
    """
    Viser koeffisienter fra lineær regresjon for hver target-kolonne.

    Args:
        df (pd.DataFrame): Datasettet.
        features (list of str): Liste over inputvariabler.
        target_cols (list of str): Liste over målvariabler som skal evalueres.
        datokolonne (str): Navn på datokolonnen for sesongfeature-generering.
    
    Returns:
        None: Viser et stolpediagram for hver target-kolonne med koeffisienter.
    """


    df = add_seasonal_features(df, date_col)

    for target in target_cols:
        model = train_model(df, target, [f for f in features if f != target], LinearRegression())
        coeffs = pd.Series(model.coef_, index=[f for f in features if f != target])
        coeffs.plot(kind="bar", title=f"Coefficients for {target}", color="skyblue")
        plt.ylabel("Coefficient value")
        plt.tight_layout()
        plt.show()

    
def plot_polynomial_regression(X, y, level, feature, target_col):
    """
    Lager et scatterplot og polynomkurver for gitt X og y.

    Args:
        X (np.ndarray): Inputvariabel (1D array).
        y (np.ndarray): Målvariabel.
        level (list): Grader av polynomer som skal tegnes (f.eks. [1, 2, 3]).
        feature (str): Navn på inputvariabelen (for akselabel).
        target_col (str): Navn på målvariabelen (for akselabel).

    Returns:
        None. Viser en matplotlib-figur med scatterplot og regresjonslinjer.
    """
   
    # Lag en jevn fordeling av X-verdier til prediksjonslinjene
    x_range = np.linspace(X.min(), X.max(), 300)

    plt.figure(figsize=(10, 5))
    plt.scatter(X, y, s=10, color="lightgray", label="Faktiske data")

    for lev in level:
        # Tren og bruk polynommodell
        model = np.poly1d(np.polyfit(X, y, lev))
        y_pred = model(X)
        r2 = r2_score(y, y_pred)

        # Tegn regresjonslinje med R²-score i label
        plt.plot(x_range, model(x_range), label=f"{lev}. grad (R²={r2:.3f})")

    # Formatering av plottet
    plt.xlabel(feature)
    plt.ylabel(target_col)
    plt.title(f"Polynomregresjon: {feature} → {target_col}")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def visualize_polynomial_fit_for_feature(df, feature, target_col, level=[1, 2, 3], date_col="Dato"):
    """
    Viser polynomregresjon mellom én feature og target med ulike grader.

    Args:
        df (pd.DataFrame): Datasettet.
        feature (str): Navnet på inputvariabelen (X).
        target_col (str): Navnet på målvariabelen (y).
        level (list): Liste over grader som skal vises (default: [1, 2, 3]).
        date_col (str): Dato-kolonnen som brukes i sesongtransformasjon.
    Returns:
        None. Displays a matplotlib plot showing polynomial fits.
    """
    df = df.copy()
    df = add_seasonal_features(df, date_col)
    X = df[feature].values
    y = df[target_col].values

    plot_polynomial_regression(X, y, level, feature, target_col)