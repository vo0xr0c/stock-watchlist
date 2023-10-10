import React, { useState, useEffect } from 'react';
import StockItem from './StockItem';
import config from './config';

const Watchlist = ({ watchlist, setWatchlist }) => {
  const [loading, setLoading] = useState(false);
  // Load the watchlist from the backend when the component mounts
  useEffect(() => {
    const loadWatchlist = async () => {
      setLoading(true);
      try {
        const response = await fetch(`${config.backendURL}/api/watchlist`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Username': localStorage.getItem('userToken') // There should be Authorization header
          },
        });
        const data = await response.json();
        setWatchlist(data);
      } catch (error) {
        console.error('Error loading watchlist:', error);
      } finally {
        setLoading(false);
      }
    };
    
    loadWatchlist();
  }, []);

  const removeFromWatchlist = async (stock) => {
    try {
      const response = await fetch(`${config.backendURL}/api/watchlist/${stock.ticker}/`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'Username': localStorage.getItem('userToken')
        },
      });
      
      if (response.ok) {
        setWatchlist(watchlist.filter(item => item.ticker !== stock.ticker));
      } else {
        console.error('Error removing from watchlist:', await response.text());
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <div>
      {loading ? (
        <p>Loading...</p>
      ) : (
        watchlist.map(stock => (
          <StockItem
            key={stock.ticker}
            stock={stock}
            removeFromWatchlist={() => removeFromWatchlist(stock)}
          />
        ))
      )}
    </div>
  );
};

export default Watchlist;