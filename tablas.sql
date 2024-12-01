
CREATE TABLE Peliculas (
    imdb_title_id VARCHAR(255) PRIMARY KEY,
    title TEXT,
    original_title TEXT,
    year_pelicula INT,
    date_published DATE,
    genre TEXT,
    duration INT,
    country TEXT,
    language TEXT,
    description TEXT
);
CREATE TABLE Personal (
    imdb_title_id VARCHAR(255),
    director TEXT,
    writer TEXT,
    PRIMARY KEY (imdb_title_id, director, writer),
    FOREIGN KEY (imdb_title_id) REFERENCES Peliculas(imdb_title_id)
);
CREATE TABLE peliculas_actores (
    imdb_title_id VARCHAR(255),
    actors TEXT
);




