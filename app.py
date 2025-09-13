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
        {"id": 1, "client_id": 1, "valeur": 1580000, "taux": 10, "duree": 6.5, "statut": "en-cours", "date_debut": "2025-01-01"},
        {"id": 2, "client_id": 1, "valeur": 2000000, "taux": 12, "duree": 4, "statut": "en-cours", "date_debut": "2025-02-15"},
        {"id": 3, "client_id": 2, "valeur": 2300000, "taux": 15, "duree": 3, "statut": "termine", "date_debut": "2024-11-10"}
    ]
if 'paiements' not in st.session_state:
    st.session_state.paiements = [
        {"id": 1, "client_id": 1, "operation_id": 1, "type": "ordinaire", "montant": 158000, "date": "2025-10-15"},
        {"id": 2, "client_id": 2, "operation_id": 3, "type": "anticipe", "montant": 345000, "date": "2025-09-20"}
    ]

# --- Fonctions utilitaires ---
def format_montant(montant):
    return "{:,.0f}".format(montant).replace(",", " ")

def get_client_by_id(client_id):
    return next((c for c in st.session_state.clients if c["id"] == client_id), None)

def get_operations_by_client(client_id):
    return [op for op in st.session_state.operations if op["client_id"] == client_id and op["statut"] == "en-cours"]

def get_operation_by_id(op_id):
    return next((op for op in st.session_state.operations if op["id"] == op_id), None)

def calculer_prochaine_echeance(op):
    date_debut = datetime.strptime(op["date_debut"], "%Y-%m-%d")
    duree_mois = op["duree"]
    # Calcul simplifié : échéance = date_debut + durée en mois
    prochaine_echeance = date_debut + timedelta(days=30*duree_mois)
    return prochaine_echeance.strftime("%d/%m/%Y")

# --- Styles CSS personnalisés ---
st.markdown("""
<style>
    .stButton>button {
        border-radius: 5px;
        padding: 5px 15px;
        font-weight: bold;
        border: none;
    }
    .operation-card {
        background-color: #e3f2fd;
        border-left: 5px solid #2196F3;
        padding: 10px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .paiement-card {
        background-color: #f1f8e9;
        border-left: 5px solid #8bc34a;
        padding: 10px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .client-card {
        background-color: #fce4ec;
        border-left: 5px solid #e91e63;
        padding: 10px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .statut-en-cours {
        color: #2196F3;
        font-weight: bold;
    }
    .statut-termine {
        color: #8bc34a;
        font-weight: bold;
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

# --- Onglet Accueil (Tableau de bord mis à jour) ---
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
                mensualite = (op["valeur"] * (1 + op["taux"]/100)) / op["duree"]
                prochaine_echeance = calculer_prochaine_echeance(op)
                st.markdown(f"""
                <div class="operation-card">
                    <p><strong>Client :</strong> {client['nom']}</p>
                    <p><strong>Opération ID :</strong> {op['id']}</p>
                    <p><strong>Valeur marchandise :</strong> {format_montant(op['valeur'])}</p>
                    <p><strong>Prochaine échéance :</strong> {prochaine_echeance}</p>
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
            st.markdown(f"""
            <div class="client-card">
                <p><strong>Description :</strong> {client['description']}</p>
                <p><strong>Téléphone :</strong> {client['tel']}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"🗑️ Supprimer", key=f"suppr_client_{client['id']}"):
                st.session_state.clients = [c for c in st.session_state.clients if c["id"] != client["id"]]
                st.rerun()

# --- Onglet Opérations ---
with tab_operations:
    st.header("📦 Gestion des Opérations")
    # Ajouter une opération
    with st.expander("➕ Ajouter une opération", expanded=False):
        with st.form("ajouter_operation"):
            client = st.selectbox(
                "Client *",
                options=st.session_state.clients,
                format_func=lambda x: x["nom"],
                key="client_op"
            )
            valeur = st.number_input("Valeur marchandise *", min_value=1, key="valeur_op")
            taux = st.number_input("Taux de bénéfice (%) *", min_value=1, key="taux_op")
            duree = st.number_input("Durée (mois) *", min_value=0.1, format="%.1f", key="duree_op")
            statut = st.selectbox("Statut", ["en-cours", "termine"], key="statut_op")
            date_debut = st.date_input("Date de début *", datetime.now(), key="date_debut_op")
            submitted = st.form_submit_button("Ajouter")
            if submitted:
                new_id = max([op["id"] for op in st.session_state.operations], default=0) + 1
                st.session_state.operations.append({
                    "id": new_id,
                    "client_id": client["id"],
                    "valeur": valeur,
                    "taux": taux,
                    "duree": duree,
                    "statut": statut,
                    "date_debut": date_debut.strftime("%Y-%m-%d")
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
                <p><strong>ID :</strong> {op['id']}</p>
                <p><strong>Valeur :</strong> {format_montant(op['valeur'])}</p>
                <p><strong>Taux :</strong> {op['taux']}%</p>
                <p><strong>Durée :</strong> {op['duree']} mois</p>
                <p><strong>Statut :</strong> <span class="statut-{op['statut']}">{op['statut']}</span></p>
                <p><strong>Date début :</strong> {op['date_debut']}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"🗑️ Supprimer", key=f"suppr_op_{op['id']}"):
                st.session_state.operations = [o for o in st.session_state.operations if o["id"] != op["id"]]
                st.rerun()

# --- Onglet Paiements (avec sélection client → opérations) ---
with tab_paiements:
    st.header("💰 Gestion des Paiements")
    # Ajouter un paiement
    with st.expander("➕ Ajouter un paiement", expanded=True):
        with st.form("ajouter_paiement"):
            # Étape 1 : Sélection du client
            client = st.selectbox(
                "Client *",
                options=st.session_state.clients,
                format_func=lambda x: x["nom"],
                key="client_paiement"
            )
            if client:
                # Étape 2 : Sélection de l'opération (uniquement celles du client)
                operations_client = get_operations_by_client(client["id"])
                if not operations_client:
                    st.error("❌ Ce client n'a aucune opération en cours.")
                else:
                    operation = st.selectbox(
                        "Opération *",
                        options=operations_client,
                        format_func=lambda x: f"Opération {x['id']} - {format_montant(x['valeur'])} ({x['duree']} mois)",
                        key="operation_paiement"
                    )
                    if operation:
                        # Étape 3 : Type de paiement et montant
                        type_paiement = st.selectbox("Type de paiement *", ["ordinaire", "anticipe"], key="type_paiement")
                        if type_paiement == "ordinaire":
                            montant = st.number_input(
                                "Montant (mensualité) *",
                                min_value=1,
                                value=int(operation["valeur"] * (1 + operation["taux"]/100) / operation["duree"]),
                                key="montant_paiement"
                            )
                        else:
                            montant = int(operation["valeur"] * operation["taux"] / 100)
                            st.info(f"💡 Montant calculé pour paiement anticipé : {format_montant(montant)}")
                        date = st.date_input("Date *", datetime.now(), key="date_paiement")
                        submitted = st.form_submit_button("Ajouter")
                        if submitted:
                            new_id = max([p["id"] for p in st.session_state.paiements], default=0) + 1
                            st.session_state.paiements.append({
                                "id": new_id,
                                "client_id": client["id"],
                                "operation_id": operation["id"],
                                "type": type_paiement,
                                "montant": montant,
                                "date": date.strftime("%Y-%m-%d")
                            })
                            st.success(f"✅ Paiement de {format_montant(montant)} ajouté pour l'opération {operation['id']} !")

    # Liste des paiements
    st.subheader("Liste des paiements")
    for paiement in st.session_state.paiements:
        client = get_client_by_id(paiement["client_id"])
        operation = get_operation_by_id(paiement.get("operation_id"))
        if client and operation:
            st.markdown(f"""
            <div class="paiement-card">
                <p><strong>Client :</strong> {client['nom']}</p>
                <p><strong>Opération :</strong> {operation['id']} ({format_montant(operation['valeur'])})</p>
                <p><strong>Type :</strong> {paiement['type']}</p>
                <p><strong>Montant :</strong> {format_montant(paiement['montant'])}</p>
                <p><strong>Date :</strong> {paiement['date']}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"🗑️ Supprimer", key=f"suppr_paiement_{paiement['id']}"):
                st.session_state.paiements = [p for p in st.session_state.paiements if p["id"] != paiement["id"]]
                st.rerun()
