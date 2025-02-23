## Mutation Query to read all movie

```graphql
{
  allMovies {
    title
    genre
    description
    director
    actors
    year
    runtime
    rating
    votes
    revenue
  }
}
```

## Mutation Query to find a movie by title

```graphql
{
  movieByTitle(title: "Promotheus") {
    title
    genre
    description
    director
    actors
    year
    runtime
    rating
    votes
    revenue
  }
}
```

# Mutation query to add a movie

```graphql
mutation {
  createMovie(
    title: "Guardians of the Galaxy"
    description: "A group of intergalactic criminals are forced to work together to stop..."
    runtime: 121
    genre: ["Action", "Adventure", "Sci-Fi"]
    rating: 8.1
    votes: 757074
    revenue: 333.13
    director: "James Gunn"
    actors: ["Chris Pratt", "Vin Diesel", "Bradley Cooper", "Zoe Saldana"]
    year: 2014
  ) {
    movie {
      id
      title
      description
      runtime
      genre
      rating
      votes
      revenue
      director
      actors
      year
    }
  }
}
```

## Mutation Query to update a movie

```graphql
mutation {
  updateMovie(
    title: "Guardians of the Galaxy"
    description: "A new description for the movie."
    rating: 8.5
    revenue: 350.00
  ) {
    success
    movie {
      id
      title
      description
      runtime
      genre
      rating
      votes
      revenue
      director
      actors
      year
    }
  }
}
```
