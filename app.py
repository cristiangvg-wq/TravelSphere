import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, timedelta
from urllib.parse import quote_plus

from travelsphere.data import build_demo_results
from travelsphere.utils import money, search_url, duration_days

st.set_page_config(page_title="TravelSphere · Your journey, reimagined", page_icon="✦", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
:root{--bg:#080b14;--panel:rgba(21,27,45,.72);--line:rgba(164,180,255,.16);--muted:#9ba8c7;--text:#edf1ff;--cyan:#7ce7f2;--violet:#a994ff;}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;color:var(--text)}
.stApp{background:radial-gradient(ellipse at 12% 0%,rgba(76,64,170,.22),transparent 35%),radial-gradient(ellipse at 88% 15%,rgba(28,142,164,.15),transparent 30%),var(--bg)}
.block-container{max-width:1440px;padding-top:1.5rem;padding-bottom:3rem}
h1,h2,h3,.brand{font-family:'Space Grotesk',sans-serif!important;letter-spacing:-.035em}
.hero{padding:2rem 0 1.5rem;position:relative}.eyebrow{color:var(--cyan);font-size:.76rem;letter-spacing:.2em;text-transform:uppercase;font-weight:700}
.hero h1{font-size:clamp(2.6rem,5vw,4.8rem);line-height:1.02;margin:.55rem 0 1rem;background:linear-gradient(100deg,#fff 15%,#b7baff 56%,#7ce7f2);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.sub{color:var(--muted);font-size:1.05rem;max-width:680px;line-height:1.7}
.glass{background:linear-gradient(135deg,rgba(34,43,70,.78),rgba(17,22,38,.68));border:1px solid var(--line);border-radius:22px;padding:1.2rem 1.3rem;box-shadow:0 18px 50px rgba(0,0,0,.18);backdrop-filter:blur(18px);transition:transform .25s ease,border-color .25s ease}
.glass:hover{transform:translateY(-3px);border-color:rgba(124,231,242,.38)}
.metric{font-size:1.8rem;font-weight:700;font-family:'Space Grotesk';margin:.35rem 0}.muted{color:var(--muted);font-size:.9rem}.pill{display:inline-block;padding:.28rem .6rem;border:1px solid rgba(124,231,242,.25);border-radius:999px;color:var(--cyan);font-size:.75rem;margin-right:.3rem}
.card-title{font-family:'Space Grotesk';font-size:1.13rem;font-weight:600;margin:.35rem 0}.card-price{font-size:1.55rem;font-weight:700;color:#fff;margin:.55rem 0}.card-price small{font-size:.8rem;color:var(--muted);font-weight:400}
.stButton>button, .stLinkButton>a{border-radius:12px;border:1px solid rgba(124,231,242,.3);background:linear-gradient(110deg,rgba(124,231,242,.16),rgba(169,148,255,.16));color:#f5f7ff;font-weight:600;transition:all .2s ease}.stButton>button:hover,.stLinkButton>a:hover{border-color:var(--cyan);transform:translateY(-1px)}
[data-baseweb="tab-list"]{gap:.45rem;background:rgba(16,21,36,.7);padding:.45rem;border:1px solid var(--line);border-radius:16px}
[data-baseweb="tab"]{border-radius:11px;padding:.6rem 1rem}.stTabs [aria-selected="true"]{background:rgba(124,231,242,.12);color:var(--cyan)}
label,.stMarkdown p{color:var(--text)}.stTextInput input,.stNumberInput input,.stDateInput input,.stSelectbox div[data-baseweb="select"]{background:rgba(9,13,25,.8);border-color:var(--line);border-radius:10px}
hr{border-color:var(--line)}.footer{color:#71809f;text-align:center;font-size:.8rem;padding-top:2rem}
@keyframes floatIn{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}.hero,.glass{animation:floatIn .55s ease both}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero"><div class="eyebrow">✦ THE ART OF GETTING AWAY</div><h1>TravelSphere</h1><div class="sub">Diseña viajes que se sienten extraordinarios. Explora vuelos, estancias, sabores y experiencias desde un solo espacio.</div></div>', unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown("### ✧ Construye tu viaje")
    c1,c2,c3 = st.columns(3)
    with c1:
        origin = st.text_input("Origen · ciudad o aeropuerto", "Bogotá, Colombia", placeholder="Ej. Bogotá, Colombia")
        departure = st.date_input("Fecha de ida", date.today()+timedelta(days=30), min_value=date.today())
    with c2:
        destination = st.text_input("Destino · ciudad o país", "Ciudad de México, México", placeholder="Ej. Lisboa, Portugal")
        return_date = st.date_input("Fecha de regreso", date.today()+timedelta(days=37), min_value=date.today())
    with c3:
        adults = st.number_input("Adultos", min_value=1, max_value=20, value=2)
        children = st.number_input("Niños", min_value=0, max_value=20, value=0)
    c4,c5,c6 = st.columns(3)
    with c4:
        budget = st.number_input("Presupuesto total estimado (COP)", min_value=100000, value=6000000, step=250000, format="%d")
    with c5:
        style = st.selectbox("Estilo de viaje", ["Cultural", "Aventura", "Relax", "Gastronómico", "Lujo", "Familiar", "Económico"])
    with c6:
        currency = st.selectbox("Moneda de visualización", ["COP", "USD", "EUR"], index=0)
    submitted = st.button("✦ Crear mi TravelSphere", type="primary", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

if return_date < departure:
    st.error("La fecha de regreso debe ser igual o posterior a la fecha de ida.")
    st.stop()

if submitted:
    st.session_state["trip"] = {"origin":origin,"destination":destination,"departure":departure,"return_date":return_date,"adults":adults,"children":children,"budget":budget,"style":style,"currency":currency}
trip = st.session_state.get("trip", {"origin":origin,"destination":destination,"departure":departure,"return_date":return_date,"adults":adults,"children":children,"budget":budget,"style":style,"currency":currency})

if not trip["origin"].strip() or not trip["destination"].strip():
    st.info("Completa el origen y el destino para personalizar la propuesta.")
    st.stop()
if trip["return_date"] < trip["departure"]:
    st.error("Revisa las fechas del viaje."); st.stop()

nights = max(1, duration_days(trip["departure"],trip["return_date"]))
results = build_demo_results(trip, nights)
people = int(trip["adults"]+trip["children"])

st.markdown("<div style='height:1rem'></div>",unsafe_allow_html=True)
st.markdown(f"<div class='eyebrow'>YOUR JOURNEY AT A GLANCE</div><h2>{trip['origin']} <span style='color:#7ce7f2'>→</span> {trip['destination']}</h2>",unsafe_allow_html=True)
m1,m2,m3,m4 = st.columns(4)
for col, label, value, note in [
    (m1,"Duración",f"{nights} noches",f"{trip['departure'].strftime('%d %b')} — {trip['return_date'].strftime('%d %b %Y')}"),
    (m2,"Viajeros",str(people),f"{trip['adults']} adultos · {trip['children']} niños"),
    (m3,"Presupuesto",money(trip['budget'],trip['currency']),"Tope estimado del viaje"),
    (m4,"Tu estilo",trip['style'],"Curado para ti")]:
    with col: st.markdown(f"<div class='glass'><div class='muted'>{label}</div><div class='metric'>{value}</div><div class='muted'>{note}</div></div>",unsafe_allow_html=True)

st.markdown("<div style='height:1rem'></div>",unsafe_allow_html=True)
tabs = st.tabs(["✈️  Vuelos", "⌂  Hoteles", "✦  Gastronomía", "◷  Itinerario", "◈  Finanzas"])

with tabs[0]:
    st.markdown("### Tiquetes aéreos")
    st.caption("Precios y tiempos son ilustrativos para prototipado; confirma tarifas y disponibilidad en el proveedor antes de comprar.")
    f1,f2 = st.columns(2)
    with f1: airline_filter = st.multiselect("Aerolínea", sorted({x['airline'] for x in results['flights']}), default=sorted({x['airline'] for x in results['flights']}))
    with f2: stops_filter = st.multiselect("Escalas", ["Directo", "1 escala", "2+ escalas"], default=["Directo","1 escala","2+ escalas"])
    shown = [x for x in results['flights'] if x['airline'] in airline_filter and x['stops'] in stops_filter]
    if not shown: st.warning("No hay opciones con esos filtros. Prueba ampliarlos.")
    for x in shown:
        a,b = st.columns([4,1])
        with a: st.markdown(f"<div class='glass'><span class='pill'>{x['airline']}</span><span class='pill'>{x['stops']}</span><div class='card-title'>{x['depart']} → {x['arrive']}</div><div class='muted'>{x['duration']} · {x['baggage']}</div><div class='card-price'>{money(x['price']*people,trip['currency'])} <small>ida y vuelta · grupo</small></div></div>",unsafe_allow_html=True)
        with b:
            st.write("")
            st.link_button("Kayak ↗",search_url("kayak",trip))
            st.link_button("Skyscanner ↗",search_url("skyscanner",trip))
            st.link_button("Google Flights ↗",search_url("google_flights",trip))

with tabs[1]:
    st.markdown("### Hospedaje & hoteles")
    st.caption("Opciones de ejemplo: no representan disponibilidad ni tarifas verificadas.")
    for x in results['hotels']:
        left,right=st.columns([4,1])
        with left:
            amenities = " · ".join(x['amenities'])
            st.markdown(f"<div class='glass'><span class='pill'>{x['kind']}</span><span class='pill'>★ {x['rating']}</span><div class='card-title'>{x['name']}</div><div class='muted'>⌖ {x['area']} · {amenities}</div><div class='card-price'>{money(x['nightly']*nights,trip['currency'])} <small>total estimado · {nights} noches</small></div></div>",unsafe_allow_html=True)
        with right:
            st.write("")
            st.link_button("Booking ↗",search_url("booking",trip))
            st.link_button("Airbnb ↗",search_url("airbnb",trip))
            st.link_button("Ver mapa ↗",search_url("maps",trip))

with tabs[2]:
    st.markdown("### Gastronomía & restaurantes")
    r1,r2=st.columns(2)
    with r1: cuisine=st.selectbox("Tipo de cocina",["Todas","Local","Mexicana","Internacional","Vegetariana","Mariscos"])
    with r2: price_level=st.selectbox("Rango de precio",["Todos","Económico","Moderado","Premium"])
    for x in results['restaurants']:
        if cuisine!="Todas" and x['cuisine'] not in [cuisine,"Local"]: continue
        if price_level!="Todos" and x['price_level']!=price_level: continue
        st.markdown(f"<div class='glass'><span class='pill'>{x['cuisine']}</span><span class='pill'>{x['price_level']}</span><span class='pill'>★ {x['rating']}</span><div class='card-title'>{x['name']}</div><div class='muted'>{x['description']}</div><div class='card-price'>{money(x['avg_cost']*people,trip['currency'])} <small>estimado para {people} personas</small></div></div>",unsafe_allow_html=True)
        q=quote_plus(f"{x['name']} {trip['destination']}")
        c1,c2=st.columns(2)
        with c1: st.link_button("Google Maps ↗",f"https://www.google.com/maps/search/?api=1&query={q}")
        with c2: st.link_button("Tripadvisor ↗",f"https://www.tripadvisor.com/Search?q={q}")

with tabs[3]:
    st.markdown("### Itinerario sugerido")
    st.caption("Plan orientativo generado con datos de demostración. Ajusta actividades según horarios, clima y disponibilidad.")
    for day in results['itinerary']:
        with st.expander(f"Día {day['day']} · {day['title']}", expanded=day['day']==1):
            for item in day['items']:
                st.markdown(f"**{item['time']} · {item['name']}**  \n{item['description']}  \n<span class='muted'>Costo estimado por persona: {money(item['cost'],trip['currency'])}</span>",unsafe_allow_html=True)
                c1,c2=st.columns([1,5])
                with c1: st.link_button("Entradas ↗",f"https://www.getyourguide.com/s/?q={quote_plus(item['name']+' '+trip['destination'])}")
            st.markdown(f"**Estimado por persona para el día:** {money(sum(i['cost'] for i in day['items']),trip['currency'])}")

with tabs[4]:
    st.markdown("### Resumen financiero")
    st.caption("Distribución ilustrativa del presupuesto. No es una cotización ni incluye necesariamente todos los gastos.")
    categories = results['budget_breakdown']
    total_est = sum(categories.values())
    spent_pct = min(100, round(total_est/max(1,trip['budget'])*100))
    c1,c2=st.columns([3,2])
    with c1:
        df=pd.DataFrame([{"Categoría":k,"Costo estimado":v} for k,v in categories.items()])
        fig=px.pie(df,values="Costo estimado",names="Categoría",hole=.68,template="plotly_dark")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",margin=dict(t=15,b=15,l=5,r=5),legend=dict(orientation="h",y=-.08))
        st.plotly_chart(fig,use_container_width=True)
    with c2:
        st.markdown(f"<div class='glass'><div class='muted'>Costo total estimado</div><div class='metric'>{money(total_est,trip['currency'])}</div><div class='muted'>Presupuesto disponible: {money(trip['budget']-total_est,trip['currency']) if trip['budget']>=total_est else 'Excedido por '+money(total_est-trip['budget'],trip['currency'])}</div><hr><div class='muted'>Uso del presupuesto</div><div class='metric'>{spent_pct}%</div><div style='height:8px;background:#202943;border-radius:9px;overflow:hidden'><div style='height:8px;width:{spent_pct}%;background:linear-gradient(90deg,#7ce7f2,#a994ff);border-radius:9px'></div></div></div>",unsafe_allow_html=True)
        st.markdown("**Desglose**")
        for k,v in categories.items(): st.write(f"{k}: **{money(v,trip['currency'])}**")
    st.download_button("↓ Descargar presupuesto CSV",pd.DataFrame([{"Categoría":k,"Costo estimado":v} for k,v in categories.items()]).to_csv(index=False).encode('utf-8-sig'),file_name="travelsphere-presupuesto.csv",mime="text/csv",use_container_width=True)

st.markdown("<div class='footer'>TRAVELSPHERE · Planifica con intención, viaja sin límites.<br>Demo UI · Los precios, puntuaciones y recomendaciones son ilustrativos; valida la información con proveedores externos.</div>",unsafe_allow_html=True)
