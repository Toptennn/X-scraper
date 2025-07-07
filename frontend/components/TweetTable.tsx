import { useState } from 'react';
import type { Tweet, SortDirection } from '../types';

interface SortIconProps {
  field: string;
  sortField: string;
  sortDirection: SortDirection;
}

interface TweetTableProps {
  tweets: Tweet[];
  onExportCSV: () => void;
  onExportExcel: () => void;
}

const SortIcon = ({ field, sortField, sortDirection }: SortIconProps) => {
  if (sortField !== field) {
    return <span className="text-gray-400 ml-1">↕️</span>;
  }
  return sortDirection === 'asc' ? 
    <span className="text-primary-600 ml-1">↑</span> : 
    <span className="text-primary-600 ml-1">↓</span>;
};

const TweetTable = ({ tweets, onExportCSV, onExportExcel }: TweetTableProps) => {
  const [sortField, setSortField] = useState<string>('created_at');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set());

  const handleSort = (field: string) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const toggleRowExpansion = (index: number) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedRows(newExpanded);
  };

  const sortedTweets = [...tweets].sort((a, b) => {
    let aValue: any = a[sortField as keyof Tweet];
    let bValue: any = b[sortField as keyof Tweet];

    if (sortField === 'created_at') {
      aValue = new Date(aValue);
      bValue = new Date(bValue);
    } else if (typeof aValue === 'string' && typeof bValue === 'string') {
      aValue = aValue.toLowerCase();
      bValue = bValue.toLowerCase();
    }

    // Handle null/undefined values
    if (aValue == null && bValue == null) return 0;
    if (aValue == null) return sortDirection === 'asc' ? -1 : 1;
    if (bValue == null) return sortDirection === 'asc' ? 1 : -1;

    if (aValue < bValue) return sortDirection === 'asc' ? -1 : 1;
    if (aValue > bValue) return sortDirection === 'asc' ? 1 : -1;
    return 0;
  });

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

  const formatNumber = (num?: number): string => {
    if (num == null) return '0';
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  };

  return (
    <div className="overflow-hidden">
      {/* Mobile Cards View */}
      <div className="block md:hidden space-y-4">
        {sortedTweets.map((tweet, index) => (
          <div key={tweet.tweet_id ?? index} className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex justify-between items-start mb-3">
              <div className="flex-1">
                <div className="font-semibold text-gray-900">@{tweet.username}</div>
                <div className="text-sm text-gray-500">{formatDate(tweet.created_at)}</div>
              </div>
              <a
                href={tweet.url ?? `https://twitter.com/${tweet.username}/status/${tweet.tweet_id}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary-600 hover:text-primary-800 text-sm font-medium"
              >
                View
              </a>
            </div>
            
            <div className="mb-3">
              <div className={`text-gray-700 text-sm ${expandedRows.has(index) ? '' : 'line-clamp-3'}`}>
                {tweet.text}
              </div>
              {tweet.text && tweet.text.length > 100 && (
                <button
                  onClick={() => toggleRowExpansion(index)}
                  className="text-primary-600 hover:text-primary-800 text-sm mt-1 font-medium"
                >
                  {expandedRows.has(index) ? 'Show less' : 'Show more'}
                </button>
              )}
            </div>
            
            <div className="flex justify-between text-sm text-gray-500 pt-2 border-t border-gray-100">
              <span className="flex items-center gap-1">
                <span>💬</span>
                <span>{formatNumber(tweet.reply_count)}</span>
              </span>
              <span className="flex items-center gap-1">
                <span>🔁</span>
                <span>{formatNumber(tweet.retweet_count)}</span>
              </span>
              <span className="flex items-center gap-1">
                <span>❤️</span>
                <span>{formatNumber(tweet.favorite_count)}</span>
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Desktop Table View */}
      <div className="hidden md:block overflow-x-auto">
        <table className="w-full border-collapse bg-white rounded-lg overflow-hidden shadow-sm">
          <thead>
            <tr className="bg-gray-50">
              <th 
                className="px-4 py-3 text-left text-sm font-semibold text-gray-700 border-b cursor-pointer hover:bg-gray-100 transition-colors select-none"
                onClick={() => handleSort('created_at')}
              >
                <div className="flex items-center">
                  Post Date
                  <SortIcon field="created_at" sortField={sortField} sortDirection={sortDirection} />
                </div>
              </th>
              <th 
                className="px-4 py-3 text-left text-sm font-semibold text-gray-700 border-b cursor-pointer hover:bg-gray-100 transition-colors select-none"
                onClick={() => handleSort('username')}
              >
                <div className="flex items-center">
                  Username
                  <SortIcon field="username" sortField={sortField} sortDirection={sortDirection} />
                </div>
              </th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700 border-b">
                Text
              </th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700 border-b">
                URL
              </th>
              <th 
                className="px-4 py-3 text-center text-sm font-semibold text-gray-700 border-b cursor-pointer hover:bg-gray-100 transition-colors select-none"
                onClick={() => handleSort('retweet_count')}
              >
                <div className="flex items-center justify-center">
                  Retweets
                  <SortIcon field="retweet_count" sortField={sortField} sortDirection={sortDirection} />
                </div>
              </th>
              <th 
                className="px-4 py-3 text-center text-sm font-semibold text-gray-700 border-b cursor-pointer hover:bg-gray-100 transition-colors select-none"
                onClick={() => handleSort('favorite_count')}
              >
                <div className="flex items-center justify-center">
                  Likes
                  <SortIcon field="favorite_count" sortField={sortField} sortDirection={sortDirection} />
                </div>
              </th>
              <th 
                className="px-4 py-3 text-center text-sm font-semibold text-gray-700 border-b cursor-pointer hover:bg-gray-100 transition-colors select-none"
                onClick={() => handleSort('reply_count')}
              >
                <div className="flex items-center justify-center">
                  Replies
                  <SortIcon field="reply_count" sortField={sortField} sortDirection={sortDirection} />
                </div>
              </th>
            </tr>
          </thead>
          <tbody>
            {sortedTweets.map((tweet, index) => (
              <tr key={tweet.tweet_id ?? index} className="hover:bg-gray-50 transition-colors duration-150">
                <td className="px-4 py-3 text-sm text-gray-600 border-b whitespace-nowrap">
                  {formatDate(tweet.created_at)}
                </td>
                <td className="px-4 py-3 text-sm font-medium text-gray-800 border-b">
                  @{tweet.username}
                </td>
                <td className="px-4 py-3 text-sm text-gray-700 border-b max-w-md">
                  <div className={`${expandedRows.has(index) ? '' : 'line-clamp-2'}`} title={tweet.text}>
                    {tweet.text}
                  </div>
                  {tweet.text && tweet.text.length > 100 && (
                    <button
                      onClick={() => toggleRowExpansion(index)}
                      className="text-primary-600 hover:text-primary-800 text-xs mt-1 font-medium"
                    >
                      {expandedRows.has(index) ? 'Show less' : 'Show more'}
                    </button>
                  )}
                </td>
                <td className="px-4 py-3 text-sm border-b">
                  <a
                    href={tweet.url ?? `https://twitter.com/${tweet.username}/status/${tweet.tweet_id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary-600 hover:text-primary-800 hover:underline font-medium"
                  >
                    View Tweet
                  </a>
                </td>
                <td className="px-4 py-3 text-sm text-gray-600 border-b text-center">
                  {formatNumber(tweet.retweet_count)}
                </td>
                <td className="px-4 py-3 text-sm text-gray-600 border-b text-center">
                  {formatNumber(tweet.favorite_count)}
                </td>
                <td className="px-4 py-3 text-sm text-gray-600 border-b text-center">
                  {formatNumber(tweet.reply_count)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Export Actions */}
      <div className="flex flex-col sm:flex-row gap-2 mt-6 justify-center md:justify-end">
        <button
          onClick={onExportCSV}
          className="bg-green-500 hover:bg-green-600 text-white px-6 py-2 rounded-lg text-sm font-medium transition-all duration-200 flex items-center justify-center gap-2 hover:shadow-lg"
        >
          <span>📄</span> Export CSV
        </button>
        <button
          onClick={onExportExcel}
          className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-lg text-sm font-medium transition-all duration-200 flex items-center justify-center gap-2 hover:shadow-lg"
        >
          <span>📊</span> Export Excel
        </button>
      </div>
    </div>
  );
};

export default TweetTable;
