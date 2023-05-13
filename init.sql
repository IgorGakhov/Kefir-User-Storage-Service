CREATE TABLE cities (
    id SERIAL PRIMARY KEY,
    name TEXT
);
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    hashed_password TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    other_name TEXT,
    email TEXT NOT NULL UNIQUE,
    phone TEXT,
    birthday DATE,
    city_id INTEGER REFERENCES cities(id),
    additional_info TEXT,
    role TEXT NOT NULL DEFAULT 'basic'
);
