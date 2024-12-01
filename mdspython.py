# Modelos de base de datos
class Pelicula(db.Model):
    __tablename__ = 'peliculas'
    imdb_title_id = db.Column(db.String(255), primary_key=True)
    title = db.Column(db.Text, nullable=False)
    original_title = db.Column(db.Text)
    year_pelicula = db.Column(db.Integer)
    date_published = db.Column(db.Date)
    genre = db.Column(db.Text)
    duration = db.Column(db.Integer)
    country = db.Column(db.Text)
    language = db.Column(db.Text)
    description = db.Column(db.Text)
    # Relación con peliculas_actores
    actores = db.relationship('PeliculasActores', backref='pelicula', lazy=True)
    personal = db.relationship('Personal', backref='pelicula', lazy=True)

class Personal(db.Model):
    __tablename__ = 'personal'
    imdb_title_id = db.Column(db.String(255), db.ForeignKey('peliculas.imdb_title_id'), primary_key=True)
    director = db.Column(db.Text, primary_key=True)
    writer = db.Column(db.Text, primary_key=True)

class PeliculasActores(db.Model):
    __tablename__ = 'peliculas_actores'

    imdb_title_id = db.Column(db.String, db.ForeignKey('peliculas.imdb_title_id'), primary_key=True, nullable=False)
    actor = db.Column(db.String, primary_key=True, nullable=False)

    def __repr__(self):
        return f"<PeliculasActores(imdb_title_id='{self.imdb_title_id}', actor='{self.actor}')>"
# Rutas para realizar consultas optimizadas con vistas e índices

# Ruta para obtener películas de un género específico y ordenadas por duración (vista `peliculas_por_genero_duracion`)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/peliculas/actores_por_genero_director_duracion', methods=['GET', 'POST'])
def peliculas_actores_por_genero_director_duracion():
    if request.method == 'POST':  # Cuando el formulario sea enviado
        genero = request.form.get('genero')
        director = request.form.get('director')
        duracion_max = request.form.get('duracion_max', type=int)
        actores = request.form.get('actores')  # Lista de actores separados por coma

        # Base de la consulta
        query = """
            SELECT p.title, p.year_pelicula, p.duration, pa.actors
            FROM peliculas p
            JOIN peliculas_actores pa ON p.imdb_title_id = pa.imdb_title_id
            JOIN personal pr ON p.imdb_title_id = pr.imdb_title_id
            WHERE p.genre = :genero
              AND pr.director = :director
        """
        params = {"genero": genero, "director": director}

        # Agregar filtro de duración si se especifica
        if duracion_max is not None:
            query += " AND p.duration <= :duracion_max"
            params["duracion_max"] = duracion_max

        # Filtrar por actores si se especifica
        if actores:
            actores_lista = actores.split(',')
            actor_conditions = []
            for actor in actores_lista:
                actor_conditions.append("pa.actors ILIKE :actors_" + actor.replace(" ", "_"))
                params["actors_" + actor.replace(" ", "_")] = f"%{actor}%"

            query += " AND (" + " OR ".join(actor_conditions) + ")"

        # Ejecutar la consulta con los parámetros proporcionados
        query = db.text(query)
        resultado = db.session.execute(query, params).fetchall()

        # Construir los datos para enviar al HTML
        peliculas = []
        for r in resultado:
            peliculas.append({
                "titulo": r[0],
                "anio": r[1],
                "duracion": r[2],
                "actores": r[3]
            })

        return render_template('consulta_actores_genero_director_duracion.html', peliculas=peliculas)

    # GET: Muestra el formulario vacío inicialmente
    return render_template('consulta_actores_genero_director_duracion.html', peliculas=None)


@app.route('/peliculas/actores_por_genero_director', methods=['GET', 'POST'])
def peliculas_actores_por_genero_director():
    # Normalizar entrada del usuario
    genero = request.args.get('genero', '').strip().lower()
    genero = ' '.join(genero.split())  # Eliminar espacios redundantes
    director = request.args.get('director', '').strip().lower()
    director = ' '.join(director.split())  # Eliminar espacios redundantes

    if not genero or not director:
        return render_template(
            'consulta_actores_genero_director.html',
            peliculas=None,
            error="Por favor, ingresa tanto un género como un director."
        )

    # Base de la consulta
    query = """
        SELECT p.title, p.year_pelicula, pa.actors
        FROM peliculas p
        JOIN peliculas_actores pa ON p.imdb_title_id = pa.imdb_title_id
        JOIN personal pr ON p.imdb_title_id = pr.imdb_title_id
        WHERE LOWER(p.genre) LIKE :genero AND LOWER(pr.director) LIKE :director
    """
    # Agregar comodines para coincidencias parciales
    params = {"genero": f"%{genero}%", "director": f"%{director}%"}

    try:
        # Preparar y ejecutar la consulta
        query = db.text(query)
        resultado = db.session.execute(query, params).fetchall()

        # Construir los resultados
        peliculas = [
            {"titulo": r[0], "anio": r[1], "actores": r[2]}
            for r in resultado
        ]

        return render_template(
            'consulta_actores_genero_director.html',
            peliculas=peliculas,
            genero=genero,
            director=director
        )
    except Exception as e:
        return render_template(
            'consulta_actores_genero_director.html',
            peliculas=None,
            error="Ha ocurrido un error al procesar la consulta. Por favor, inténtalo de nuevo."
        )



@app.route('/peliculas/por_genero_duracion', methods=['GET', 'POST'])
def peliculas_por_genero_duracion():
    # Normalizar entrada del usuario
    genero = request.args.get('genero', '').strip().lower()
    genero = ' '.join(genero.split())  # Eliminar espacios extra entre palabras
    duracion_max = request.args.get('duracion_max', type=int, default=None)

    if not genero:
        return render_template('consulta_genero_duracion.html', peliculas=[], error="Por favor, ingresa un género.")

    # Base de la consulta
    query = """
        SELECT p.title, p.genre, p.duration, p.country, p.year_pelicula
        FROM peliculas p
        WHERE LOWER(REPLACE(p.genre, ' ', '')) LIKE LOWER(REPLACE(:genero, ' ', ''))
    """
    params = {"genero": f"%{genero.replace(' ', '')}%"}  # Coincidencias sin espacios

    # Filtro adicional si se especifica duración máxima
    if duracion_max is not None:
        query += " AND p.duration <= :duracion_max"
        params["duracion_max"] = duracion_max

    try:
        # Preparar y ejecutar consulta
        query = db.text(query)
        resultado = db.session.execute(query, params).fetchall()

        # Formatear resultados
        peliculas = [
            {
                "title": r.title,
                "genre": r.genre,
                "duration": r.duration,
                "country": r.country,
                "year": r.year_pelicula
            }
            for r in resultado
        ]
    except Exception as e:
        return render_template('consulta_genero_duracion.html', peliculas=[], error=str(e))

    # Renderizar resultados
    return render_template('consulta_genero_duracion.html', peliculas=peliculas, genero=genero, duracion_max=duracion_max)





@app.route('/peliculas/por_region_epoca', methods=['GET'])
def peliculas_por_region_epoca():
    region = request.args.get('region')
    epoca_inicio = request.args.get('epoca_inicio', type=int)
    epoca_fin = request.args.get('epoca_fin', type=int)

    if not (region and epoca_inicio and epoca_fin):
        return render_template('consulta_region_epoca.html', error="Faltan parámetros", peliculas=None)

    # Consulta segura usando parámetros ligados
    query = """
        SELECT p.title, p.year_pelicula, p.country, p.genre, pr.director
        FROM peliculas p
        JOIN personal pr ON p.imdb_title_id = pr.imdb_title_id
        WHERE p.country ILIKE :region AND p.year_pelicula BETWEEN :epoca_inicio AND :epoca_fin
    """
    params = {
        "region": f"%{region}%",
        "epoca_inicio": epoca_inicio,
        "epoca_fin": epoca_fin
    }

    try:
        resultado = db.session.execute(db.text(query), params).fetchall()
        peliculas = [
            {"titulo": r.title, "anio": r.year_pelicula, "pais": r.country, "genero": r.genre, "director": r.director}
            for r in resultado
        ]
        return render_template('consulta_region_epoca.html', peliculas=peliculas)
    except Exception as e:
        return render_template('consulta_region_epoca.html', error=str(e), peliculas=None)

@app.route('/peliculas/colaboraciones_frecuentes', methods=['GET'])
def colaboraciones_frecuentes():
    try:
        query = """
            SELECT 
                pa.actors AS actor,  -- Usar la columna "actors"
                pr.director AS director, 
                COUNT(*) AS colaboraciones
            FROM peliculas_actores pa
            JOIN personal pr ON pa.imdb_title_id = pr.imdb_title_id
            GROUP BY pa.actors, pr.director
            ORDER BY colaboraciones DESC
            LIMIT 15
        """
        query = db.text(query)
        resultado = db.session.execute(query).fetchall()

        # Filtrar los resultados donde el actor es "Desconocido" o el director es None
        colaboraciones = [
            {"actor": r[0], "director": r[1], "colaboraciones": r[2]}
            for r in resultado if r[0] != "Desconocido" and r[1] is not None
        ]

        return render_template('colaboraciones_frecuentes.html', colaboraciones=colaboraciones)

    except Exception as e:
        return render_template('colaboraciones_frecuentes.html', colaboraciones=None, error=str(e))
