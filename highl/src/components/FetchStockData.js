import React, { useState } from "react";

function FetchStockData() {
    const [symbol, setSymbol] = useState("");
    const [message, setMessage] = useState("");
    const [tableData, setTableData] = useState([]);

    const fetchData = async () => {
        if (!symbol) {
            alert("Enter a stock symbol!");
            return;
        }

        const response = await fetch("http://127.0.0.1:5000/get_stock_data", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ symbol }),
        });

        const data = await response.json();
        setMessage(data.error ? `Error: ${data.error}` : data.message);

        if (data.data) {
            setTableData(data.data); // Set the table data with the first few rows
        }
    };

    return (
        <div>
            <h2>Fetch Stock Data</h2>
            <input
                type="text"
                value={symbol}
                placeholder="Enter Stock Symbol"
                onChange={(e) => setSymbol(e.target.value)}
            />
            <button onClick={fetchData}>Get Data</button>
            <p>{message}</p>

            {/* Display data in tabular format */}
            {tableData.length > 0 && (
                <table>
                    <thead>
                    <tr>
                        <th>Date</th>
                        <th>Close</th>
                        <th>SMA_50</th>
                        <th>SMA_200</th>
                        <th>DMA_50_200</th>
                        <th>RSI</th>
                        <th>MACD</th>
                        <th>Signal_Line</th>
                        <th>Upper_Band</th>
                        <th>Lower_Band</th>
                        <th>Volume_Change</th>
                        <th>Sentiment</th>
                        <th>Future Close</th>
                    </tr>
                    </thead>
                    <tbody>
                    {tableData.map((row, index) => (
                        <tr key={index}>
                            <td>{row.Date}</td>
                            <td>{row.Close}</td>
                            <td>{row.SMA_50}</td>
                            <td>{row.SMA_200}</td>
                            <td>{row.DMA_50_200}</td>
                            <td>{row.RSI}</td>
                            <td>{row.MACD}</td>
                            <td>{row.Signal_Line}</td>
                            <td>{row.Upper_Band}</td>
                            <td>{row.Lower_Band}</td>
                            <td>{row.Volume_Change}</td>
                            <td>{row.Sentiment}</td>
                            <td>{row['Future Close']}</td>
                        </tr>
                    ))}
                    </tbody>
                </table>
            )}
        </div>
    );
}

export default FetchStockData;
