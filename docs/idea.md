# Project Idea - Pokedex etl service.

The goal of this project is to showcase the BMAD method for creating a green field full stack with UI project from beggining to end to a team of real full stack agile team.

A common workflow for my team is: 

- Creating database tables based on an api response.
- Calling an api endpoint using a batchjob, saving the response to a database.
- Creating an api that uses crud operations on the info from the database.
- Creating an UI to show that information.

For this project we will use a Pokemon theme. The pokemon API has the correct complexity to be a real world example.

- The pokedex will only be focused on pokemon and their most common information.
  - id
  - name
  - height
  - weight
  - types
  - sprites
  - stats
    - hp
    - attack
    - defense
    - special-attack
    - special-defense
    - speed
- The ui will be a single page app.
- The ui will be themed on the first generation pokedex.
- The ui will only show one pokemon with its information.
- The ui will include buttons that show the different pokemon sprites (female, and shiny included, if available) based on different generations if available. The default sprite will be the default front one.
- The documentation for the pokemon api is https://pokeapi.co/docs/v2
- For creating the database tables we will use the json response from the following endpoint
  - GET - https://pokeapi.co/api/v2/pokemon/{id or name}/
    - Examples:
      - `docs/1.json`
      - `docs/10.json`
      - `docs/100.json`
      - `docs/1000.json`
  - The tables will be normalized to the Third Normal Form (3NF)
- The front end will use HTMX and tailwind css
  - htmx docs https://htmx.org/docs/
  - tailwind css docs https://tailwindcss.com/docs
- The back end will python focused
  - python 3.12+
  - typer - for the batchjob
  - fastapi - for the backend api
  - sqlmodel - for interacting with sql databases
  - sqlalchemy - for interacting with sql databases
  - uv - for virtual environment setup
  - ruff - for linting
  - mypy - type hints
  - pytests
- Sqlite3 as database
