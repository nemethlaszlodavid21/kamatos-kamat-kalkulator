import math
from dataclasses import dataclass
from io import BytesIO

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="Kamatos kamat kalkulátor",
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
            margin-top: 12px;
            margin-bottom: 8px;
        }

        .goal-card {
            background: white;
            border: 1px solid #e6ebf2;
            border-radius: 18px;
            padding: 20px 22px;
            box-shadow: 0 7px 24px rgba(16, 24, 40, 0.06);
            margin-bottom: 8px;
        }

        .goal-title {
            color: #667085;
            font-size: 0.88rem;
            font-weight: 700;
            margin-bottom: 8px;
        }

        .goal-value {
            color: #101828;
            font-size: 1.45rem;
            font-weight: 800;
            letter-spacing: -0.02em;
        }

        .goal-detail {
            color: #667085;
            font-size: 0.88rem;
            margin-top: 8px;
            line-height: 1.5;
        }

        .stButton > button,
        .stDownloadButton > button {
            border-radius: 12px;
            font-weight: 700;
        }

        div[data-testid="stNumberInput"] input,
        div[data-testid="stSelectbox"] div,
        div[data-testid="stSlider"] {
            border-radius: 12px;
        }

        /* Mobil optimalizálás */
        @media (max-width: 768px) {
            .block-container {
                padding-top: 1rem !important;
                padding-left: 0.85rem !important;
                padding-right: 0.85rem !important;
                padding-bottom: 2rem !important;
            }

            .hero {
                padding: 20px 18px;
                border-radius: 16px;
                margin-bottom: 16px;
            }

            .hero h1 {
                font-size: 1.65rem;
                line-height: 1.15;
            }

            .hero p {
                font-size: 0.92rem;
                line-height: 1.45;
            }

            .metric-card,
            .goal-card {
                min-height: auto;
                padding: 16px 17px;
                border-radius: 15px;
            }

            .metric-value {
                font-size: 1.42rem;
            }

            .goal-value {
                font-size: 1.28rem;
            }

            .section-title {
                font-size: 1.12rem;
                margin-top: 10px;
            }

            /* A Streamlit oszlopok mobilon kerüljenek egymás alá */
            div[data-testid="stHorizontalBlock"] {
                flex-direction: column !important;
                gap: 0.75rem !important;
            }

            div[data-testid="column"] {
                width: 100% !important;
                flex: 1 1 100% !important;
                min-width: 100% !important;
            }

            /* Letöltés gombok teljes szélességben */
            .stDownloadButton > button,
            .stButton > button {
                width: 100%;
                min-height: 44px;
            }

            /* Inputok kényelmesebb érintéshez */
            div[data-testid="stNumberInput"] input {
                min-height: 42px;
                font-size: 16px;
            }

            div[data-baseweb="select"] > div {
                min-height: 42px;
            }

            /* Plotly grafikon ne lógjon ki */
            div[data-testid="stPlotlyChart"] {
                width: 100% !important;
                overflow-x: hidden !important;
            }

            /* Táblák mobilon vízszintesen görgethetők legyenek */
            div[data-testid="stDataFrame"] {
                width: 100% !important;
                overflow-x: auto !important;
            }

            /* Oldalsáv mobilon valamivel keskenyebb és könnyebben kezelhető */
            section[data-testid="stSidebar"] {
                min-width: min(88vw, 360px) !important;
                max-width: min(88vw, 360px) !important;
            }

            /* Streamlit alap felső margóinak finomhangolása mobilon */
            header[data-testid="stHeader"] {
                background: transparent;
            }
        }

        @media (max-width: 480px) {
            .block-container {
                padding-left: 0.65rem !important;
                padding-right: 0.65rem !important;
            }

            .hero {
                padding: 18px 15px;
            }

            .hero h1 {
                font-size: 1.45rem;
            }

            .hero p {
                font-size: 0.88rem;
            }

            .metric-value {
                font-size: 1.28rem;
            }

            .metric-label,
            .goal-title {
                font-size: 0.82rem;
            }

            .metric-sub,
            .goal-detail {
                font-size: 0.76rem;
            }
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


def format_duration(days: int) -> str:
    years = days // 365
    remaining_days = days % 365
    months = int(remaining_days / (365 / 12))
    remaining = int(round(remaining_days - months * (365 / 12)))

    parts = []
    if years:
        parts.append(f"{years} év")
    if months:
        parts.append(f"{months} hónap")
    if remaining and years == 0:
        parts.append(f"{remaining} nap")
    return " ".join(parts) if parts else "azonnal"


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


@dataclass
class GoalResult:
    reached: bool
    days_to_goal: int | None
    balance_at_goal: float | None
    contributions_at_goal: float | None
    interest_at_goal: float | None


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
    days_per_year = 365
    total_days = int(years * days_per_year)

    balance = float(initial_capital)
    total_contributions = float(initial_capital)
    accrued_interest = 0.0
    total_payment_events = 0

    payment_interval = days_per_year / payment_frequency
    credit_interval = days_per_year / credit_frequency

    next_payment_day = payment_interval
    next_credit_day = credit_interval

    daily_rate = annual_rate / days_per_year if annual_rate > -1 else 0

    snapshots = []

    for day in range(1, total_days + 1):
        current_year_index = min((day - 1) // days_per_year, years - 1)
        payment_this_year = recurring_payment * ((1 + annual_payment_increase) ** current_year_index)

        accrued_interest += balance * daily_rate

        while day + 1e-9 >= next_payment_day and next_payment_day <= total_days + 1e-9:
            balance += payment_this_year
            total_contributions += payment_this_year
            total_payment_events += 1
            next_payment_day += payment_interval

        while day + 1e-9 >= next_credit_day and next_credit_day <= total_days + 1e-9:
            balance += accrued_interest
            accrued_interest = 0.0
            next_credit_day += credit_interval

        if day % days_per_year == 0 or day == total_days:
            displayed_balance = balance + accrued_interest
            elapsed_years = day / days_per_year
            real_value = (
                displayed_balance / ((1 + inflation_rate) ** elapsed_years)
                if inflation_rate > -1
                else displayed_balance
            )
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
    real_final_balance = (
        final_balance / ((1 + inflation_rate) ** years)
        if inflation_rate > -1
        else final_balance
    )

    return SimulationResult(
        data=pd.DataFrame(snapshots),
        final_balance=final_balance,
        total_contributions=total_contributions,
        total_interest=total_interest,
        real_final_balance=real_final_balance,
        total_payment_events=total_payment_events,
    )


def calculate_goal(
    target_amount: float,
    initial_capital: float,
    recurring_payment: float,
    payment_frequency: int,
    annual_payment_increase: float,
    annual_rate: float,
    credit_frequency: int,
    max_years: int = 100,
) -> GoalResult:
    if initial_capital >= target_amount:
        return GoalResult(
            reached=True,
            days_to_goal=0,
            balance_at_goal=initial_capital,
            contributions_at_goal=initial_capital,
            interest_at_goal=0.0,
        )

    days_per_year = 365
    total_days = max_years * days_per_year

    balance = float(initial_capital)
    total_contributions = float(initial_capital)
    accrued_interest = 0.0

    payment_interval = days_per_year / payment_frequency
    credit_interval = days_per_year / credit_frequency
    next_payment_day = payment_interval
    next_credit_day = credit_interval

    daily_rate = annual_rate / days_per_year if annual_rate > -1 else 0

    for day in range(1, total_days + 1):
        current_year_index = (day - 1) // days_per_year
        payment_this_year = recurring_payment * ((1 + annual_payment_increase) ** current_year_index)

        accrued_interest += balance * daily_rate

        while day + 1e-9 >= next_payment_day and next_payment_day <= total_days + 1e-9:
            balance += payment_this_year
            total_contributions += payment_this_year
            next_payment_day += payment_interval

        while day + 1e-9 >= next_credit_day and next_credit_day <= total_days + 1e-9:
            balance += accrued_interest
            accrued_interest = 0.0
            next_credit_day += credit_interval

        displayed_balance = balance + accrued_interest
        if displayed_balance >= target_amount:
            return GoalResult(
                reached=True,
                days_to_goal=day,
                balance_at_goal=displayed_balance,
                contributions_at_goal=total_contributions,
                interest_at_goal=displayed_balance - total_contributions,
            )

    return GoalResult(
        reached=False,
        days_to_goal=None,
        balance_at_goal=None,
        contributions_at_goal=None,
        interest_at_goal=None,
    )


def dataframe_to_excel(df: pd.DataFrame) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Éves kalkuláció")
        worksheet = writer.book["Éves kalkuláció"]

        widths = {
            "A": 12,
            "B": 22,
            "C": 22,
            "D": 22,
            "E": 22,
        }
        for column, width in widths.items():
            worksheet.column_dimensions[column].width = width

        for row in worksheet.iter_rows(min_row=2, min_col=2, max_col=5):
            for cell in row:
                cell.number_format = '#,##0 "Ft"'

    return output.getvalue()


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

    st.divider()

    target_enabled = st.toggle("Célösszeg számítása", value=True)
    target_amount = st.number_input(
        "Célösszeg (Ft)",
        min_value=100_000,
        max_value=10_000_000_000,
        value=100_000_000,
        step=1_000_000,
        disabled=not target_enabled,
    )


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

goal_result = None
if target_enabled:
    goal_result = calculate_goal(
        target_amount=target_amount,
        initial_capital=initial_capital,
        recurring_payment=recurring_payment,
        payment_frequency=PAYMENT_FREQUENCIES[payment_frequency_label],
        annual_payment_increase=annual_payment_increase_pct / 100,
        annual_rate=annual_rate_pct / 100,
        credit_frequency=CREDIT_FREQUENCIES[credit_frequency_label],
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


if target_enabled and goal_result is not None:
    st.markdown("<div class='section-title'>Célösszeg</div>", unsafe_allow_html=True)

    if goal_result.reached:
        duration_text = format_duration(goal_result.days_to_goal or 0)
        within_term = (goal_result.days_to_goal or 0) <= years * 365
        status_text = "A beállított futamidőn belül elérhető." if within_term else "A beállított futamidőn túl érhető el."

        goal_col1, goal_col2, goal_col3 = st.columns(3)
        with goal_col1:
            st.markdown(
                f"""
                <div class="goal-card">
                    <div class="goal-title">Célösszeg</div>
                    <div class="goal-value">{format_huf(target_amount)}</div>
                    <div class="goal-detail">{status_text}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with goal_col2:
            st.markdown(
                f"""
                <div class="goal-card">
                    <div class="goal-title">Becsült elérési idő</div>
                    <div class="goal-value">{duration_text}</div>
                    <div class="goal-detail">A jelenlegi befizetési és hozamfeltételekkel.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with goal_col3:
            st.markdown(
                f"""
                <div class="goal-card">
                    <div class="goal-title">Hozam a cél elérésekor</div>
                    <div class="goal-value">{format_huf(goal_result.interest_at_goal or 0)}</div>
                    <div class="goal-detail">Saját befizetés: {format_huf(goal_result.contributions_at_goal or 0)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.warning(
            "A megadott feltételekkel a célösszeg 100 éven belül sem érhető el. "
            "Növeld a rendszeres befizetést, a futamidőt vagy módosítsd a hozamfeltételezést."
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

if target_enabled:
    fig.add_hline(
        y=target_amount,
        line_dash="dash",
        annotation_text="Célösszeg",
        annotation_position="top left",
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
        st.write(
            f"{format_pct(inflation_rate_pct)} átlagos infláció mellett a nominális végösszeg "
            f"mai vásárlóereje körülbelül **{format_huf(result.real_final_balance)}**."
        )


st.markdown("<div class='section-title'>Éves bontás</div>", unsafe_allow_html=True)

annual_table_display = result.data.copy()
for col in ["Portfólió értéke", "Saját befizetés", "Hozam", "Reálérték"]:
    annual_table_display[col] = annual_table_display[col].map(format_huf)
annual_table_display["Év"] = annual_table_display["Év"].map(lambda x: f"{x:.0f}")

st.dataframe(annual_table_display, use_container_width=True, hide_index=True, height=360)


st.markdown("<div class='section-title'>Eredmények exportálása</div>", unsafe_allow_html=True)
st.caption("A letöltött fájlok az éves bontás számszerű adatait tartalmazzák.")

export_df = result.data.copy()
export_df["Év"] = export_df["Év"].round(0).astype(int)

csv_data = export_df.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig")
excel_data = dataframe_to_excel(export_df)

export_col1, export_col2 = st.columns(2)
with export_col1:
    st.download_button(
        label="CSV letöltése",
        data=csv_data,
        file_name="kamatos_kamat_eves_kalkulacio.csv",
        mime="text/csv",
        use_container_width=True,
    )

with export_col2:
    st.download_button(
        label="Excel letöltése",
        data=excel_data,
        file_name="kamatos_kamat_eves_kalkulacio.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )


st.caption(
    "A kalkulátor becslést készít. A tényleges befektetési hozamok nem garantáltak, és időben változhatnak. "
    "A heti, havi és negyedéves eseményeket a modell egyenletesen osztja el az éven belül."
)
