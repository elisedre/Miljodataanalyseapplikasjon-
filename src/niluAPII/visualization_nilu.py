import pandas as pd
import plotly.graph_objects as go

def plot_air_quality(df, verdi_kolonner, titler, fargekolonne, tidskolonne="Dato"):
    df[tidskolonne] = pd.to_datetime(df[tidskolonne])

    fig = go.Figure()

    # Legg til alle komponenter, men bare én synlig om gangen
    for i, verdi_kolonne in enumerate(verdi_kolonner):
        fig.add_trace(go.Scatter(
            x=df[tidskolonne],
            y=df[verdi_kolonne],
            mode='markers+lines',
            marker=dict(color=df[fargekolonne], size=6),
            name=titler[i],
            visible=(i == 0)  # Bare første synlig
        ))

    # Dropdown-meny for å velge komponent
    buttons = []
    for i, tittel in enumerate(titler):
        visible = [False] * len(titler)
        visible[i] = True
        buttons.append(dict(label=tittel, method="update", args=[{"visible": visible}, {"title": tittel}]))

    fig.update_layout(
        updatemenus=[dict(
            type="dropdown",
            active=0,
            buttons=buttons,
            x=1.15,
            y=1.15
        )],
        title=titler[0],
        xaxis_title="Dato",
        yaxis_title="Verdi",
        width=1000,
        height=500
    )

    fig.show()