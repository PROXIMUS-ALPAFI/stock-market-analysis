import React, { useEffect, useState } from "react";

const History = () => {
    const [history, setHistory] = useState([]);

    useEffect(() => {
        fetch("http://127.0.0.1:5000/fetch_history") // Adjust URL if needed
            .then((response) => response.json())
            .then((data) => setHistory(data.history))
            .catch((error) => console.error("Error fetching history:", error));
    }, []);

    return (
        <div className="history-container">
            <h2>User Action History</h2>
            <table>
                <thead>
                <tr>
                    <th>ID</th>
                    <th>Stock Symbol</th>
                    <th>Action</th>
                    <th>Timestamp</th>
                </tr>
                </thead>
                <tbody>
                {history.map((entry) => (
                    <tr key={entry[0]}>
                        <td>{entry[0]}</td>
                        <td>{entry[1]}</td>
                        <td>{entry[2]}</td>
                        <td>{entry[3]}</td>
                    </tr>
                ))}
                </tbody>
            </table>
        </div>
    );
};

export default History;
