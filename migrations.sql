-- migrations.sql
-- 1. Créer la table accounting_periods
CREATE TABLE accounting_periods (
    id INT AUTO_INCREMENT PRIMARY KEY,
    year INT NOT NULL,
    month INT NULL,
    status ENUM('OPEN', 'CLOSED') DEFAULT 'OPEN',
    closing_date DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_period (year, month)
);

-- 2. Ajouter la colonne validated à la table ecriture
ALTER TABLE ecriture 
ADD COLUMN validated BOOLEAN DEFAULT FALSE;

-- 3. Créer un index pour optimiser les requêtes par date
CREATE INDEX idx_ecriture_date ON ecriture(date_ecriture);
CREATE INDEX idx_accounting_period ON accounting_periods(year, month, status);


---Créer la table fournisseur
CREATE TABLE fournisseurs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    email VARCHAR(255),
    phone VARCHAR(50)
);

---Créer la table facture fournisseur
CREATE TABLE factures_fournisseur (
    id SERIAL PRIMARY KEY,
    fournisseur_id INT REFERENCES fournisseurs(id),
    invoice_number VARCHAR(100),
    date_facture DATE NOT NULL,
    date_echeance DATE,
    total_ht NUMERIC(12,2),
    total_tva NUMERIC(12,2),
    total_ttc NUMERIC(12,2),
    statut VARCHAR(50) DEFAULT 'DRAFT',
    created_at TIMESTAMP DEFAULT NOW()
);

--Créer la table lignes factures
CREATE TABLE ligne_facture_fournisseur (
    id SERIAL PRIMARY KEY,
    facture_id INT REFERENCES factures_fournisseur(id),
    description TEXT,
    quantite NUMERIC(12,2),
    prix_unitaire NUMERIC(12,2),
    tva NUMERIC(5,2)
);

---Créer la table paiement
CREATE TABLE paiements_fournisseur (
    id SERIAL PRIMARY KEY,
    facture_id INT REFERENCES factures_fournisseur(id),
    montant NUMERIC(12,2),
    date_paiement DATE,
    mode_paiement VARCHAR(50)
);
