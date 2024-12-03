import React, { useState, useEffect } from 'react';

const App = () => {
    const [athletes, setAthletes] = useState([]);
    const [searchQuery, setSearchQuery] = useState('');

    // Fetch athletes data
    useEffect(() => {
        const fetchAthletes = async () => {
            try {
                const response = await fetch(
                    `http://localhost:5000/api/athletes?query=${searchQuery}`
                );
                const data = await response.json();
                setAthletes(data);
            } catch (error) {
                console.error('Error fetching athletes:', error);
            }
        };
        fetchAthletes();
    }, [searchQuery]);

    return (
        <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
            <h1>Athlete Information</h1>
            <input
                type="text"
                placeholder="Search athletes by name"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                style={{
                    padding: '10px',
                    width: '300px',
                    marginBottom: '20px',
                }}
            />
            <div>
                {athletes.length > 0 ? (
                    athletes.map((athlete) => (
                        <div
                            key={athlete._id}
                            style={{
                                border: '1px solid #ccc',
                                padding: '10px',
                                marginBottom: '10px',
                                borderRadius: '5px',
                            }}
                        >
                            <h2>{athlete.details.name}</h2>
                            <p>
                                <strong>Country:</strong> {athlete.details.country}
                            </p>
                            <p>
                                <strong>Event:</strong> {athlete.details.events.join(', ')}
                            </p>
                            <p>
                                <strong>Date of Birth:</strong>{' '}
                                {athlete.details.date_of_birth}
                            </p>
                            <p>
                                <strong>Athlete Code:</strong>{' '}
                                {athlete.details.athlete_code}
                            </p>
                            <p>
                                <strong>Highest Event Ranking:</strong> {athlete.details.highest_event_ranking?athlete.details.highest_event_ranking.ranking:''}{' '}
                                in {athlete.details.highest_event_ranking?athlete.details.highest_event_ranking.event:''}
                            </p>
                            <img
                                src={athlete.details.image_url}
                                alt={`${athlete.details.name}`}
                                style={{
                                    maxWidth: '200px',
                                    borderRadius: '10px',
                                    margin: '10px 0',
                                }}
                            />
                            <h3>Additional Events</h3>
                            {athlete.details.additional_events.length > 0 ? (
                                <ul>
                                    {athlete.details.additional_events.map((event, index) => (
                                        <li key={index}>
                                            <strong>{event.title}:</strong>{' '}
                                            {event.result} ({event.date}), Score: {event.score}
                                        </li>
                                    ))}
                                </ul>
                            ) : (
                                <p>No additional events available.</p>
                            )}
                            <a
                                href={athlete.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                style={{
                                    display: 'inline-block',
                                    marginTop: '10px',
                                    color: 'blue',
                                    textDecoration: 'underline',
                                }}
                            >
                                View More Details
                            </a>
                        </div>
                    ))
                ) : (
                    <p>No athletes found.</p>
                )}
            </div>
        </div>
    );
};

export default App;