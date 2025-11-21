import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Configuration de la page
st.set_page_config(
    page_title="GetAround Analysis",
    page_icon="🚗",
    layout="wide"
)

# --- CHARGEMENT ET PRÉPARATION DES DONNÉES ---
@st.cache_data
def load_and_process_data():
    # Chargement depuis l'URL
    url = "https://full-stack-assets.s3.eu-west-3.amazonaws.com/Deployment/get_around_delay_analysis.xlsx"
    df = pd.read_excel(url)
    
    # Nettoyage basique
    df = df.rename(columns=lambda col: col.replace('_in_minutes', '') if col.endswith('_in_minutes') else col)
    df['checkin_type'] = df['checkin_type'].astype('category')
    df['state'] = df['state'].astype('category')
    
    # Création des données pour les locations enchainées (Merge)
    df_previous = df[['rental_id', 'delay_at_checkout']].copy()
    df_previous.columns = ['rental_id_prev', 'previous_delay_at_checkout']
    
    df_join = df.merge(df_previous, left_on='previous_ended_rental_id', right_on='rental_id_prev', how='inner')
    
    # Logique : Un cas est problématique si le retard précédent est supérieur au temps de battement prévu
    df_join['is_problematic'] = (df_join['previous_delay_at_checkout'] > df_join['time_delta_with_previous_rental'])
    
    return df, df_join

try:
    df, df_join = load_and_process_data()
except Exception as e:
    st.error(f"Erreur lors du chargement des données : {e}")
    st.stop()

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Aller vers", ["Aperçu & Problèmes", "Simulation & Seuil"])

# --- PAGE 1 : APERÇU & PROBLÈMES ---
if page == "Aperçu & Problèmes":
    
    st.markdown("<h1 style='text-align: center;'>Analyse d'impact des retards sur la location de véhicule</h1>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # --- SECTION 1 : APERÇU ---
    st.markdown("### Aperçu des données")
    st.markdown("---") # Trait fin

    # Métriques Globales
    total_rentals = len(df)
    consecutive_rentals = len(df_join)
    percent_consecutive = (consecutive_rentals / total_rentals) * 100

    col1, col2, col3 = st.columns([1, 2, 1]) # Centrage visuel
    with col2:
        c1, c2 = st.columns(2)
        c1.metric("Nombre de locations total", f"{total_rentals:,}".replace(",", " "))
        c2.metric("Locations enchaînées", f"{consecutive_rentals:,}".replace(",", " "), delta=f"{percent_consecutive:.1f} % du total", delta_color="off")

    st.markdown("<br>", unsafe_allow_html=True)

    # 3 Donuts sur une ligne
    col_d1, col_d2, col_d3 = st.columns(3)

    # Donut 1 : Proportion des retards
    df_delay_clean = df.dropna(subset=['delay_at_checkout'])
    late_count = df_delay_clean[df_delay_clean['delay_at_checkout'] > 0].shape[0]
    on_time_count = len(df_delay_clean) - late_count
    
    fig_donut1 = px.pie(
        names=['En retard', "À l'heure"],
        values=[late_count, on_time_count],
        color_discrete_sequence=['#ef553b', '#00CC96'],
        hole=0.5
    )
    # Mise à jour : Légende visible en bas
    fig_donut1.update_layout(
        title_text="Proportion des retards", title_x=0.3,
        showlegend=True, 
        legend=dict(orientation="h", y=-0.1),
        margin=dict(t=40, b=20, l=0, r=0)
    )
    # CORRECTION WARNING : width="stretch" au lieu de use_container_width=True
    col_d1.plotly_chart(fig_donut1, width="stretch")

    # Donut 2 : Check-in Type
    checkin_counts = df['checkin_type'].value_counts().reset_index()
    checkin_counts.columns = ['Type', 'Count']
    fig_donut2 = px.pie(
        checkin_counts, values='Count', names='Type',
        color='Type',
        color_discrete_map={'mobile':'#636EFA', 'connect':'#AB63FA'},
        hole=0.5
    )
    fig_donut2.update_layout(
        title_text="Type de check-in", title_x=0.35,
        showlegend=True, 
        legend=dict(orientation="h", y=-0.1),
        margin=dict(t=40, b=20, l=0, r=0)
    )
    col_d2.plotly_chart(fig_donut2, width="stretch")

    # Donut 3 : État des locations
    state_counts = df['state'].value_counts().reset_index()
    state_counts.columns = ['State', 'Count']
    fig_donut3 = px.pie(
        state_counts, values='Count', names='State',
        color='State',
        color_discrete_map={'ended':'#00CC96', 'canceled':'#ef553b'},
        hole=0.5
    )
    fig_donut3.update_layout(
        title_text="État des locations", title_x=0.35,
        showlegend=True, 
        legend=dict(orientation="h", y=-0.1),
        margin=dict(t=40, b=20, l=0, r=0)
    )
    col_d3.plotly_chart(fig_donut3, width="stretch")

    # --- SECTION 2 : CAS PROBLÉMATIQUES ---
    st.markdown("### Cas problématiques (frictions)")
    st.markdown("---")

    # Calcul des KPIs Friction
    prob_count = df_join['is_problematic'].sum()
    prob_total = len(df_join)
    median_delay_prob = df_join[df_join['is_problematic']]['delay_at_checkout'].median()
    cancel_prob = df_join[(df_join['is_problematic']) & (df_join['state'] == 'canceled')].shape[0]

    col_fric_1, col_fric_2 = st.columns([1, 1])

    with col_fric_1:
        # Donut Friction
        # IMPORTANT : On passe les valeurs dans l'ordre [Friction, Sans impact]
        # Et on met sort=False pour que Plotly respecte notre ordre et donc nos couleurs
        fig_fric = px.pie(
            names=['Friction', 'Sans impact'],
            values=[prob_count, prob_total - prob_count],
            title="Proportion des frictions",
            color_discrete_sequence=['#ef553b', '#d3d3d3'], # Rouge pour Friction, Gris clair pour le reste
            hole=0.6
        )
        # Annotation au centre
        fig_fric.add_annotation(text=f"{prob_count/prob_total:.1%}", showarrow=False, font_size=25, font_color="#ef553b", font_weight="bold")
        
        # sort=False empêche Plotly de mettre la plus grosse part (gris) en premier (rouge)
        fig_fric.update_traces(sort=False) 
        
        fig_fric.update_layout(showlegend=True, legend=dict(orientation="h", y=0), margin=dict(t=40, b=20, l=0, r=0))
        st.plotly_chart(fig_fric, width="stretch")

    with col_fric_2:
        # 3 Chiffres alignés verticalement avec un peu de style
        st.markdown("#### Détails des impacts")
        st.markdown("<br>", unsafe_allow_html=True) 
        
        # On utilise des colonnes vides pour centrer un peu ou aérer si besoin
        st.metric("Nombre de cas problématiques", f"{prob_count}")
        st.markdown("---")
        st.metric("Médiane du retard (cas problématiques)", f"{median_delay_prob:.0f} min")
        st.markdown("---")
        st.metric("Annulations suite à friction", f"{cancel_prob}")


# --- PAGE 2 : SIMULATION ---
elif page == "Simulation & Seuil":
    
    st.title("Seuil (Threshold) & Périmètre (Scope)")

    # --- CONTROLS ---
    col_control1, col_control2 = st.columns([1, 2])
    
    with col_control1:
        scope_option = st.radio(
            "Sélectionnez le périmètre :",
            ('Tous les véhicules', 'Mobile', 'Connect'),
            horizontal=True
        )
    
    with col_control2:
        threshold = st.slider(
            "Déterminez le seuil (temps de battement minimum entre deux locations) :",
            min_value=0,
            max_value=300, # 5 heures
            step=30,
            value=60
        )

    # --- FILTRAGE DES DONNÉES POUR LA SIMULATION ---
    
    # Filtrage du scope (Périmètre)
    if scope_option == 'Mobile':
        current_df_join = df_join[df_join['checkin_type'] == 'mobile'].copy()
        total_rentals_scope = len(df[df['checkin_type'] == 'mobile'])
    elif scope_option == 'Connect':
        current_df_join = df_join[df_join['checkin_type'] == 'connect'].copy()
        total_rentals_scope = len(df[df['checkin_type'] == 'connect'])
    else:
        current_df_join = df_join.copy()
        total_rentals_scope = len(df)

    # --- CALCUL DE LA SIMULATION (COURBES) ---
    # On calcule pour TOUS les seuils pour tracer les courbes
    sim_thresholds = range(0, 301, 15) # Step plus fin pour le graph
    results = []

    for t in sim_thresholds:
        # Solution : On résout les cas qui étaient problématiques ET qui ont un delta < t
        # (Car on suppose qu'on aurait refusé la 2eme location, donc plus de problème de retard)
        solved_count = current_df_join[
            (current_df_join['is_problematic'] == True) & 
            (current_df_join['time_delta_with_previous_rental'] < t)
        ].shape[0]
        
        # Coût : On perd TOUTES les locations (enchaînées) qui ont un delta < t
        lost_count = current_df_join[
            current_df_join['time_delta_with_previous_rental'] < t
        ].shape[0]
        
        results.append({
            'threshold': t,
            'solved': solved_count,
            'lost': lost_count,
            'preserved_percent': ((total_rentals_scope - lost_count) / total_rentals_scope) * 100
        })

    df_sim = pd.DataFrame(results)

    # --- VISUALISATIONS ---
    col_graph1, col_graph2 = st.columns(2)

    with col_graph1:
        # Graphique 1 : Coût vs Bénéfice
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=df_sim['threshold'], y=df_sim['lost'], mode='lines', name='Locations perdues (Coût)', line=dict(color='#ef553b', width=3)))
        fig1.add_trace(go.Scatter(x=df_sim['threshold'], y=df_sim['solved'], mode='lines', name='Problèmes résolus (Bénéfice)', line=dict(color='#00cc96', width=3)))
        
        # Ligne verticale pour le seuil choisi
        fig1.add_vline(x=threshold, line_width=2, line_dash="dash", line_color="grey")
        
        fig1.update_layout(
            title="Compromis Coût / Bénéfice",
            xaxis_title="Seuil (min)",
            yaxis_title="Nombre de locations",
            legend=dict(x=0.01, y=0.99),
            height=400
        )
        st.plotly_chart(fig1, width="stretch")

    with col_graph2:
        # Graphique 2 : Volume préservé
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=df_sim['threshold'], y=df_sim['preserved_percent'], mode='lines', name='% Volume préservé', line=dict(color='#636EFA', width=3)))
        
        # Ligne verticale pour le seuil choisi
        fig2.add_vline(x=threshold, line_width=2, line_dash="dash", line_color="grey")
        
        fig2.update_layout(
            title="Impact sur le chiffre d'affaires global",
            xaxis_title="Seuil (min)",
            yaxis_title="% Volume Préservé",
            yaxis_range=[80, 101],
            height=400
        )
        st.plotly_chart(fig2, width="stretch")

    # --- CHIFFRES CLÉS (ENCADRÉ) ---
    
    # Récupération des chiffres exacts pour le seuil sélectionné par l'utilisateur
    # On ne prend pas dans df_sim car le step du slider (30) peut différer du step de simulation (15)
    # On recalcule à la volée pour être précis
    
    metric_solved = current_df_join[
        (current_df_join['is_problematic'] == True) & 
        (current_df_join['time_delta_with_previous_rental'] < threshold)
    ].shape[0]
    
    metric_lost = current_df_join[
        current_df_join['time_delta_with_previous_rental'] < threshold
    ].shape[0]
    
    metric_preserved_pct = ((total_rentals_scope - metric_lost) / total_rentals_scope) * 100
    
    # Calcul du pourcentage de problèmes résolus par rapport au total des problèmes du scope
    total_problems_in_scope = current_df_join['is_problematic'].sum()
    if total_problems_in_scope > 0:
        pct_solved_problems = (metric_solved / total_problems_in_scope) * 100
    else:
        pct_solved_problems = 0

    # Affichage style "Dashboard"
    st.markdown(f"""
    <div style="background-color: #F0F2F6; padding: 20px; border-radius: 10px; border: 1px solid #d1d1d1;">
        <h3 style="color: #31333F; margin-top: 0;">Résultats pour un seuil de <span style="color: #FF4B4B;">{threshold} minutes</span> ({scope_option})</h3>
        <div style="display: flex; justify-content: space-around; text-align: center;">
            <div>
                <h4 style="color: #00cc96; margin-bottom: 0;">Problèmes résolus</h4>
                <p style="font-size: 24px; font-weight: bold; margin: 0;">{metric_solved} <span style="font-size: 16px; font-weight: normal;">({pct_solved_problems:.1f}%)</span></p>
            </div>
            <div style="border-left: 1px solid #ccc; margin: 0 15px;"></div>
            <div>
                <h4 style="color: #ef553b; margin-bottom: 0;">Locations perdues</h4>
                <p style="font-size: 24px; font-weight: bold; margin: 0;">{metric_lost} <span style="font-size: 16px; font-weight: normal;">({(metric_lost/total_rentals_scope)*100:.1f}%)</span></p>
            </div>
            <div style="border-left: 1px solid #ccc; margin: 0 15px;"></div>
            <div>
                <h4 style="color: #636EFA; margin-bottom: 0;">Volume préservé</h4>
                <p style="font-size: 24px; font-weight: bold; margin: 0;">{metric_preserved_pct:.1f} %</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)