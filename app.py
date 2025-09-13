import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

# --- Fonctions de la Base de Données ---

def init_db():
    """
    Initialise la base de données et crée les tables si elles n'existent pas.
    """
    conn = sqlite3.connect('ventes_terme.db')
    cursor = conn.cursor()

    # Table des clients
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            telephone TEXT,
            description TEXT
        )
    ''')

    # Table des opérations
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS operations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            valeur_marchandise REAL NOT NULL,
            taux_benefice REAL NOT NULL,
            duree_mois REAL NOT NULL,
            date_creation TEXT NOT NULL,
            statut TEXT DEFAULT 'En cours',
            montant_total REAL NOT NULL,
            montant_benefice REAL NOT NULL,
            montant_mensualite REAL NOT NULL,
            FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE CASCADE
        )
    ''')

    # Table des paiements
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS paiements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            operation_id INTEGER NOT NULL,
            type_paiement TEXT NOT NULL,
            montant REAL NOT NULL,
            date_paiement TEXT NOT NULL,
            FOREIGN KEY (operation_id) REFERENCES operations (id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()

# Fonctions pour gérer les clients
def ajouter_client(nom, telephone, description):
    conn = sqlite3.connect('ventes_terme.db')
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO clients (nom, telephone, description) VALUES (?, ?, ?)', (nom, telephone, description))
        conn.commit()
        return True, "Client ajouté avec succès!"
    except Exception as e:
        return False, f"Erreur lors de l'ajout du client: {e}"
    finally:
        conn.close()

def supprimer_client(client_id):
    conn = sqlite3.connect('ventes_terme.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM clients WHERE id = ?', (client_id,))
    conn.commit()
    conn.close()
    return True, "Client et ses opérations/paiements supprimés avec succès!"

def get_clients():
    conn = sqlite3.connect('ventes_terme.db')
    df = pd.read_sql_query("SELECT * FROM clients ORDER BY nom", conn)
    conn.close()
    return df

# Fonctions pour gérer les opérations
def creer_operation(client_id, valeur_marchandise, taux_benefice, duree_mois, statut, date_creation):
    conn = sqlite3.connect('ventes_terme.db')
    cursor = conn.cursor()
    
    # Vérifier s'il y a déjà une opération en cours pour ce client
    cursor.execute('SELECT COUNT(*) FROM operations WHERE client_id = ? AND statut = "En cours"', (client_id,))
    en_cours_count = cursor.fetchone()[0]
    
    if en_cours_count > 0:
        conn.close()
        return None, "Ce client a déjà une opération en cours. Veuillez la terminer avant d'en créer une nouvelle."

    montant_total = valeur_marchandise * (1 + taux_benefice / 100)
    montant_benefice = valeur_marchandise * (taux_benefice / 100)
    montant_mensualite = montant_total / duree_mois
    
    cursor.execute('''
        INSERT INTO operations (client_id, valeur_marchandise, taux_benefice, duree_mois, date_creation, 
                                statut, montant_total, montant_benefice, montant_mensualite)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (client_id, valeur_marchandise, taux_benefice, duree_mois, date_creation, statut, montant_total, montant_benefice, montant_mensualite))
    
    operation_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return operation_id, "Opération ajoutée avec succès!"

def supprimer_operation(operation_id):
    conn = sqlite3.connect('ventes_terme.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM operations WHERE id = ?', (operation_id,))
    conn.commit()
    conn.close()
    return True, "Opération et ses paiements supprimés avec succès!"

def get_operations():
    conn = sqlite3.connect('ventes_terme.db')
    df = pd.read_sql_query('''
        SELECT o.*, c.nom AS client_nom
        FROM operations o
        JOIN clients c ON o.client_id = c.id
        ORDER BY o.date_creation DESC
    ''', conn)
    conn.close()
    return df

def get_operations_by_client_id(client_id):
    conn = sqlite3.connect('ventes_terme.db')
    df = pd.read_sql_query('''
        SELECT * FROM operations WHERE client_id = ? AND statut = 'En cours'
    ''', conn, params=(client_id,))
    conn.close()
    return df

# Fonctions pour gérer les paiements
def enregistrer_paiement(operation_id, type_paiement, montant, date_paiement):
    conn = sqlite3.connect('ventes_terme.db')
    cursor = conn.cursor()
    
    # Récupérer l'ID du client depuis l'opération
    cursor.execute('SELECT client_id FROM operations WHERE id = ?', (operation_id,))
    client_id = cursor.fetchone()[0]

    cursor.execute('''
        INSERT INTO paiements (operation_id, type_paiement, montant, date_paiement)
        VALUES (?, ?, ?, ?)
    ''', (operation_id, type_paiement, montant, date_paiement))
    
    conn.commit()
    conn.close()
    return True, "Paiement enregistré avec succès!"

def supprimer_paiement(paiement_id):
    conn = sqlite3.connect('ventes_terme.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM paiements WHERE id = ?', (paiement_id,))
    conn.commit()
    conn.close()
    return True, "Paiement supprimé avec succès!"

def get_paiements():
    conn = sqlite3.connect('ventes_terme.db')
    df = pd.read_sql_query('''
        SELECT p.*, o.client_id, o.valeur_marchandise, c.nom as client_nom
        FROM paiements p
        JOIN operations o ON p.operation_id = o.id
        JOIN clients c ON o.client_id = c.id
        ORDER BY p.date_paiement DESC
    ''', conn)
    conn.close()
    return df

# Fonctions utilitaires
def format_montant(montant):
    return "{:,.0f}".format(montant).replace(",", " ")

def calculer_prochaine_echeance(op):
    date_creation = datetime.strptime(op["date_creation"], "%Y-%m-%d")
    total_paiements = get_total_paiements(op['id'])
    montant_total = op['montant_total']
    
    if total_paiements >= montant_total:
        return "Opération terminée"
    else:
        jours_passes = (datetime.now() - date_creation).days
        mois_passes = jours_passes // 30
        prochaine_date = date_creation + timedelta(days=30 * (mois_passes + 1))
        return prochaine_date.strftime("%d/%m/%Y")

def get_total_paiements(operation_id):
    conn = sqlite3.connect('ventes_terme.db')
    cursor = conn.cursor()
    cursor.execute('SELECT SUM(montant) FROM paiements WHERE operation_id = ?', (operation_id,))
    total = cursor.fetchone()[0] or 0
    conn.close()
    return total

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

def main():
    init_db()

    st.set_page_config(page_title="Gestion Commerciale", layout="wide")
    st.title("📊 Gestion des Clients, Opérations et Paiements")

    tab_accueil, tab_clients, tab_operations, tab_paiements = st.tabs(
        ["🏠 Tableau de bord", "👥 Clients", "📦 Opérations", "💰 Paiements"]
    )

    # Onglet Accueil
    with tab_accueil:
        st.header("📊 Tableau de bord")
        st.subheader("Opérations en cours")
        
        operations = get_operations()
        operations_en_cours = operations[operations['statut'] == 'En cours']

        if operations_en_cours.empty:
            st.info("Aucune opération en cours.")
        else:
            for _, op in operations_en_cours.iterrows():
                montant_total = op['valeur_marchandise'] * (1 + op['taux_benefice'] / 100)
                montant_mensualite = montant_total / op['duree_mois']
                prochaine_echeance = calculer_prochaine_echeance(op)
                
                st.markdown(f"""
                <div class="operation-card">
                    <p><strong>Client :</strong> {op['client_nom']}</p>
                    <p><strong>Opération ID :</strong> {op['id']}</p>
                    <p><strong>Valeur marchandise :</strong> {format_montant(op['valeur_marchandise'])}</p>
                    <p><strong>Prochaine échéance :</strong> {prochaine_echeance}</p>
                    <p><strong>Montant à payer :</strong> {format_montant(montant_mensualite)}</p>
                    <p><strong>Statut :</strong> <span class="statut-en-cours">{op['statut']}</span></p>
                </div>
                """, unsafe_allow_html=True)
    
    # Onglet Clients
    with tab_clients:
        st.header("👥 Gestion des Clients")
        with st.expander("➕ Ajouter un client", expanded=False):
            with st.form("ajouter_client"):
                nom = st.text_input("Nom *")
                description = st.text_input("Description")
                tel = st.text_input("Téléphone *")
                submitted = st.form_submit_button("Ajouter")
                if submitted:
                    if nom and tel:
                        success, message = ajouter_client(nom, tel, description)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
                    else:
                        st.error("❌ Le nom et le téléphone sont obligatoires.")

        st.subheader("Liste des clients")
        clients = get_clients()
        if clients.empty:
            st.info("Aucun client enregistré.")
        else:
            for _, client in clients.iterrows():
                with st.expander(f"👤 {client['nom']}"):
                    st.markdown(f"""
                    <div class="client-card">
                        <p><strong>Description :</strong> {client['description'] or 'N/A'}</p>
                        <p><strong>Téléphone :</strong> {client['telephone'] or 'N/A'}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"🗑️ Supprimer", key=f"suppr_client_{client['id']}"):
                        success, message = supprimer_client(client['id'])
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)

    # Onglet Opérations
    with tab_operations:
        st.header("📦 Gestion des Opérations")
        clients = get_clients()
        with st.expander("➕ Ajouter une opération", expanded=False):
            if clients.empty:
                st.warning("Veuillez d'abord ajouter un client.")
            else:
                with st.form("ajouter_operation"):
                    client_sel = st.selectbox(
                        "Client *",
                        options=clients['nom'].tolist(),
                        format_func=lambda x: x
                    )
                    client_id = clients[clients['nom'] == client_sel]['id'].iloc[0]
                    
                    valeur = st.number_input("Valeur marchandise *", min_value=1.0, key="valeur_op")
                    taux = st.number_input("Taux de bénéfice (%) *", min_value=1.0, key="taux_op")
                    duree = st.number_input("Durée (mois) *", min_value=0.1, key="duree_op")
                    statut = st.selectbox("Statut", ["En cours", "Terminé"], key="statut_op")
                    date_debut = st.date_input("Date de début *", datetime.now(), key="date_debut_op")
                    
                    submitted = st.form_submit_button("Ajouter")
                    if submitted:
                        if valeur and taux and duree:
                            operation_id, message = creer_operation(client_id, valeur, taux, duree, statut, date_debut.strftime("%Y-%m-%d"))
                            if operation_id:
                                st.success("✅ Opération ajoutée avec succès !")
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
                        else:
                            st.error("❌ Tous les champs marqués d'une étoile sont obligatoires.")
        
        st.subheader("Liste des opérations")
        operations = get_operations()
        if operations.empty:
            st.info("Aucune opération enregistrée.")
        else:
            for _, op in operations.iterrows():
                statut_class = 'statut-termine' if op['statut'] == 'Terminé' else 'statut-en-cours'
                st.markdown(f"""
                <div class="operation-card">
                    <p><strong>Client :</strong> {op['client_nom']}</p>
                    <p><strong>ID :</strong> {op['id']}</p>
                    <p><strong>Valeur :</strong> {format_montant(op['valeur_marchandise'])}</p>
                    <p><strong>Taux :</strong> {op['taux_benefice']}%</p>
                    <p><strong>Durée :</strong> {op['duree_mois']} mois</p>
                    <p><strong>Statut :</strong> <span class="{statut_class}">{op['statut']}</span></p>
                    <p><strong>Date début :</strong> {op['date_creation']}</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"🗑️ Supprimer", key=f"suppr_op_{op['id']}"):
                    supprimer_operation(op['id'])
                    st.success("Opération supprimée.")
                    st.rerun()

    # Onglet Paiements
    with tab_paiements:
        st.header("💰 Gestion des Paiements")
        clients = get_clients()
        with st.expander("➕ Ajouter un paiement", expanded=True):
            if clients.empty:
                st.warning("Veuillez d'abord ajouter un client.")
            else:
                with st.form("ajouter_paiement"):
                    client_sel = st.selectbox(
                        "Client *",
                        options=clients['nom'].tolist()
                    )
                    client_id = clients[clients['nom'] == client_sel]['id'].iloc[0]
                    
                    operations_client = get_operations_by_client_id(client_id)
                    if operations_client.empty:
                        st.error("❌ Ce client n'a aucune opération en cours.")
                    else:
                        op_sel = st.selectbox(
                            "Opération *",
                            options=operations_client['id'].tolist(),
                            format_func=lambda op_id: f"Opération {op_id} - {format_montant(operations_client[operations_client['id'] == op_id]['valeur_marchandise'].iloc[0])}"
                        )
                        operation = operations_client[operations_client['id'] == op_sel].iloc[0]

                        type_paiement = st.selectbox("Type de paiement *", ["Ordinaire", "Anticipé"])
                        
                        montant_total_op = operation['valeur_marchandise'] * (1 + operation['taux_benefice'] / 100)
                        montant_mensuel = montant_total_op / operation['duree_mois']
                        
                        if type_paiement == "Ordinaire":
                            montant_suggere = montant_mensuel
                        else:
                            montant_suggere = operation['montant_benefice']

                        montant = st.number_input("Montant *", min_value=1.0, value=montant_suggere)
                        date = st.date_input("Date *", datetime.now())
                        
                        submitted = st.form_submit_button("Ajouter")
                        if submitted:
                            if montant and date:
                                success, message = enregistrer_paiement(operation['id'], type_paiement, montant, date.strftime("%Y-%m-%d"))
                                if success:
                                    st.success(message)
                                    st.rerun()
                                else:
                                    st.error(message)
                            else:
                                st.error("❌ Le montant et la date sont obligatoires.")

        st.subheader("Liste des paiements")
        paiements = get_paiements()
        if paiements.empty:
            st.info("Aucun paiement enregistré.")
        else:
            for _, paiement in paiements.iterrows():
                st.markdown(f"""
                <div class="paiement-card">
                    <p><strong>Client :</strong> {paiement['client_nom']}</p>
                    <p><strong>Opération :</strong> {paiement['operation_id']} ({format_montant(paiement['valeur_marchandise'])})</p>
                    <p><strong>Type :</strong> {paiement['type_paiement']}</p>
                    <p><strong>Montant :</strong> {format_montant(paiement['montant'])}</p>
                    <p><strong>Date :</strong> {paiement['date_paiement']}</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"🗑️ Supprimer", key=f"suppr_paiement_{paiement['id']}"):
                    success, message = supprimer_paiement(paiement['id'])
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

if __name__ == "__main__":
    main()
