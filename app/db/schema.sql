CREATE DATABASE IF NOT EXISTS mitti_se_mandi
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE mitti_se_mandi;



-- USERS


CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,

    role ENUM('farmer', 'buyer') NOT NULL,

    full_name VARCHAR(150) NOT NULL,

    email VARCHAR(255) NOT NULL UNIQUE,

    phone VARCHAR(20),

    password VARCHAR(255) NOT NULL,

    state VARCHAR(100),

    city VARCHAR(100),

    address TEXT,

    crops TEXT,

    land_size DECIMAL(10,2),

    business_name VARCHAR(200),

    interests TEXT,

    is_verified BOOLEAN NOT NULL DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP
);

-- FARMER CROPS


CREATE TABLE IF NOT EXISTS crops (
    id INT AUTO_INCREMENT PRIMARY KEY,

    farmer_id INT NOT NULL,

    crop_name VARCHAR(150) NOT NULL,

    variety VARCHAR(150),

    quantity DECIMAL(12,2) NOT NULL,

    quantity_unit VARCHAR(30) NOT NULL DEFAULT 'quintal',

    grade VARCHAR(100),

    expected_price DECIMAL(12,2),

    harvest_date DATE,

    available_date DATE,

    market_name VARCHAR(200),

    status ENUM(
        'available',
        'listed',
        'sold',
        'inactive'
    ) NOT NULL DEFAULT 'available',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_crops_farmer
        FOREIGN KEY (farmer_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);



-- LOTS


CREATE TABLE IF NOT EXISTS lots (
    id INT AUTO_INCREMENT PRIMARY KEY,

    farmer_id INT NOT NULL,

    lot_code VARCHAR(50) NOT NULL UNIQUE,

    crop_name VARCHAR(150) NOT NULL,

    variety VARCHAR(150),

    quantity DECIMAL(12,2) NOT NULL,

    quantity_unit VARCHAR(30) NOT NULL DEFAULT 'quintal',

    grade VARCHAR(100),

    expected_price DECIMAL(12,2),

    market_name VARCHAR(200),

    location VARCHAR(200),

    available_date DATE,

    status ENUM(
        'draft',
        'published',
        'matched',
        'sold',
        'cancelled'
    ) NOT NULL DEFAULT 'draft',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_lots_farmer
        FOREIGN KEY (farmer_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);



-- BUYER REQUIREMENTS


CREATE TABLE IF NOT EXISTS buyer_requirements (
    id INT AUTO_INCREMENT PRIMARY KEY,

    buyer_id INT NOT NULL,

    crop_name VARCHAR(150) NOT NULL,

    variety VARCHAR(150),

    min_quantity DECIMAL(12,2),

    max_quantity DECIMAL(12,2),

    quantity_unit VARCHAR(30) NOT NULL DEFAULT 'quintal',

    required_grade VARCHAR(100),

    preferred_location VARCHAR(200),

    max_price DECIMAL(12,2),

    status ENUM(
        'active',
        'closed'
    ) NOT NULL DEFAULT 'active',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_requirements_buyer
        FOREIGN KEY (buyer_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);



-- LISTINGS


CREATE TABLE IF NOT EXISTS listings (
    id INT AUTO_INCREMENT PRIMARY KEY,

    lot_id INT NOT NULL,

    farmer_id INT NOT NULL,

    title VARCHAR(200) NOT NULL,

    description TEXT,

    asking_price DECIMAL(12,2),

    status ENUM(
        'active',
        'paused',
        'sold',
        'cancelled'
    ) NOT NULL DEFAULT 'active',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_listings_lot
        FOREIGN KEY (lot_id)
        REFERENCES lots(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_listings_farmer
        FOREIGN KEY (farmer_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);


-- OFFERS

CREATE TABLE IF NOT EXISTS offers (
    id INT AUTO_INCREMENT PRIMARY KEY,

    listing_id INT NOT NULL,

    buyer_id INT NOT NULL,

    quantity DECIMAL(12,2) NOT NULL,

    offered_price DECIMAL(12,2) NOT NULL,

    message TEXT,

    status ENUM(
        'pending',
        'accepted',
        'rejected',
        'countered',
        'cancelled'
    ) NOT NULL DEFAULT 'pending',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_offers_listing
        FOREIGN KEY (listing_id)
        REFERENCES listings(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_offers_buyer
        FOREIGN KEY (buyer_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);


-- TRANSACTIONS


CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,

    offer_id INT NOT NULL UNIQUE,

    farmer_id INT NOT NULL,

    buyer_id INT NOT NULL,

    quantity DECIMAL(12,2) NOT NULL,

    agreed_price DECIMAL(12,2) NOT NULL,

    total_amount DECIMAL(14,2) NOT NULL,

    status ENUM(
        'pending',
        'confirmed',
        'completed',
        'cancelled',
        'disputed'
    ) NOT NULL DEFAULT 'pending',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_transactions_offer
        FOREIGN KEY (offer_id)
        REFERENCES offers(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_transactions_farmer
        FOREIGN KEY (farmer_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_transactions_buyer
        FOREIGN KEY (buyer_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);



-- PAYMENTS


CREATE TABLE IF NOT EXISTS payments (
    id INT AUTO_INCREMENT PRIMARY KEY,

    transaction_id INT NOT NULL UNIQUE,

    amount DECIMAL(14,2) NOT NULL,

    payment_reference VARCHAR(150),

    status ENUM(
        'pending',
        'paid',
        'failed',
        'refunded'
    ) NOT NULL DEFAULT 'pending',

    paid_at DATETIME,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_payments_transaction
        FOREIGN KEY (transaction_id)
        REFERENCES transactions(id)
        ON DELETE CASCADE
);


-- DISPUTES

CREATE TABLE IF NOT EXISTS disputes (
    id INT AUTO_INCREMENT PRIMARY KEY,

    transaction_id INT NOT NULL,

    raised_by INT NOT NULL,

    subject VARCHAR(200) NOT NULL,

    description TEXT NOT NULL,

    status ENUM(
        'open',
        'under_review',
        'resolved',
        'closed'
    ) NOT NULL DEFAULT 'open',

    resolution TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    resolved_at DATETIME,

    CONSTRAINT fk_disputes_transaction
        FOREIGN KEY (transaction_id)
        REFERENCES transactions(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_disputes_user
        FOREIGN KEY (raised_by)
        REFERENCES users(id)
        ON DELETE CASCADE
);

-- INDEXES


CREATE INDEX idx_users_role
    ON users(role);

CREATE INDEX idx_crops_farmer
    ON crops(farmer_id);

CREATE INDEX idx_crops_crop_name
    ON crops(crop_name);

CREATE INDEX idx_lots_farmer
    ON lots(farmer_id);

CREATE INDEX idx_lots_crop
    ON lots(crop_name);

CREATE INDEX idx_lots_status
    ON lots(status);

CREATE INDEX idx_requirements_buyer
    ON buyer_requirements(buyer_id);

CREATE INDEX idx_requirements_crop
    ON buyer_requirements(crop_name);

CREATE INDEX idx_listings_farmer
    ON listings(farmer_id);

CREATE INDEX idx_listings_status
    ON listings(status);

CREATE INDEX idx_offers_buyer
    ON offers(buyer_id);

CREATE INDEX idx_offers_status
    ON offers(status);

CREATE INDEX idx_transactions_farmer
    ON transactions(farmer_id);

CREATE INDEX idx_transactions_buyer
    ON transactions(buyer_id);

CREATE INDEX idx_transactions_status
    ON transactions(status);

CREATE INDEX idx_disputes_status
    ON disputes(status);