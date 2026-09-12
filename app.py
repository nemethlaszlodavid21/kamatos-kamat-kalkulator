import math
from dataclasses import dataclass

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="Kamatos kamat kalkulátor",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -----------------------------
# Stílus
# -----------------------------
st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(180deg, #f7f9fc 0%, #eef3f9 100%);
        }

        [data-testid="stSidebar"] {
            background: rgba(255, 255, 255, 0.95);
            border-right: 1px solid #e6ebf2;
        }

        .hero {
            background: linear-gradient(135deg, #101828 0%, #1d2939 60%, #344054 100%);
            padding: 28px 30px;
            border-radius: 22px;
            margin-bottom: 22px;
            box-shadow: 0 14px 40px rgba(16, 24, 40, 0.12);
        }

        .hero h1 {
            color: white;
            margin: 0;
            font-size: 2.15rem;
            font-weight: 800;
            letter-spacing: -0.03em;
        }

        .hero p {
            color: #d0d5dd;
            margin: 8px 0 0 0;
            font-size: 1.02rem;
        }

        .metric-card {
            background: white;
            border: 1px solid #e6ebf2;
            border-radius: 18px;
            padding: 19px 20px;
            min-height: 118px;
            box-shadow: 0 7px 24px rgba(16, 24, 40, 0.06);
        }

        .metric-label {
            color: #667085;
            font-size: 0.88rem;
            font-weight: 650;
            margin-bottom: 7px;
        }

        .metric-value {
            color: #101828;
            font-size: 1.65rem;
            font-weight: 800;
            letter-spacing: -0.03em;
            line-height: 1.12;
        }

        .metric-sub {
            color: #98a2b3;
            font-size: 0.78rem;
            margin-top: 6px;
        }

        .section-title {
            color: #101828;
            font-size: 1.28rem;
            font-weight: 800;
            margin-top: 8px;
            margin-bottom: 6px;
        }

        .soft-card {
            background: rgba(255,255,255,0.85);
            border: 1px solid #e6ebf2;
            border-radius: 18px;
            padding: 16px 18px;
            box-shadow: 0 7px 20px rgba(16, 24, 40, 0.04);
        }

        .small-muted {
            color: #667085;
            font-size: 0.85rem;
        }

        .stButton > button {
            border-radius: 12px;
            font-weight: 700;
        }

        div[data-testid="stNumberInput"] input,
        div[data-testid="stSelectbox"] div,
        div[data-testid="stSlider"] {
            border-radius: 12px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# Segédfüggvények
# -----------------------------

def format_huf(value: float) -> str:
    return f"{value:,.0f} Ft".replace(",", " ")


def format_pct(value: float) -> str:
    return f"{value:.1f}%"


PAYMENT_FREQUENCIES = {
    "Hetente": 52,
    "Kéthetente": 26,
    "Havonta": 12,
    "Negyedévente": 4,
    "Félévente": 2,
    "Évente": 1,
}

CREDIT_FREQUENCIES = {
    "Havonta": 12,
    "Negyedévente": 4,
    "Félévente": 2,
    "Évente": 1,
}


@dataclass
class SimulationResult:
    data: pd.DataFrame
    final_balance: float
    total_contributions: float
    total_interest: float
    real_final_balance: float
    total_payment_events: int


def simulate(
    initial_capital: float,
    recurring_payment: float,
    payment_frequency: int,
    annual_payment_increase: float,
    annual_rate: float,
    years: int,
    credit_frequency: int,
    inflation_rate: float,
) -> SimulationResult:
    """
    Napi léptékű cashflow-szimuláció.

    Miért napi?
    - így a heti/havi/negyedéves befizetések egymással kombinálhatók;
    - a kamatot a megadott jóváírási periódusokban írjuk jóvá;
    - az egyes periódusokon belül felhalmozott kamat nem kamatozik tovább a következő
      jóváírásig, ezért a jóváírás gyakorisága ténylegesen számít.
    """
    days_per_year = 365
    total_days = int(years * days_per_year)

    balance = float(initial_capital)
    total_contributions = float(initial_capital)
    accrued_interest = 0.0
    total_payment_events = 0

    # Eseménynapok közelítő, egyenletes elosztással.
    payment_interval = days_per_year / payment_frequency
    credit_interval = days_per_year / credit_frequency

    next_payment_day = payment_interval
    next_credit_day = credit_interval

    daily_rate = (1 + annual_rate) ** (1 / days_per_year) - 1 if annual_rate > -1 else 0

    snapshots = []

    for day in range(1, total_days + 1):
        current_year_index = min((day - 1) // days_per_year, years - 1)
        payment_this_year = recurring_payment * ((1 + annual_payment_increase) ** current_year_index)

        # A már jóváírt egyenleg termeli a kamatot; az időközben felgyűlt kamat
        # csak a következő kamatjóváírás után válik kamatozó tőkévé.
        accrued_interest += balance * daily_rate

        # Rendszeres befizetések
        while day + 1e-9 >= next_payment_day and next_payment_day <= total_days + 1e-9:
            balance += payment_this_year
            total_contributions += payment_this_year
            total_payment_events += 1
            next_payment_day += payment_interval

        # Kamatjóváírás
        while day + 1e-9 >= next_credit_day and next_credit_day <= total_days + 1e-9:
            balance += accrued_interest
            accrued_interest = 0.0
            next_credit_day += credit_interval

        # Év végi snapshot, plusz utolsó nap
        if day % days_per_year == 0 or day == total_days:
            displayed_balance = balance + accrued_interest
            elapsed_years = day / days_per_year
            real_value = displayed_balance / ((1 + inflation_rate) ** elapsed_years) if inflation_rate > -1 else displayed_balance
            snapshots.append(
                {
                    "Év": round(elapsed_years, 2),
                    "Portfólió értéke": displayed_balance,
                    "Saját befizetés": total_contributions,
                    "Hozam": displayed_balance - total_contributions,
                    "Reálérték": real_value,
                }
            )

    final_balance = balance + accrued_interest
    total_interest = final_balance - total_contributions
    real_final_balance = final_balance / ((1 + inflation_rate) ** years) if inflation_rate > -1 else final_balance

    return SimulationResult(
        data=pd.DataFrame(snapshots),
        final_balance=final_balance,
        total_contributions=total_contributions,
        total_interest=total_interest,
        real_final_balance=real_final_balance,
        total_payment_events=total_payment_events,
    )


# -----------------------------
# Oldalsáv – bemeneti adatok
# -----------------------------
with st.sidebar:
    st.markdown("## ⚙️ Beállítások")
    st.caption("Állítsd be a megtakarítási és befektetési feltételeket.")

    initial_enabled = st.toggle("Kezdőtőke használata", value=True)
    initial_capital = st.number_input(
        "Kezdőtőke (Ft)",
        min_value=0,
        max_value=1_000_000_000,
        value=1_000_000 if initial_enabled else 0,
        step=100_000,
        disabled=not initial_enabled,
    )
    if not initial_enabled:
        initial_capital = 0

    st.divider()

    recurring_payment = st.number_input(
        "Rendszeres befizetés (Ft)",
        min_value=0,
        max_value=100_000_000,
        value=100_000,
        step=10_000,
    )

    payment_frequency_label = st.selectbox(
        "Befizetés gyakorisága",
        list(PAYMENT_FREQUENCIES.keys()),
        index=2,
    )

    increase_enabled = st.toggle("Éves befizetés-növelés", value=False)
    annual_payment_increase_pct = st.slider(
        "Éves növelés (%)",
        min_value=0.0,
        max_value=25.0,
        value=5.0,
        step=0.5,
        disabled=not increase_enabled,
    )
    if not increase_enabled:
        annual_payment_increase_pct = 0.0

    st.divider()

    annual_rate_pct = st.slider(
        "Éves hozam / kamatláb (%)",
        min_value=0.0,
        max_value=30.0,
        value=8.0,
        step=0.1,
    )

    years = st.slider(
        "Futamidő (év)",
        min_value=1,
        max_value=50,
        value=20,
        step=1,
    )

    credit_frequency_label = st.selectbox(
        "Kamatjóváírás gyakorisága",
        list(CREDIT_FREQUENCIES.keys()),
        index=0,
        help="A kamat csak jóváírás után válik a kamatozó tőke részévé.",
    )

    st.divider()

    inflation_enabled = st.toggle("Infláció figyelembevétele", value=True)
    inflation_rate_pct = st.slider(
        "Éves infláció (%)",
        min_value=0.0,
        max_value=15.0,
        value=3.0,
        step=0.1,
        disabled=not inflation_enabled,
    )
    if not inflation_enabled:
        inflation_rate_pct = 0.0


# -----------------------------
# Számítás
# -----------------------------
result = simulate(
    initial_capital=initial_capital,
    recurring_payment=recurring_payment,
    payment_frequency=PAYMENT_FREQUENCIES[payment_frequency_label],
    annual_payment_increase=annual_payment_increase_pct / 100,
    annual_rate=annual_rate_pct / 100,
    years=years,
    credit_frequency=CREDIT_FREQUENCIES[credit_frequency_label],
    inflation_rate=inflation_rate_pct / 100,
)


# -----------------------------
# Főoldal
# -----------------------------
st.markdown(
    """
    <div class="hero">
        <h1>Kamatos kamat kalkulátor</h1>
        <p>Tervezd meg, hogyan növekedhet a vagyonod rendszeres befizetéssel, kamatos kamattal és inflációval.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Végső egyenleg</div>
            <div class="metric-value">{format_huf(result.final_balance)}</div>
            <div class="metric-sub">{years} év után</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Saját befizetés</div>
            <div class="metric-value">{format_huf(result.total_contributions)}</div>
            <div class="metric-sub">Kezdőtőkével együtt</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    interest_share = (result.total_interest / result.final_balance * 100) if result.final_balance else 0
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Megtermelt hozam</div>
            <div class="metric-value">{format_huf(result.total_interest)}</div>
            <div class="metric-sub">A végösszeg {interest_share:.1f}%-a</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Mai pénzen</div>
            <div class="metric-value">{format_huf(result.real_final_balance)}</div>
            <div class="metric-sub">{format_pct(inflation_rate_pct)} infláció mellett</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<div class='section-title'>A vagyon növekedése</div>", unsafe_allow_html=True)
st.caption("A grafikon megmutatja, mekkora rész származik a saját befizetéseidből, és mennyit termel a hozam.")

fig = go.Figure()
fig.add_trace(
    go.Scatter(
        x=result.data["Év"],
        y=result.data["Portfólió értéke"],
        mode="lines+markers",
        name="Portfólió értéke",
        line=dict(width=4),
        hovertemplate="%{x:.0f}. év<br><b>%{y:,.0f} Ft</b><extra></extra>",
    )
)
fig.add_trace(
    go.Scatter(
        x=result.data["Év"],
        y=result.data["Saját befizetés"],
        mode="lines",
        name="Saját befizetés",
        line=dict(width=3, dash="dash"),
        hovertemplate="%{x:.0f}. év<br>%{y:,.0f} Ft<extra></extra>",
    )
)

if inflation_enabled:
    fig.add_trace(
        go.Scatter(
            x=result.data["Év"],
            y=result.data["Reálérték"],
            mode="lines",
            name="Reálérték (mai pénzen)",
            line=dict(width=2, dash="dot"),
            hovertemplate="%{x:.0f}. év<br>%{y:,.0f} Ft<extra></extra>",
        )
    )

fig.update_layout(
    height=500,
    margin=dict(l=10, r=10, t=25, b=10),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(255,255,255,0.85)",
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    xaxis_title="Év",
    yaxis_title="Érték (Ft)",
    yaxis_tickformat=",.0f",
)
fig.update_xaxes(showgrid=True, gridcolor="rgba(152,162,179,0.15)")
fig.update_yaxes(showgrid=True, gridcolor="rgba(152,162,179,0.15)")

st.plotly_chart(fig, use_container_width=True)

left, right = st.columns([1.05, 1])

with left:
    st.markdown("<div class='section-title'>Részletes összesítés</div>", unsafe_allow_html=True)

    summary_df = pd.DataFrame(
        {
            "Mutató": [
                "Kezdőtőke",
                "Rendszeres befizetés",
                "Befizetés gyakorisága",
                "Éves befizetés-növelés",
                "Éves hozam",
                "Futamidő",
                "Kamatjóváírás",
                "Befizetések száma",
            ],
            "Érték": [
                format_huf(initial_capital),
                format_huf(recurring_payment),
                payment_frequency_label,
                format_pct(annual_payment_increase_pct),
                format_pct(annual_rate_pct),
                f"{years} év",
                credit_frequency_label,
                f"{result.total_payment_events} alkalom",
            ],
        }
    )
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

with right:
    st.markdown("<div class='section-title'>💡 Mit jelent az eredmény?</div>", unsafe_allow_html=True)

    multiplier = (result.final_balance / result.total_contributions) if result.total_contributions > 0 else 0
    if result.total_interest > 0:
        message = (
            f"A megadott feltételekkel **{format_huf(result.total_contributions)}** saját pénzből "
            f"**{format_huf(result.final_balance)}** vagyon épülhet fel. "
            f"Ebből **{format_huf(result.total_interest)}** a megtermelt hozam."
        )
    else:
        message = "A jelenlegi beállítások mellett nem keletkezik pozitív hozam."

    st.info(message)
    if multiplier > 0:
        st.write(f"A végső egyenleg a saját befizetésed **{multiplier:.2f}×-ese**.")
    if inflation_enabled:
        purchasing_power_loss = result.final_balance - result.real_final_balance
        st.write(
            f"{format_pct(inflation_rate_pct)} átlagos infláció mellett a nominális végösszeg "
            f"mai vásárlóereje körülbelül **{format_huf(result.real_final_balance)}**."
        )

st.markdown("<div class='section-title'>Éves bontás</div>", unsafe_allow_html=True)

annual_table = result.data.copy()
for col in ["Portfólió értéke", "Saját befizetés", "Hozam", "Reálérték"]:
    annual_table[col] = annual_table[col].map(format_huf)
annual_table["Év"] = annual_table["Év"].map(lambda x: f"{x:.0f}")

st.dataframe(annual_table, use_container_width=True, hide_index=True, height=360)

st.caption(
    "A kalkulátor becslést készít. A tényleges befektetési hozamok nem garantáltak, és időben változhatnak. "
    "A heti/havi/negyedéves eseményeket a modell egyenletesen osztja el az éven belül."
)
