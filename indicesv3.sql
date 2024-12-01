CREATE INDEX idx_peliculas_genre ON peliculas(genre);
CREATE INDEX idx_peliculas_duration ON peliculas(duration);
CREATE INDEX idx_peliculas_year ON peliculas(year_pelicula);
CREATE INDEX idx_peliculas_country_year ON peliculas(country, year_pelicula);
CREATE INDEX idx_peliculas_imdb_title_id ON peliculas(imdb_title_id);
CREATE INDEX idx_peliculas_actores_actors ON peliculas_actores(actors);
CREATE INDEX idx_peliculas_actores_imdb_title_id ON peliculas_actores(imdb_title_id);
CREATE INDEX idx_personal_director ON personal(director);
CREATE INDEX idx_personal_imdb_title_id ON personal(imdb_title_id);
CREATE INDEX idx_peliculas_actores_imdb_actors ON peliculas_actores(imdb_title_id, actors);
CREATE INDEX idx_personal_imdb_director ON personal(imdb_title_id, director);

