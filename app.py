import warnings

warnings.filterwarnings('ignore', category=FutureWarning)
from flask import abort, render_template, Flask
import logging
import db

APP = Flask(__name__)


# Start page
@APP.route('/')
def index():
    stats = {}
    stats = db.execute('''
    SELECT * FROM
      (SELECT COUNT(*) n_Contratos FROM Contratos)
    JOIN
      (SELECT COUNT(*) n_Adjudicantes FROM Adjudicantes)
    JOIN
      (SELECT COUNT(*) n_Adjudicatarios FROM Adjudicatarios)
    JOIN 
      (SELECT COUNT(*) n_Cpv FROM Cpv)
    JOIN 
      (SELECT COUNT(*) n_LocaisExecucao FROM LocaisExecucao)
    JOIN 
      (SELECT COUNT(*) n_Municipios FROM Municipios)
    JOIN 
      (SELECT COUNT(*) n_Distritos FROM Distritos)
    JOIN 
      (SELECT COUNT(*) n_Paises FROM Paises)
    ''').fetchone()
    logging.info(stats)
    return render_template('index.html', stats=stats)

@APP.route('/contratos/')
def list_contratos():
    contratos = db.execute(
        '''
        SELECT * 
        FROM Contratos
        ORDER BY idContrato
        ''').fetchall()
    return render_template('contratos-list.html', contratos=contratos)


@APP.route('/contratos/<int:id>/')
def get_contrato(id):
    contrato = db.execute(
        '''
        SELECT * 
        FROM Contratos 
        WHERE idContrato = ?
        ''', [id]).fetchone()

    if contrato is None:
        abort(404, 'Movie id {} does not exist.'.format(id))

    return render_template('contrato.html',
                           contrato=contrato)

@APP.route('/municipios/')
def list_municipios():
    municipios = db.execute(
        '''
        SELECT * 
        FROM Municipios
        ''').fetchall()
    return render_template('municipios-list.html', municipios=municipios)

@APP.route('/municipios/<string:nome>/')
def get_municipio(nome):
    municipio = db.execute(
        '''
        SELECT nomeMunicipio, idContrato, precoContratual, dataCelebracaoContrato FROM locaisExecucao l
        JOIN municipios m
        USING (codigoMunicipio)
        JOIN contratos c
        ON l.idLocalExecucao = c.idLocalizacao
        WHERE m.nomeMunicipio = ?
        ''', [nome]).fetchall()

    if municipio is None:
        abort(404, 'Movie id {} does not exist.'.format(nome))

    return render_template('municipio.html',
                           municipio=municipio)

# @APP.route('/municipios/<string:nome>/')
# def get_contrato(nome):
#     municipio = db.execute(
#         '''
#         SELECT codigoMunicipio, nomeMunicipio, idContrato
#         FROM Municipios
#         JOIN locaisExecucao ON locaisExecucao.idMunicipio = Municipios.codigoMunicipio
#         JOIN Contratos
#         WHERE nomeMunicipio = ?
#         ''', [nome]).fetchone()
#
#     if municipio is None:
#         abort(404, 'Movie id {} does not exist.'.format(nome))
#
#     return render_template('municipio.html',
#                            municipio=municipio)

@APP.route('/movies/search/<expr>/')
def search_movie(expr):
    search = {'expr': expr}
    expr = '%' + expr + '%'
    movies = db.execute(
        ''' 
        SELECT MovieId, Title
        FROM MOVIE 
        WHERE Title LIKE ?
        ''', [expr]).fetchall()
    return render_template('movie-search.html',
                           search=search, movies=movies)


# Actors
@APP.route('/actors/')
def list_actors():
    actors = db.execute('''
      SELECT ActorId, Name 
      FROM Actor
      ORDER BY Name
    ''').fetchall()
    return render_template('actor-list.html', actors=actors)


@APP.route('/actors/<int:id>/')
def view_movies_by_actor(id):
    actor = db.execute(
        '''
        SELECT ActorId, Name
        FROM ACTOR 
        WHERE ActorId = ?
        ''', [id]).fetchone()

    if actor is None:
        abort(404, 'Actor id {} does not exist.'.format(id))

    movies = db.execute(
        '''
        SELECT MovieId, Title
        FROM MOVIE NATURAL JOIN MOVIE_ACTOR
        WHERE ActorId = ?
        ORDER BY Title
        ''', [id]).fetchall()

    return render_template('actor.html',
                           actor=actor, movies=movies)


@APP.route('/actors/search/<expr>/')
def search_actor(expr):
    search = {'expr': expr}
    # SQL INJECTION POSSIBLE! - avoid this!
    actors = db.execute(
        ' SELECT ActorId, Name'
        ' FROM ACTOR '
        ' WHERE Name LIKE \'%' + expr + '%\''
    ).fetchall()

    return render_template('actor-search.html',
                           search=search, actors=actors)


# Genres
@APP.route('/genres/')
def list_genres():
    genres = db.execute('''
      SELECT GenreId, Label 
      FROM GENRE
      ORDER BY Label
    ''').fetchall()
    return render_template('genre-list.html', genres=genres)


@APP.route('/genres/<int:id>/')
def view_movies_by_genre(id):
    genre = db.execute(
        '''
        SELECT GenreId, Label
        FROM GENRE 
        WHERE GenreId = ?
        ''', [id]).fetchone()

    if genre is None:
        abort(404, 'Genre id {} does not exist.'.format(id))

    movies = db.execute(
        '''
        SELECT MovieId, Title
        FROM MOVIE NATURAL JOIN MOVIE_GENRE
        WHERE GenreId = ?
        ORDER BY Title
        ''', [id]).fetchall()

    return render_template('genre.html',
                           genre=genre, movies=movies)


# Streams
@APP.route('/streams/<int:id>/')
def get_stream(id):
    stream = db.execute(
        '''
        SELECT StreamId, StreamDate, Charge, MovieId, Title, CustomerId, Name
        FROM STREAM NATURAL JOIN MOVIE NATURAL JOIN CUSTOMER 
        WHERE StreamId = ?
        ''', [id]).fetchone()

    if stream is None:
        abort(404, 'Stream id {} does not exist.'.format(id))

    return render_template('stream.html', stream=stream)


# Staff
@APP.route('/staff/')
def list_staff():
    staff = db.execute('''
      SELECT S1.StaffId AS StaffId, 
             S1.Name AS Name,
             S1.Job AS Job, 
             S1.Supervisor AS Supervisor,
             S2.Name AS SupervisorName
      FROM STAFF S1 LEFT JOIN STAFF S2 ON(S1.Supervisor = S2.StaffId)
      ORDER BY S1.Name
    ''').fetchall()
    return render_template('staff-list.html', staff=staff)


@APP.route('/staff/<int:id>/')
def show_staff(id):
    staff = db.execute(
        '''
        SELECT StaffId, Name, Supervisor, Job
        FROM STAFF
        WHERE staffId = ?
        ''', [id]).fetchone()

    if staff is None:
        abort(404, 'Staff id {} does not exist.'.format(id))
    superv = {}
    if not (staff['Supervisor'] is None):
        superv = db.execute(
            '''
            SELECT Name
            FROM staff
            WHERE staffId = ?
            ''', [staff['Supervisor']]).fetchone()
    supervisees = []
    supervisees = db.execute(
        '''
          SELECT StaffId, Name from staff
          where Supervisor = ?
          ORDER BY Name
        ''', [id]).fetchall()

    return render_template('staff.html',
                           staff=staff, superv=superv, supervisees=supervisees)

