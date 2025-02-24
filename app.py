from flask import Flask
from flask_graphql import GraphQLView
from graphql import GraphQLError
from pymongo import MongoClient
import graphene

app = Flask(__name__)

# MongoDB connection
try:
    #client = MongoClient("mongodb+srv://<your-mongodb-atlas-connection-string>")  # Use your Atlas connection string
    client = MongoClient("mongodb://localhost:27017")
    db = client["IMDB"]  
    collection = db["imdb"]  
    print("Connected to the database successfully.", collection)
except Exception as e:
    print(f"Failed to connect to the database: {e}")
    exit(1)  

# GraphQL Schema
class Movie(graphene.ObjectType):
    id = graphene.String()
    title = graphene.String()
    genres = graphene.List(graphene.String)
    description = graphene.String()
    director = graphene.String()
    actors = graphene.List(graphene.String)
    year = graphene.Int()
    runtime = graphene.Int()
    rating = graphene.Float()
    votes = graphene.Int()
    revenue = graphene.Float()

class Query(graphene.ObjectType):
    all_movies = graphene.List(Movie)
    movie_by_title = graphene.Field(Movie, title=graphene.String())

    def resolve_all_movies(self, info):
        movies = collection.find()
        return [
            Movie(
                id=str(movie.get("_id")),
                title=movie.get("Title"),
                genres=movie.get("Genre", []).split(", ") if movie.get("Genre") else [],
                description=movie.get("Description"),
                director=movie.get("Director"),
                actors=movie.get("Actors", []).split(", ") if movie.get("Actors") else [],
                year=movie.get("Year"),
                runtime=movie.get("Runtime"),
                rating=movie.get("Rating"),
                votes=movie.get("Votes"),
                revenue=movie.get("Revenue")
            )
            for movie in movies
        ]

    def resolve_movie_by_title(self, info, title):
        movie = collection.find_one({"Title": title})
        if not movie:
            raise GraphQLError("Movie not found")
        return Movie(
            id=str(movie.get("_id")),
            title=movie.get("Title"),
            genres=movie.get("Genre", []).split(","),
            description=movie.get("Description"),
            director=movie.get("Director"),
            actors=movie.get("Actors", []).split(", ") if movie.get("Actors") else [],
            year=movie.get("Year"),
            runtime=movie.get("Runtime"),
            rating=movie.get("Rating"),
            votes=movie.get("Votes"),
            revenue=movie.get("Revenue")
        )
# 1.Create function: insert the new movies.
class CreateMovie(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        genres  = graphene.List(graphene.String, required=True)
        description = graphene.String(required=True)
        director = graphene.String(required=True)
        actors = graphene.List(graphene.String, required=True)
        year = graphene.Int(required=True)
        runtime = graphene.Int(required=True)
        rating = graphene.Float(required=True)
        votes = graphene.Int(required=True)
        revenue = graphene.Float(required=True)

    movie = graphene.Field(Movie)

    def mutate(self, info, title, genres, description, director, actors, year, runtime, rating, votes, revenue):
        new_movie = {
            "Title": title,
            "Genre": ",".join(genres),  
            "Description": description,
            "Director": director,
            "Actors": ", ".join(actors),  
            "Year": year,
            "Runtime": runtime,
            "Rating": rating,
            "Votes": votes,
            "Revenue": revenue
        }
     
        collection.insert_one(new_movie)
       
        return CreateMovie(movie=Movie(
            title=new_movie['Title'],
            genres=new_movie['Genre'].split(","), 
            description=new_movie['Description'],
            director=new_movie['Director'],
            actors=new_movie['Actors'].split(", ") if new_movie.get('Actors') else [],
            year=new_movie['Year'],
            runtime=new_movie['Runtime'],
            rating=new_movie['Rating'],
            votes=new_movie['Votes'],
            revenue=new_movie['Revenue']
        ))


class UpdateMovie(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        description = graphene.String()  
        runtime = graphene.Int()         
        genres = graphene.List(graphene.String) 
        votes = graphene.Int()           

    movie = graphene.Field(Movie)

    def mutate(self, info, title, description=None, runtime=None, genres=None, votes=None):
        
        update_data = {}

        if description is not None:
            update_data["Description"] = description
        if runtime is not None:
            update_data["Runtime"] = runtime
        if genres is not None:
            update_data["Genre"] = ",".join(genres)
        if votes is not None:
            update_data["Votes"] = votes

        result = collection.update_one({"Title": title}, {"$set": update_data})
        if result.matched_count == 0:
            raise GraphQLError("Movie not found")

        updated_movie = collection.find_one({"Title": title})

        updated_genres = updated_movie.get("Genre", "").split(",") if updated_movie.get("Genre") else []

        return UpdateMovie(movie=Movie(
            title=updated_movie.get("Title"),
            description=updated_movie.get("Description"),
            director=updated_movie.get("Director"),
            actors=updated_movie.get("Actors", "").split(", ") if updated_movie.get("Actors") else [],
            year=updated_movie.get("Year"),
            runtime=updated_movie.get("Runtime"),
            rating=updated_movie.get("Rating"),
            votes=updated_movie.get("Votes"),
            revenue=updated_movie.get("Revenue"),
            genres=updated_genres
        ))

class DeleteMovie(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)

    success = graphene.Boolean()

    def mutate(self, info, title):
        result = collection.delete_one({"Title": title})
        return DeleteMovie(success=result.deleted_count > 0)

class Mutation(graphene.ObjectType):
    create_movie = CreateMovie.Field()
    update_movie = UpdateMovie.Field()
    delete_movie = DeleteMovie.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)

app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True)
)

if __name__ == "__main__":
    app.run(port=5017, debug=True)
