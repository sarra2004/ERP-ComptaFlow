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
