import React, { useState, useEffect } from 'react';
import config from './config'; 

const StockItem = ({ stock, removeFromWatchlist }) => {
  const [price, setPrice] = useState(0);
  const [webSocket, setWebSocket] = useState(null);
  
  useEffect(() => {
    const fetchPrice = async () => {
        try {
            const response = await fetch(`${config.backendURL}/api/securities/${stock.ticker}/`);
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const data = await response.json();
            setPrice(data.last_price);
        } catch (error) {
            console.log("There was a problem with the fetch operation:", error.message);
        }
    };
    fetchPrice();

    const ws = new WebSocket(`${config.wsURL}/ws/stocks/${stock.ticker}/`);

    ws.onopen = () => {
      console.log(`WebSocket connected for ${stock.ticker}`);
    }

    ws.onmessage = (event) => {
      const newPrice = JSON.parse(event.data).price;
      setPrice(newPrice);
    };

    ws.onclose = () => {
      console.log(`WebSocket disconnected for ${stock.ticker}`);
    };

    setWebSocket(ws);

    return () => {
      ws.close();
    };
  }, [stock.ticker]);

  const handleRemoveFromWatchlist = () => {
    webSocket.close();
    removeFromWatchlist();
  };

  return (
    <div>
      <p>{stock.ticker} - {stock.name}: ${price}</p>
      <button onClick={handleRemoveFromWatchlist}>Remove</button>
    </div>
  );
};

export default StockItem;
