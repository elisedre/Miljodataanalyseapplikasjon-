import pandas as pd
from sklearn.preprocessing import PowerTransformer, StandardScaler

def analyse_skewness(df, cols):
    """
    Analyserer og skriver ut skjevhet for valgte kolonner.

    Args:
        df (pd.DataFrame): DataFrame med data.
        cols (list): Liste over kolonner som skal analyseres.

    Returns:
        dict: Ordbok med kolonnenavn som nøkkel og skjevhetsverdi som verdi.
    """
    skewness_dict = {}
    print("Skjevhet før transformasjon:")
    for col in cols:
        skew_val = df[col].skew()
        skewness_dict[col] = skew_val
        print(f"→ {col}: {skew_val:.2f}")
    return skewness_dict

def fix_skewness(df, skewness_dict, threshold):
    """
    Transformerer/skalerer kolonner basert på skjevhetsverdier.
    Legger til nye kolonner med '_Trans'-suffix.

    Args:
        df (pd.DataFrame): DataFrame med data.
        skewness_dict (dict): Ordbok med skjevhetsverdier for kolonner.
        threshold (float): Grenseverdi for skjevhet.

    Returns:
        pd.DataFrame: DataFrame med transformerte kolonner lagt til.
    """
    yeo = PowerTransformer(method='yeo-johnson')
    scaler = StandardScaler()
    df_transformed = df.copy()

    print(f"\nBehandler kolonner med skjevhet over ±{threshold}:\n")
    for col, skew in skewness_dict.items():
        new_col = f"{col}_Trans"
        try:
            if abs(skew) > threshold:
                print(f"{col}: skjevhet {skew:.2f} → Yeo-Johnson + skalering")
                transformed = yeo.fit_transform(df[[col]])
                scaled = scaler.fit_transform(transformed)
                df_transformed[new_col] = scaled.flatten()
            else:
                print(f"{col}: skjevhet {skew:.2f} → kun skalering")
                scaled = scaler.fit_transform(df[[col]])
                df_transformed[new_col] = scaled.flatten()
        except Exception as e:
            print(f"Feil ved transformasjon av {col}: {e}")

    print("\nSkjevhet etter transformasjon:")
    for col in skewness_dict:
        new_col = f"{col}_Trans"
        if new_col in df_transformed.columns:
            print(f"→ {new_col}: {df_transformed[new_col].skew():.2f}")

    return df_transformed