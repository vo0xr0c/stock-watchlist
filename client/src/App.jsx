import React, { useState, useCallback } from 'react';
import './App.css';
import { LoginForm } from './LoginForm';
import { UserContext } from './UserContext';
import { User } from "./User.jsx";
import SearchBar from './SearchBar';
import Watchlist from './Watchlist';
import config from './config';

function App() {
  const [user, setUser] = useState(null);
  const [watchlist, setWatchlist] = useState([]);
  const [searchResults, setSearchResults] = useState([]);

  const login = useCallback((u) => setUser(u), []);
  const logout = useCallback(() => setUser(null), []);

  const handleSearch = useCallback(async (query) => {
    if (query) {
      try {
        const response = await fetch(`${config.backendURL}/api/securities/?query=${query}`);
        const results = await response.json();
        setSearchResults(results);
      } catch (error) {
        console.error('Error searching stocks:', error);
      }
    } else {
      setSearchResults([]);
    }
  }, []);

  const handleAddToWatchlist = useCallback(async (stock) => {
    try {
      const response = await fetch(`${config.backendURL}/api/watchlist/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Username': localStorage.getItem('userToken'), // There should be Authorization header
        },
        body: JSON.stringify(stock),
      });

      if (response.ok) {
        setWatchlist([...watchlist, stock]);
      } else {
        console.error('Error adding to watchlist:', await response.text());
      }
    } catch (error) {
      console.error('Error:', error);
    }
  });

  return (
    <UserContext.Provider value={{ user, login, logout }}>
      <div className="app">
        <LoginForm />
        <header>
          <h1>Albert stock watch</h1>
          <User />
        </header>
        {user && (
          <section>
            <SearchBar onSearch={handleSearch} results={searchResults} onAddToWatchlist={handleAddToWatchlist} />
            <div>
              <h2>Your Watchlist</h2>
              <Watchlist watchlist={watchlist} setWatchlist={setWatchlist} />
            </div>
          </section>
        )}
      </div>
    </UserContext.Provider>
  );
}

export default App;
