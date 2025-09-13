from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
# Modèles
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    tel = db.Column(db.String(20), nullable=False)

class Operation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    valeur = db.Column(db.Integer, nullable=False)
    taux = db.Column(db.Integer, nullable=False)
    duree = db.Column(db.Float, nullable=False)
    statut = db.Column(db.String(20), default="en-cours")

class Paiement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # ordinaire/anticipe
    montant = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String(20), nullable=False)

# Routes
@app.route('/')
def index():
    operations = Operation.query.filter_by(statut="en-cours").all()
    return render_template('index.html', operations=operations)

@app.route('/clients')
def clients():
    clients = Client.query.all()
    return render_template('clients.html', clients=clients)

@app.route('/operations')
def operations():
    operations = Operation.query.all()
    return render_template('operations.html', operations=operations)

@app.route('/paiements')
def paiements():
    paiements = Paiement.query.all()
    return render_template('paiements.html', paiements=paiements)

# Ajouter un client
@app.route('/ajouter_client', methods=['POST'])
def ajouter_client():
    nom = request.form['nom']
    description = request.form['description']
    tel = request.form['tel']
    client = Client(nom=nom, description=description, tel=tel)
    db.session.add(client)
    db.session.commit()
    return redirect(url_for('clients'))

# Autres routes (ajouter/modifier/supprimer) à ajouter selon le même modèle

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

