import { useState, useMemo } from 'react';
import Head from 'next/head';
import * as XLSX from 'xlsx';
import Papa from 'papaparse';
import TweetTable from '../components/TweetTable';
import type { Tweet, Toast } from '../types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Home() {
  const [authId, setAuthId] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [mode, setMode] = useState<string>('timeline');
  const [screenName, setScreenName] = useState<string>('');
  const [query, setQuery] = useState<string>('');
  const [count, setCount] = useState<number>(50);
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [tweets, setTweets] = useState<Tweet[]>([]);
  const [error, setError] = useState<string>('');
  
  // Filter states
  const [usernameFilter, setUsernameFilter] = useState<string>('');
  const [keywordFilter, setKeywordFilter] = useState<string>('');
  const [toast, setToast] = useState<Toast | null>(null);

  // Filtered tweets based on filters
  const filteredTweets = useMemo(() => {
    return tweets.filter(tweet => {
      const matchesUsername = !usernameFilter || 
        tweet.username.toLowerCase().includes(usernameFilter.toLowerCase());
      const matchesKeyword = !keywordFilter || 
        tweet.text.toLowerCase().includes(keywordFilter.toLowerCase());
      return matchesUsername && matchesKeyword;
    });
  }, [tweets, usernameFilter, keywordFilter]);

  const showToast = (message: string, type: 'success' | 'error' = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setTweets([]);
    setError('');

    try {
      let endpoint = '';
      let body: any = {};
      if (mode === 'timeline') {
        endpoint = `${API_URL}/timeline`;
        body = { auth_id: authId, password, screen_name: screenName, count: parseInt(count.toString()) };
      } else {
        endpoint = `${API_URL}/search`;
        body = {
          auth_id: authId,
          password,
          query,
          count: parseInt(count.toString()),
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
      
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      
      const data: Tweet[] = await res.json();
      setTweets(data);
      showToast(`Successfully scraped ${data.length} tweets!`);
    } catch (err) {
      console.error(err);
      setError('Failed to scrape tweets. Please check your credentials and try again.');
      showToast('Failed to scrape tweets. Please check your credentials and try again.', 'error');
    }

    setLoading(false);
  };

  const formatDate = (dateString: string): string => {
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return dateString;
    }
  };

  const exportToCSV = () => {
    const csvData = filteredTweets.map(tweet => ({
      post_date: formatDate(tweet.created_at),
      username: tweet.username,
      text: tweet.text,
      url: tweet.url ?? `https://twitter.com/${tweet.username}/status/${tweet.tweet_id}`,
      retweet_count: tweet.retweet_count ?? 0,
      favorite_count: tweet.favorite_count ?? 0,
      reply_count: tweet.reply_count ?? 0
    }));

    const csv = Papa.unparse(csvData);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', 'tweets_export.csv');
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    showToast('CSV export completed successfully!');
  };

  const exportToExcel = () => {
    const excelData = filteredTweets.map(tweet => ({
      'Post Date': formatDate(tweet.created_at),
      'Username': tweet.username,
      'Text': tweet.text,
      'URL': tweet.url ?? `https://twitter.com/${tweet.username}/status/${tweet.tweet_id}`,
      'Retweet Count': tweet.retweet_count ?? 0,
      'Favorite Count': tweet.favorite_count ?? 0,
      'Reply Count': tweet.reply_count ?? 0
    }));

    const worksheet = XLSX.utils.json_to_sheet(excelData);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Tweets');
    XLSX.writeFile(workbook, 'tweets_export.xlsx');
    showToast('Excel export completed successfully!');
  };

  return (
    <>
      <Head>
        <title>𝕏 Scraper Dashboard - Advanced Tweet Analysis Tool</title>
        <meta name="description" content="Extract and analyze tweets with advanced search capabilities. User-friendly interface for Twitter data scraping." />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      {toast && (
        <div className={`toast ${toast.type}`}>
          {toast.message}
        </div>
      )}
      
      <div className="min-h-screen bg-primary-gradient">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-4 drop-shadow-lg">
              𝕏 Scraper Dashboard
            </h1>
            <p className="text-xl text-white/90 max-w-2xl mx-auto">
              Extract and analyze tweets with advanced search capabilities
            </p>
          </div>

          {/* Main Content */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Form Section */}
            <div className="lg:col-span-1">
              <div className="bg-white/95 backdrop-blur-sm rounded-2xl p-6 shadow-2xl border border-white/20">
                <form onSubmit={handleSubmit} className="space-y-6">
                  {/* Authentication */}
                  <div className="space-y-4">
                    <div className="flex items-center gap-2 mb-4">
                      <div className="w-1 h-6 bg-primary-gradient rounded-full"></div>
                      <h2 className="text-lg font-semibold text-gray-700">🔐 Authentication</h2>
                    </div>
                    <div>
                      <label htmlFor="authId" className="block text-sm font-medium text-gray-700 mb-2">
                        Username/Email
                      </label>
                      <input
                        id="authId"
                        type="text"
                        value={authId}
                        onChange={e => setAuthId(e.target.value)}
                        placeholder="Enter your X username or email"
                        className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-200 transition-all duration-200"
                        required
                      />
                    </div>
                    <div>
                      <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                        Password
                      </label>
                      <input
                        id="password"
                        type="password"
                        value={password}
                        onChange={e => setPassword(e.target.value)}
                        placeholder="Enter your X password"
                        className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-200 transition-all duration-200"
                        required
                      />
                    </div>
                  </div>

                  {/* Search Mode */}
                  <div className="space-y-4">
                    <div className="flex items-center gap-2 mb-4">
                      <div className="w-1 h-6 bg-primary-gradient rounded-full"></div>
                      <h2 className="text-lg font-semibold text-gray-700">⚙️ Search Mode</h2>
                    </div>
                    <div>
                      <label htmlFor="mode" className="block text-sm font-medium text-gray-700 mb-2">
                        Select Mode
                      </label>
                      <select
                        id="mode"
                        value={mode}
                        onChange={e => setMode(e.target.value)}
                        className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-200 transition-all duration-200"
                      >
                        <option value="timeline">👤 User Timeline</option>
                        <option value="date_range">📅 Date Range Search</option>
                        <option value="popular">🔥 Popular Tweets</option>
                        <option value="latest">⚡ Latest Tweets</option>
                      </select>
                    </div>
                  </div>

                  {/* Search Parameters */}
                  <div className="space-y-4">
                    <div className="flex items-center gap-2 mb-4">
                      <div className="w-1 h-6 bg-primary-gradient rounded-full"></div>
                      <h2 className="text-lg font-semibold text-gray-700">🎯 Search Parameters</h2>
                    </div>
                    
                    {mode === 'timeline' && (
                      <div>
                        <label htmlFor="screenName" className="block text-sm font-medium text-gray-700 mb-2">
                          Username (without @)
                        </label>
                        <input
                          id="screenName"
                          type="text"
                          value={screenName}
                          onChange={e => setScreenName(e.target.value)}
                          placeholder="e.g., elonmusk"
                          className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-200 transition-all duration-200"
                          required
                        />
                      </div>
                    )}

                    {mode !== 'timeline' && (
                      <div>
                        <label htmlFor="query" className="block text-sm font-medium text-gray-700 mb-2">
                          Search Query
                        </label>
                        <input
                          id="query"
                          type="text"
                          value={query}
                          onChange={e => setQuery(e.target.value)}
                          placeholder="Enter keywords, hashtags, or @mentions"
                          className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-200 transition-all duration-200"
                          required
                        />
                      </div>
                    )}

                    {mode === 'date_range' && (
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label htmlFor="startDate" className="block text-sm font-medium text-gray-700 mb-2">
                            Start Date
                          </label>
                          <input
                            id="startDate"
                            type="date"
                            value={startDate}
                            onChange={e => setStartDate(e.target.value)}
                            className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-200 transition-all duration-200"
                          />
                        </div>
                        <div>
                          <label htmlFor="endDate" className="block text-sm font-medium text-gray-700 mb-2">
                            End Date
                          </label>
                          <input
                            id="endDate"
                            type="date"
                            value={endDate}
                            onChange={e => setEndDate(e.target.value)}
                            className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-200 transition-all duration-200"
                          />
                        </div>
                      </div>
                    )}

                    <div>
                      <label htmlFor="count" className="block text-sm font-medium text-gray-700 mb-2">
                        Number of Tweets
                      </label>
                      <input
                        id="count"
                        type="number"
                        min="1"
                        max="200"
                        value={count}
                        onChange={e => setCount(parseInt(e.target.value))}
                        placeholder="Max 200"
                        className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-200 transition-all duration-200"
                      />
                    </div>
                  </div>

                  {error && (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
                      ⚠️ {error}
                    </div>
                  )}

                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-primary-gradient text-white py-3 px-6 rounded-lg font-semibold text-lg 
                             hover:shadow-lg hover:shadow-primary-500/25 transform hover:-translate-y-0.5 
                             transition-all duration-200 disabled:opacity-60 disabled:cursor-not-allowed 
                             disabled:transform-none flex items-center justify-center gap-2"
                  >
                    {loading ? (
                      <>
                        <div className="loading-spinner"></div>
                        Scraping...
                      </>
                    ) : (
                      <>
                        🚀 Start Scraping
                      </>
                    )}
                  </button>
                </form>
              </div>
            </div>

            {/* Results Section */}
            <div className="lg:col-span-2">
              <div className="bg-white/95 backdrop-blur-sm rounded-2xl shadow-2xl border border-white/20 overflow-hidden">
                {/* Results Header */}
                <div className="bg-gradient-to-r from-primary-50 to-secondary-50 px-6 py-4 border-b border-gray-200">
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                    <div className="flex items-center gap-3">
                      <h2 className="text-xl font-semibold text-gray-800">📊 Results</h2>
                      {filteredTweets.length > 0 && (
                        <span className="bg-primary-gradient text-white px-3 py-1 rounded-full text-sm font-medium">
                          {filteredTweets.length} tweet{filteredTweets.length !== 1 ? 's' : ''}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Filters */}
                {tweets.length > 0 && (
                  <div className="p-4 bg-gray-50 border-b border-gray-200">
                    <div className="flex flex-col sm:flex-row gap-4">
                      <div className="flex-1">
                        <label htmlFor="usernameFilter" className="block text-sm font-medium text-gray-700 mb-1">
                          Filter by Username
                        </label>
                        <input
                          id="usernameFilter"
                          type="text"
                          value={usernameFilter}
                          onChange={e => setUsernameFilter(e.target.value)}
                          placeholder="Enter username to filter..."
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:border-primary-500 focus:ring-1 focus:ring-primary-200 transition-all duration-200 text-sm"
                        />
                      </div>
                      <div className="flex-1">
                        <label htmlFor="keywordFilter" className="block text-sm font-medium text-gray-700 mb-1">
                          Filter by Keyword
                        </label>
                        <input
                          id="keywordFilter"
                          type="text"
                          value={keywordFilter}
                          onChange={e => setKeywordFilter(e.target.value)}
                          placeholder="Enter keyword to filter..."
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:border-primary-500 focus:ring-1 focus:ring-primary-200 transition-all duration-200 text-sm"
                        />
                      </div>
                      <div className="flex items-end">
                        <button
                          onClick={() => {
                            setUsernameFilter('');
                            setKeywordFilter('');
                          }}
                          className="px-4 py-2 text-gray-600 hover:text-gray-800 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors duration-200 text-sm"
                        >
                          Clear Filters
                        </button>
                      </div>
                    </div>
                  </div>
                )}

                {/* Results Content */}
                <div className="p-6">
                  {tweets.length === 0 && !loading && (
                    <div className="text-center py-16">
                      <div className="text-6xl mb-4">🔍</div>
                      <h3 className="text-xl font-semibold text-gray-600 mb-2">No tweets to display</h3>
                      <p className="text-gray-500">Configure your search parameters and click "Start Scraping" to begin</p>
                    </div>
                  )}

                  {filteredTweets.length > 0 && (
                    <TweetTable 
                      tweets={filteredTweets} 
                      onExportCSV={exportToCSV}
                      onExportExcel={exportToExcel}
                    />
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
