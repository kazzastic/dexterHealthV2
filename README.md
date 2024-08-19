# dexterHealthV2
This repository is for the coding assignment for the dexter health. A basic real-time messaging application with no GUI


## How to run?

In order to run this project you would need to start the server.py and then we need to open clients which want to interact, ideally we can run upto 2 different clients in terminals and then interact with eachother. 

## Prerequisites

In order to run this project we would need to either install these packages, 
- FastAPI
- asyncio
- websockets
- uvicorn

or optionally we can just do a, 

`
pip install -r requirements.txt
`

Once the necessary packages are installed we can then start running the client-server. 


### Run Server

User can run the server using the command, 

`
uvicorn server.src.server:app --reload --timeout-keep-alive 120
`
### Run Client (optionally 2)

In order to interact with the server, we need two clients running in two seperate terminals, for you to run the client from the root of the repository, run the command, 

`
python client/client.py 
`

## PostgreSQL
This client-server application has postgres as its database, in order to run the postgres you can use docker, running docker is easy, first you need docker engine installed on your local environment, once that is done you need to put in the command, 

`
docker run --name my-postgres-db -e POSTGRES_USER=dexter -e POSTGRES_PASSWORD=dexter1234 -e POSTGRES_DB=dexter -p 5432:5432 -d postgres 
`

put exactly this command since some elements of the project are hard coded for now. 

Once done, start interacting with the client and server. 

## My Thoughts

This was a great backend engineering exercise for me. Getting hands-on with async programming on python and coding a chat application was a new to me. I thoroughly loved it. 

I implemented it this using websockets, if given an ample amount of time this application has the capability to truly become end-to-end chatting application, because as of now this application let's everyone interact with everyone, meaning any amount of clients could join in, and the message would be broadcasted to all of them. I implemented it that way because I could not get to connect each of the clients with eachother, say client 1 with id 001 should be connected to client 2 with id 002. As of now any number of clients could join in. 

I also implemented a register and login service using REST API, meaning a user could register using a unique username and password, and then save conversation between themselves and another user which they should know the username of. The same user could also log into the system once their account as been created. 

### Improvements

I have made the application improvable, meaning that if I want I could, 

- hash the passwords 
- make the messages end-to-end encrypted so that DB stored messages won't be seen
- make the interaction isolated between two clients(users)
- once we can add interaction between 2 isolated clients, a group chat would be easily implemented

### Improvements After Submission
- Hashed Passwords
- Chat History loading on login/startup