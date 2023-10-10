import React, { useState } from 'react';

function SearchBar({ onSearch, results, onAddToWatchlist }) {
  const [query, setQuery] = useState('');

  const handleSearch = (event) => {
    setQuery(event.target.value);
    onSearch(event.target.value);
  };

  return (
    <div>
      <input 
        type="text" 
        value={query} 
        onChange={handleSearch} 
        placeholder="Search for stocks..." 
      />
      {results.length > 0 && (
        <ul>
          {results.map((stock, index) => (
            <li key={index}>
               ({stock.ticker}) - {stock.name}
              <button onClick={() => onAddToWatchlist(stock)}>Add to Watchlist</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default SearchBar;
