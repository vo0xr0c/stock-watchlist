# Product Engineering Case Study Overview 

Welcome to the Albert product engineering case study. The project is a stock watchlist service and client application that allows users to view their favorite stock prices.

### Functional Requirements:
- Users should be able to search for stocks by name or ticker and add them to a watchlist.
- Users should be able to remove a stock from their watchlist.
- Users should be able to see the current price of the stocks in their watchlist.
- Prices should update every 5 seconds.
- The service should be designed to support millions of users each with their own watchlist.
- User data should be persisted in a database and re-used when the app is restarted.
- The focus for this case study is on the service architecture and communication between the service and client application.
- The client application must support user login and a single screen that contains a search bar, list of stocks and current prices, but it does not need to be a polished UI.

## Project Overview

The project consists of a Django REST backend service and a React client application.

### Design Considerations
1. **Scalability**: Asynchronous job queue, Celery, is used to offload the fetching of stock data from the 3rd party API. The job schedule is made by Celery Beat. 
2. **Caching**: All stock-related data - the stock models itself and the list of available tickers are cached in Redis on each update. This reduces DB load and makes service more responsive. 
3. **Real-time Updates**: WebSockets are used to push real-time (every 5 seconds) updates to the client. Websockets are made by the `one-by-ticker` method. The idea behind it is that the system anticipates a large and diverse user base, each with unique stock interests.
4. **Database Design**: Watchlist’s are made as simple as User-to-Stock relation

### Сonstraints
1. **User Management** This project has no Authentication or User Management. Login is supported by the “Username” header, filled by username from LocalStorage, so this also breaks CORS. For a production-grade solution, Django JWT would be used.
2. **SSL** This project has no SSL support and uses plain HTTP and WS, which is insufficient.
3. **Public /api/stock/{ticker}** The stock model is assumed to be publicly accessible.

## Getting started 

When running the project for the first time, please run the following commands:

- `make build` - build the image
- `make up-db` - run DB service
- `make load` - load dumped DB
- `make up` - run all services
- `make open-app` will open the React app in your browser.

Later only `make up` and `make open-app` could be used.

There are two users with usernames `user1` and `user2` are currently available.

Additional commands, such as `migrate`, `createusers` and `test` can be found in Makefile.

## Demo

![](https://github.com/vo0xr0c/stock-watchlist/blob/main/demo/demo.gif)