import React, { useEffect, useState } from "react";

const History = () => {
    const [history, setHistory] = useState([]);

    useEffect(() => {
        const userId = localStorage.getItem("user_id");

        if (!userId) {
            alert("You must be logged in to view history.");
            return;
        }

        fetch(`http://127.0.0.1:5000/user_history/${userId}`)
            .then((response) => response.json())
            .then((data) => setHistory(data.history || []))
            .catch((error) => console.error("Error fetching history:", error));
    }, []);

    return (
        <div className="history-container" style={{ maxWidth: "700px", margin: "0 auto", padding: "20px" }}>
            <h2>Prediction History</h2>
            {history.length > 0 ? (
                <table style={{ width: "100%", borderCollapse: "collapse" }}>
                    <thead>
                    <tr>
                        <th>Stock Symbol</th>
                        <th>Predicted Price</th>
                        <th>Requested At</th>
                    </tr>
                    </thead>
                    <tbody>
                    {history.map((entry, index) => (
                        <tr key={index}>
                            <td>{entry.symbol}</td>
                            <td>${parseFloat(entry.predicted_price).toFixed(2)}</td>
                            <td>{new Date(entry.requested_at).toString()}</td>
                        </tr>
                    ))}
                    </tbody>
                </table>
            ) : (
                <p>No prediction history found.</p>
            )}
        </div>
    );
};

export default History;
