from flask import Flask
from flask_graphql import GraphQLView
from graphql import GraphQLError
from pymongo import MongoClient
import graphene

app = Flask(__name__)

# MongoDB connection
try:
    client = MongoClient("mongodb+srv://my-user:vVgi4WfgzYA7CJBr@cluster0.kbovzuj.mongodb.net/")
    # Database Name
    db = client["IMDB"]
    # Collection Name
    collection = db["imdb"]
    # Add a print statement to confirm connection
    print("Connected to the database successfully.")
except Exception as e:
    print(f"Failed to connect to the database: {e}")
    exit(1)  # Exit the application if the connection fails

# GraphQL Schema
class Movie(graphene.ObjectType):
    id = graphene.String()  # Corresponds to the MongoDB document ID
    title = graphene.String()
    genre = graphene.List(graphene.String)
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
        movies = []
        for movie in collection.find():
            movies.append(Movie(
                id=str(movie["_id"]),
                title=movie["Title"],
                genre=movie["Genre"].split(","),
                description=movie["Description"],
                director=movie["Director"],
                actors=movie["Actors"].split(","),
                year=int(movie["Year"]["$numberInt"]) if isinstance(movie["Year"], dict) else movie["Year"],
                runtime=int(movie["Runtime"]["$numberInt"]) if isinstance(movie["Runtime"], dict) else movie["Runtime"],
                rating=float(movie["Rating"]["$numberDouble"]) if isinstance(movie["Rating"], dict) else movie["Rating"],
                votes=int(movie["Votes"]["$numberInt"]) if isinstance(movie["Votes"], dict) else movie["Votes"],
                revenue=float(movie["Revenue"]["$numberDouble"]) if isinstance(movie["Revenue"], dict) else movie["Revenue"]
            ))
        return movies

    def resolve_movie_by_title(self, info, title):
        movie = collection.find_one({"Title": title})
        if not movie:
            raise GraphQLError("Movie not found")
        return Movie(
            id=str(movie["_id"]),
            title=movie["Title"],
            genre=movie["Genre"].split(","),
            description=movie["Description"],
            director=movie["Director"],
            actors=movie["Actors"].split(","),
            year=int(movie["Year"]["$numberInt"]) if isinstance(movie["Year"], dict) else movie["Year"],
            runtime=int(movie["Runtime"]["$numberInt"]) if isinstance(movie["Runtime"], dict) else movie["Runtime"],
            rating=float(movie["Rating"]["$numberDouble"]) if isinstance(movie["Rating"], dict) else movie["Rating"],
            votes=int(movie["Votes"]["$numberInt"]) if isinstance(movie["Votes"], dict) else movie["Votes"],
            revenue=float(movie["Revenue"]["$numberDouble"]) if isinstance(movie["Revenue"], dict) else movie["Revenue"]
        )

# 1.Create function: insert the new movies or shows.
class CreateMovie(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        description = graphene.String(required=True)
        runtime = graphene.Int(required=True)
        genre = graphene.List(graphene.String, required=True)
        rating = graphene.Float(required=True)  # Changed from imdbScore to rating
        votes = graphene.Int(required=False, default_value=0)  # Default value for votes
        revenue = graphene.Float(required=False, default_value=0.0)  # Default value for revenue
        director = graphene.String(required=True)
        actors = graphene.List(graphene.String, required=True)  # Changed from production_countries to actors
        year = graphene.Int(required=True)

    movie = graphene.Field(Movie)

    def mutate(self, info, title, description, runtime, genre, rating, votes, revenue, director, actors, year):
        new_movie = {
            "Title": title,
            "Description": description,
            "Runtime": runtime,
            "Genre": ', '.join(genre),
            "Rating": rating,
            "Votes": votes,
            "Revenue": revenue,
            "Director": director,
            "Actors": ', '.join(actors),
            "Year": year
        }
        # Insert the new movie into the MongoDB collection
        collection.insert_one(new_movie)
        # Return the created movie
        return CreateMovie(movie=Movie(
            id=str(new_movie["_id"]),
            title=new_movie['Title'],
            description=new_movie['Description'],
            runtime=new_movie['Runtime'],
            genre=new_movie['Genre'].split(","),
            rating=new_movie['Rating'],
            year=new_movie['Year'],
            actors=new_movie['Actors'].split(","),
            votes=new_movie['Votes'],
            revenue=new_movie['Revenue'],
            director=new_movie['Director']
        ))

# 3. Delete function: delete the movie or show document using title.
class DeleteMovie(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)

    success = graphene.Boolean()

    def mutate(self, info, title):
        result = collection.delete_one({"Title": title})
        return DeleteMovie(success=result.deleted_count > 0)

# 4. Update function: update the movie or show document using title.
class UpdateMovie(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)  # Title of the movie to update
        description = graphene.String(required=False)  # Optional
        runtime = graphene.Int(required=False)  # Optional
        genre = graphene.List(graphene.String, required=False)  # Optional
        rating = graphene.Float(required=False)  # Optional
        votes = graphene.Int(required=False)  # Optional
        revenue = graphene.Float(required=False)  # Optional
        director = graphene.String(required=False)  # Optional
        actors = graphene.List(graphene.String, required=False)  # Optional
        year = graphene.Int(required=False)  # Optional

    success = graphene.Boolean()
    movie = graphene.Field(Movie)

    def mutate(self, info, title, description=None, runtime=None, genre=None, rating=None, votes=None, revenue=None, director=None, actors=None, year=None):
        update_fields = {}
        
        if description is not None:
            update_fields["Description"] = description
        if runtime is not None:
            update_fields["Runtime"] = runtime
        if genre is not None:
            update_fields["Genre"] = ', '.join(genre)
        if rating is not None:
            update_fields["Rating"] = rating
        if votes is not None:
            update_fields["Votes"] = votes
        if revenue is not None:
            update_fields["Revenue"] = revenue
        if director is not None:
            update_fields["Director"] = director
        if actors is not None:
            update_fields["Actors"] = ', '.join(actors)
        if year is not None:
            update_fields["Year"] = year

        result = collection.update_one({"Title": title}, {"$set": update_fields})

        if result.modified_count > 0:
            updated_movie = collection.find_one({"Title": title})
            return UpdateMovie(success=True, movie=Movie(
                id=str(updated_movie["_id"]),
                title=updated_movie['Title'],
                description=updated_movie['Description'],
                runtime=updated_movie['Runtime'],
                genre=updated_movie['Genre'].split(","),
                rating=updated_movie['Rating'],
                year=updated_movie['Year'],
                actors=updated_movie['Actors'].split(","),
                votes=updated_movie['Votes'],
                revenue=updated_movie['Revenue'],
                director=updated_movie['Director']
            ))
        else:
            return UpdateMovie(success=False, movie=None)

class Mutation(graphene.ObjectType):
    create_movie = CreateMovie.Field()
    delete_movie = DeleteMovie.Field()
    update_movie = UpdateMovie.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)

app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True)
)

if __name__ == "__main__":
    app.run(port=5017,debug=True)