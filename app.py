import streamlit as st
from datetime import datetime, timedelta

# --- Initialisation des données ---
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
    return "{:,.0f}".format(montant).replace(",", " ")

def get_client_by_id(client_id):
    return next((c for c in st.session_state.clients if c["id"] == client_id), None)

def get_operation_by_id(op_id):
    return next((op for op in st.session_state.operations if op["id"] == op_id), None)

# --- Styles CSS personnalisés ---
st.markdown("""
<style>
    /* Style général */
    .stButton>button {
        border-radius: 5px;
        padding: 5px 15px;
        font-weight: bold;
        border: none;
    }
    /* Style pour les opérations */
    .operation-card {
        background-color: #e3f2fd;
        border-left: 5px solid #2196F3;
        padding: 10px;
        margin: 10px 0;
        border-radius: 5px;
    }
    /* Style pour les paiements */
    .paiement-card {
        background-color: #f1f8e9;
        border-left: 5px solid #8bc34a;
        padding: 10px;
        margin: 10px 0;
        border-radius: 5px;
    }
    /* Style pour les statuts */
    .statut-en-cours {
        color: #2196F3;
        font-weight: bold;
    }
    .statut-termine {
        color: #8bc34a;
        font-weight: bold;
    }
    /* Style pour les onglets */
    .stTabs [data-baseweb="tab"] {
        background-color: #ff6b6b;
        color: white;
        border-radius: 5px 5px 0 0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ff8fab !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Interface Streamlit ---
st.set_page_config(page_title="Gestion Commerciale", layout="wide")
st.title("📊 Gestion des Clients, Opérations et Paiements")

# --- Onglets ---
tab_accueil, tab_clients, tab_operations, tab_paiements = st.tabs(
    ["🏠 Tableau de bord", "👥 Clients", "📦 Opérations", "💰 Paiements"]
)

# --- Onglet Accueil (Tableau de bord) ---
with tab_accueil:
    st.header("📊 Tableau de bord")
    st.subheader("Opérations en cours")
    operations_en_cours = [op for op in st.session_state.operations if op["statut"] == "en-cours"]

    if not operations_en_cours:
        st.warning("Aucune opération en cours.")
    else:
        for op in operations_en_cours:
            client = get_client_by_id(op["client_id"])
            if client:
                # Calcul de la mensualité
                mensualite = (op["valeur"] * (1 + op["taux"]/100)) / op["duree"]
                # Date d'échéance simulée
                echeance = (datetime.now() + timedelta(days=30)).strftime("%d/%m/%Y")

                st.markdown(f"""
                <div class="operation-card">
                    <p><strong>Client :</strong> {client['nom']}</p>
                    <p><strong>Valeur marchandise :</strong> {format_montant(op['valeur'])}</p>
                    <p><strong>Prochaine échéance :</strong> {echeance}</p>
                    <p><strong>Montant à payer :</strong> {format_montant(int(mensualite))}</p>
                    <p><strong>Statut :</strong> <span class="statut-en-cours">{op['statut']}</span></p>
                </div>
                """, unsafe_allow_html=True)

# --- Onglet Clients ---
with tab_clients:
    st.header("👥 Gestion des Clients")
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
                    st.success(f"✅ Client {nom} ajouté avec succès !")
                else:
                    st.error("❌ Le nom et le téléphone sont obligatoires.")

    # Liste des clients
    st.subheader("Liste des clients")
    for client in st.session_state.clients:
        with st.expander(f"👤 {client['nom']}"):
            st.write(f"**Description :** {client['description']}")
            st.write(f"**Téléphone :** {client['tel']}")
            if st.button(f"🗑️ Supprimer {client['nom']}", key=f"suppr_client_{client['id']}"):
                st.session_state.clients = [c for c in st.session_state.clients if c["id"] != client["id"]]
                st.rerun()

# --- Onglet Opérations ---
with tab_operations:
    st.header("📦 Gestion des Opérations")
    # Ajouter une opération
    with st.expander("➕ Ajouter une opération", expanded=False):
        with st.form("ajouter_operation"):
            client_id = st.selectbox(
                "Client *",
                options=st.session_state.clients,
                format_func=lambda x: x["nom"],
                key="client_op"
            )
            valeur = st.number_input("Valeur marchandise *", min_value=1, key="valeur_op")
            taux = st.number_input("Taux de bénéfice (%) *", min_value=1, key="taux_op")
            duree = st.number_input("Durée (mois) *", min_value=0.1, format="%.1f", key="duree_op")
            statut = st.selectbox("Statut", ["en-cours", "termine"], key="statut_op")
            submitted = st.form_submit_button("Ajouter")
            if submitted:
                new_id = max([op["id"] for op in st.session_state.operations], default=0) + 1
                st.session_state.operations.append({
                    "id": new_id,
                    "client_id": client_id["id"],
                    "valeur": valeur,
                    "taux": taux,
                    "duree": duree,
                    "statut": statut
                })
                st.success("✅ Opération ajoutée avec succès !")

    # Liste des opérations
    st.subheader("Liste des opérations")
    for op in st.session_state.operations:
        client = get_client_by_id(op["client_id"])
        if client:
            st.markdown(f"""
            <div class="operation-card">
                <p><strong>Client :</strong> {client['nom']}</p>
                <p><strong>Valeur :</strong> {format_montant(op['valeur'])}</p>
                <p><strong>Taux :</strong> {op['taux']}%</p>
                <p><strong>Durée :</strong> {op['duree']} mois</p>
                <p><strong>Statut :</strong> <span class="statut-{op['statut']}">{op['statut']}</span></p>
                <div>
                    {st.button(f"🗑️ Supprimer", key=f"suppr_op_{op['id']}")}
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Supprimer {op['id']}", key=f"suppr_op_hidden_{op['id']}"):
                st.session_state.operations = [o for o in st.session_state.operations if o["id"] != op["id"]]
                st.rerun()

# --- Onglet Paiements ---
with tab_paiements:
    st.header("💰 Gestion des Paiements")
    # Ajouter un paiement
    with st.expander("➕ Ajouter un paiement", expanded=False):
        with st.form("ajouter_paiement"):
            client_id = st.selectbox(
                "Client *",
                options=st.session_state.clients,
                format_func=lambda x: x["nom"],
                key="client_paiement"
            )
            type_paiement = st.selectbox("Type de paiement *", ["ordinaire", "anticipe"], key="type_paiement")
            if type_paiement == "ordinaire":
                montant = st.number_input("Montant (mensualité) *", min_value=1, key="montant_paiement")
            else:
                operation_id = st.selectbox(
                    "Opération associée *",
                    options=[op for op in st.session_state.operations if op["client_id"] == client_id["id"]],
                    format_func=lambda x: f"Opération {x['id']} - {format_montant(x['valeur'])}",
                    key="operation_paiement"
                )
                if operation_id:
                    montant = int(operation_id["valeur"] * operation_id["taux"] / 100)
                    st.write(f"💡 Montant calculé : {format_montant(montant)}")
                else:
                    montant = 0
            date = st.date_input("Date *", datetime.now(), key="date_paiement")
            submitted = st.form_submit_button("Ajouter")
            if submitted:
                new_id = max([p["id"] for p in st.session_state.paiements], default=0) + 1
                st.session_state.paiements.append({
                    "id": new_id,
                    "client_id": client_id["id"],
                    "type": type_paiement,
                    "montant": montant,
                    "date": date.strftime("%Y-%m-%d")
                })
                st.success("✅ Paiement ajouté avec succès !")

    # Liste des paiements
    st.subheader("Liste des paiements")
    for paiement in st.session_state.paiements:
        client = get_client_by_id(paiement["client_id"])
        if client:
            st.markdown(f"""
            <div class="paiement-card">
                <p><strong>Client :</strong> {client['nom']}</p>
                <p><strong>Type :</strong> {paiement['type']}</p>
                <p><strong>Montant :</strong> {format_montant(paiement['montant'])}</p>
                <p><strong>Date :</strong> {paiement['date']}</p>
                <div>
                    {st.button(f"🗑️ Supprimer", key=f"suppr_paiement_{paiement['id']}")}
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Supprimer {paiement['id']}", key=f"suppr_paiement_hidden_{paiement['id']}"):
                st.session_state.paiements = [p for p in st.session_state.paiements if p["id"] != paiement["id"]]
                st.rerun()
