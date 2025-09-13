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
        {"id": 2, "client_id": 1, "valeur": 2000000, "taux": 12, "duree": 4, "statut": "en-cours"},
        {"id": 3, "client_id": 2, "valeur": 2300000, "taux": 15, "duree": 3, "statut": "termine"}
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

# --- Onglet Paiements (version améliorée) ---
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
                # Étape 2 : Sélection de l'opération (si le client en a plusieurs)
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
                            montant = st.number_input("Montant (mensualité) *", min_value=1, value=int(operation["valeur"] * (1 + operation["taux"]/100) / operation["duree"]), key="montant_paiement")
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
                <div>
                    {st.button(f"🗑️ Supprimer", key=f"suppr_paiement_{paiement['id']}")}
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Supprimer {paiement['id']}", key=f"suppr_paiement_hidden_{paiement['id']}"):
                st.session_state.paiements = [p for p in st.session_state.paiements if p["id"] != paiement["id"]]
                st.rerun()

# --- Le reste de votre code (onglets Accueil, Clients, Opérations) reste inchangé ---
# (Je peux vous le fournir si besoin, mais il n'a pas changé par rapport à la version précédente)
