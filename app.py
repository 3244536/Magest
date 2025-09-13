import streamlit as st
from datetime import datetime, timedelta

# --- Initialisation des données (simulation base de données) ---
if 'clients' not in st.session_state:
    st.session_state.clients = [
        {"id": 1, "nom": "Dupont", "description": "Client fidèle", "tel": "0612345678"},
        {"id": 2, "nom": "Martin", "description": "Nouveau client", "tel": "0687654321"}
    ]
if 'operations' not in st.session_state:
    st.session_state.operations = [
        {"id": 1, "client_id": 1, "valeur": 1580000, "taux": 10, "duree": 6.5, "statut": "en-cours"},
        {"id": 2, "client_id": 2, "valeur": 2300000, "taux": 15, "duree": 3, "statut": "termine"}
    ]
if 'paiements' not in st.session_state:
    st.session_state.paiements = [
        {"id": 1, "client_id": 1, "type": "ordinaire", "montant": 158000, "date": "2025-10-15"},
        {"id": 2, "client_id": 2, "type": "anticipe", "montant": 345000, "date": "2025-09-20"}
    ]

# --- Fonctions utilitaires ---
def format_montant(montant):
    return f"{montant:,}".replace(",", " ")

def get_client_by_id(client_id):
    for client in st.session_state.clients:
        if client["id"] == client_id:
            return client
    return None

# --- Interface Streamlit ---
st.set_page_config(page_title="Gestion Commerciale", layout="wide")
st.title("📊 Gestion des Clients, Opérations et Paiements")
st.markdown("""
<style>
    .stButton>button {
        background-color: #ff6b6b;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
    }
    .stSuccess {
        background-color: #4ecdc4 !important;
    }
    .stWarning {
        background-color: #ffeaa7 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Onglets ---
tab_accueil, tab_clients, tab_operations, tab_paiements = st.tabs(
    ["🏠 Tableau de bord", "👥 Clients", "📦 Opérations", "💰 Paiements"]
)

# --- Onglet Accueil (Tableau de bord) ---
with tab_accueil:
    st.header("Opérations en cours")
    operations_en_cours = [op for op in st.session_state.operations if op["statut"] == "en-cours"]
    if not operations_en_cours:
        st.warning("Aucune opération en cours.")
    else:
        for op in operations_en_cours:
            client = get_client_by_id(op["client_id"])
            montant = int(op["valeur"] * (1 + op["taux"]/100) / op["duree"])
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"**Client :** {client['nom']}")
            with col2:
                st.markdown(f"**Prochaine échéance :** 15/10/2025")
            with col3:
                st.markdown(f"**Montant à payer :** {format_montant(montant)}")
            st.divider()

# --- Onglet Clients ---
with tab_clients:
    st.header("Gestion des Clients")
    # Ajouter un client
    with st.expander("➕ Ajouter un client", expanded=False):
        with st.form("ajouter_client"):
            nom = st.text_input("Nom *", key="nom_client")
            description = st.text_input("Description", key="desc_client")
            tel = st.text_input("Téléphone *", key="tel_client")
            submitted = st.form_submit_button("Ajouter")
            if submitted:
                if nom and tel:
                    new_id = max([c["id"] for c in st.session_state.clients], default=0) + 1
                    st.session_state.clients.append({
                        "id": new_id,
                        "nom": nom,
                        "description": description,
                        "tel": tel
                    })
                    st.success(f"Client {nom} ajouté avec succès !")
                else:
                    st.error("Le nom et le téléphone sont obligatoires.")

    # Liste des clients
    st.subheader("Liste des clients")
    for client in st.session_state.clients:
        with st.expander(f"👤 {client['nom']}"):
            st.write(f"**Description :** {client['description']}")
            st.write(f"**Téléphone :** {client['tel']}")
            if st.button(f"Supprimer {client['nom']}", key=f"suppr_{client['id']}"):
                st.session_state.clients = [c for c in st.session_state.clients if c["id"] != client["id"]]
                st.rerun()

# --- Onglet Opérations ---
with tab_operations:
    st.header("Gestion des Opérations")
    # Ajouter une opération
    with st.expander("➕ Ajouter une opération", expanded=False):
        with st.form("ajouter_operation"):
            client_id = st.selectbox("Client *", [c["id"] for c in st.session_state.clients], format_func=lambda x: get_client_by_id(x)["nom"])
            valeur = st.number_input("Valeur marchandise *", min_value=1, key="valeur_op")
            taux = st.number_input("Taux de bénéfice (%) *", min_value=1, key="taux_op")
            duree = st.number_input("Durée (mois) *", min_value=0.1, format="%.1f", key="duree_op")
            statut = st.selectbox("Statut", ["en-cours", "termine"], key="statut_op")
            submitted = st.form_submit_button("Ajouter")
            if submitted:
                new_id = max([op["id"] for op in st.session_state.operations], default=0) + 1
                st.session_state.operations.append({
                    "id": new_id,
                    "client_id": client_id,
                    "valeur": valeur,
                    "taux": taux,
                    "duree": duree,
                    "statut": statut
                })
                st.success("Opération ajoutée avec succès !")

    # Liste des opérations
    st.subheader("Liste des opérations")
    for op in st.session_state.operations:
        client = get_client_by_id(op["client_id"])
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            st.markdown(f"**Client :** {client['nom']}")
        with col2:
            st.markdown(f"**Valeur :** {format_montant(op['valeur'])}")
        with col3:
            st.markdown(f"**Taux :** {op['taux']}%")
        with col4:
            st.markdown(f"**Durée :** {op['duree']} mois")
        with col5:
            st.markdown(f"**Statut :** {op['statut']}", unsafe_allow_html=True)
        with col6:
            if st.button(f"Supprimer {op['id']}", key=f"suppr_op_{op['id']}"):
                st.session_state.operations = [o for o in st.session_state.operations if o["id"] != op["id"]]
                st.rerun()
        st.divider()

# --- Onglet Paiements ---
with tab_paiements:
    st.header("Gestion des Paiements")
    # Ajouter un paiement
    with st.expander("➕ Ajouter un paiement", expanded=False):
        with st.form("ajouter_paiement"):
            client_id = st.selectbox("Client *", [c["id"] for c in st.session_state.clients], format_func=lambda x: get_client_by_id(x)["nom"])
            type_paiement = st.selectbox("Type de paiement *", ["ordinaire", "anticipe"])
            if type_paiement == "ordinaire":
                montant = st.number_input("Montant (mensualité) *", min_value=1, key="montant_paiement")
            else:
                operation_id = st.selectbox("Opération associée *", [op["id"] for op in st.session_state.operations if op["client_id"] == client_id])
                operation = next(op for op in st.session_state.operations if op["id"] == operation_id)
                montant = int(operation["valeur"] * operation["taux"] / 100)
                st.write(f"Montant calculé : {format_montant(montant)}")
            date = st.date_input("Date *", datetime.now())
            submitted = st.form_submit_button("Ajouter")
            if submitted:
                new_id = max([p["id"] for p in st.session_state.paiements], default=0) + 1
                st.session_state.paiements.append({
                    "id": new_id,
                    "client_id": client_id,
                    "type": type_paiement,
                    "montant": montant,
                    "date": date.strftime("%Y-%m-%d")
                })
                st.success("Paiement ajouté avec succès !")

    # Liste des paiements
    st.subheader("Liste des paiements")
    for paiement in st.session_state.paiements:
        client = get_client_by_id(paiement["client_id"])
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.markdown(f"**Client :** {client['nom']}")
        with col2:
            st.markdown(f"**Type :** {paiement['type']}")
        with col3:
            st.markdown(f"**Montant :** {format_montant(paiement['montant'])}")
        with col4:
            st.markdown(f"**Date :** {paiement['date']}")
        with col5:
            if st.button(f"Supprimer {paiement['id']}", key=f"suppr_paiement_{paiement['id']}"):
                st.session_state.paiements = [p for p in st.session_state.paiements if p["id"] != paiement["id"]]
                st.rerun()
        st.divider()
