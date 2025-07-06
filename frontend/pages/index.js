import { useState } from 'react';

const API_URL = 'http://localhost:8000';

export default function Home() {
  const [authId, setAuthId] = useState('');
  const [password, setPassword] = useState('');
  const [mode, setMode] = useState('timeline');
  const [screenName, setScreenName] = useState('');
  const [query, setQuery] = useState('');
  const [count, setCount] = useState(50);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [loading, setLoading] = useState(false);
  const [tweets, setTweets] = useState([]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setTweets([]);

    try {
      let endpoint = '';
      let body = {};
      if (mode === 'timeline') {
        endpoint = `${API_URL}/timeline`;
        body = { auth_id: authId, password, screen_name: screenName, count };
      } else {
        endpoint = `${API_URL}/search`;
        body = {
          auth_id: authId,
          password,
          query,
          count,
          mode,
          start_date: startDate || null,
          end_date: endDate || null,
        };
      }

      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      setTweets(data);
    } catch (err) {
      console.error(err);
      alert('Scraping failed');
    }

    setLoading(false);
  };

  return (
    <div className="container">
      <h1>X Scraper Dashboard</h1>
      <form onSubmit={handleSubmit}>
        <h2>Authentication</h2>
        <input value={authId} onChange={e => setAuthId(e.target.value)} placeholder="Auth ID" required />
        <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Password" required />

        <h2>Mode</h2>
        <select value={mode} onChange={e => setMode(e.target.value)}>
          <option value="timeline">Timeline</option>
          <option value="date_range">Date Range</option>
          <option value="popular">Popular</option>
          <option value="latest">Latest</option>
        </select>

        {mode === 'timeline' && (
          <input value={screenName} onChange={e => setScreenName(e.target.value)} placeholder="Screen Name" required />
        )}

        {mode !== 'timeline' && (
          <input value={query} onChange={e => setQuery(e.target.value)} placeholder="Query" required />
        )}

        {mode === 'date_range' && (
          <>
            <input type="date" value={startDate} onChange={e => setStartDate(e.target.value)} />
            <input type="date" value={endDate} onChange={e => setEndDate(e.target.value)} />
          </>
        )}

        <input type="number" min="1" value={count} onChange={e => setCount(e.target.value)} />
        <button type="submit" disabled={loading}>{loading ? 'Working...' : 'Start Scraping'}</button>
      </form>

      {tweets.length > 0 && (
        <table>
          <thead>
            <tr>
              <th>Created At</th>
              <th>User</th>
              <th>Text</th>
            </tr>
          </thead>
          <tbody>
            {tweets.map(tweet => (
              <tr key={tweet.tweet_id}>
                <td>{tweet.created_at}</td>
                <td>{tweet.username}</td>
                <td>{tweet.text}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
