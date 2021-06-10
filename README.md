# UOCIS322 - Project 7 #
Adding authentication and user interface to brevet time calculator service

#### Part 1: Authenticating the services 

- POST **/register**

Registers a new user. On success a status code 201 is returned. The body of the response contains a JSON object with the newly added user. On failure status code 400 (bad request) is returned. Note: The password is hashed before it is stored in the database. Once hashed, the original password is discarded. Your database should have three fields: id (unique index), username and password for storing the credentials.

- GET **/token**

Returns a token. This request must be authenticated using a HTTP Basic Authentication (see `DockerAuth/password.py` and `DockerAuth/testToken.py`). On success a JSON object is returned with a field `token` set to the authentication token for the user and a field `duration` set to the (approximate) number of seconds the token is valid. On failure status code 401 (unauthorized) is returned.

- GET **/RESOURCE-YOU-CREATED-IN-PROJECT-6**

Return a protected <resource>, which is basically what you created in project 6. This request must be authenticated using token-based authentication only (see `DockerAuth/testToken.py`). HTTP password-based (basic) authentication is not allowed. On success a JSON object with data for the authenticated user is returned. On failure status code 401 (unauthorized) is returned.

#### Part 2: User interface

The goal of this part of the project is to create frontend/UI for Brevet app using Flask-WTF and Flask-Login introduced in lectures. You frontend/UI should use the authentication that you created above. In addition to creating UI for basic authentication and token generation, you will add three additional functionalities in your UI: a) registration, b) login, c) remember me, d) logout.

## Author

Melodie Collins, mcolli11@uoregon.edu
