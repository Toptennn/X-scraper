# 𝕏 Scraper Dashboard

A modern, responsive Twitter/X scraper dashboard built with Next.js and Tailwind CSS.

## Features

### 🎨 Modern UI with Tailwind CSS
- Clean, responsive design with gradient backgrounds
- Mobile-first approach with adaptive layouts
- Smooth animations and transitions
- Professional color scheme

### 📊 Advanced Data Display
- **Table Format**: Data displayed in a comprehensive table with the following columns:
  - Post Date
  - Username
  - Text (Post Content)
  - URL (Link to the post)
  - Retweet Count
  - Favorite Count (Likes)
  - Reply Count

### 🔧 Enhanced Features
- **Responsive Design**: 
  - Desktop: Full table view with sortable columns
  - Mobile: Card-based layout optimized for smaller screens
- **Text Expansion**: Click "Show more/less" to expand/collapse long tweet text
- **Sortable Columns**: Click on column headers to sort by different criteria
- **Real-time Filtering**: Filter tweets by username and keywords
- **Export Options**: Download data in CSV and Excel formats

### 🔍 Filtering Options
- **Username Filter**: Filter tweets by specific usernames
- **Keyword Filter**: Search for tweets containing specific keywords
- **Clear Filters**: Reset all filters with one click

### 📥 Export Capabilities
- **CSV Export**: Export filtered data to CSV format using PapaParse
- **Excel Export**: Export filtered data to Excel format using SheetJS
- **Filtered Exports**: Only export the currently filtered/visible data

### 🚀 Search Modes
- **User Timeline**: Get tweets from specific users
- **Date Range Search**: Search tweets within a specific date range
- **Popular Tweets**: Fetch trending/popular tweets
- **Latest Tweets**: Get the most recent tweets

## Installation

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Run the development server**:
   ```bash
   npm run dev
   ```

4. **Open your browser** and navigate to `http://localhost:3000`

## Dependencies

### Core Dependencies
- `next`: React framework for production
- `react`: React library
- `react-dom`: React DOM library

### Styling
- `tailwindcss`: Utility-first CSS framework
- `postcss`: CSS post-processor
- `autoprefixer`: CSS vendor prefix automation

### Data Export
- `xlsx`: Excel file generation and parsing
- `papaparse`: CSV parsing and generation

## Project Structure

```
frontend/
├── components/
│   └── TweetTable.js       # Advanced table component with sorting and responsive design
├── pages/
│   ├── _app.js            # Next.js app configuration
│   └── index.js           # Main dashboard page
├── styles/
│   └── globals.css        # Global styles with Tailwind CSS
├── package.json
├── tailwind.config.js     # Tailwind CSS configuration
├── postcss.config.js      # PostCSS configuration
└── next.config.js         # Next.js configuration
```

## Usage

1. **Authentication**: Enter your Twitter/X credentials
2. **Select Search Mode**: Choose from timeline, date range, popular, or latest tweets
3. **Configure Parameters**: Set search query, username, date range, and tweet count
4. **Start Scraping**: Click the "Start Scraping" button
5. **View Results**: Browse the data in the responsive table
6. **Filter Results**: Use the username and keyword filters to narrow down results
7. **Export Data**: Use the export buttons to download CSV or Excel files

## Responsive Design

The dashboard is fully responsive:
- **Desktop (≥768px)**: Full table view with sortable columns
- **Mobile (<768px)**: Card-based layout with expandable content
- **Tablet**: Adaptive layout that works well on medium screens

## Export Features

### CSV Export
- Includes all filtered data
- Formatted with proper headers
- Compatible with Excel and other spreadsheet applications

### Excel Export
- Native Excel format (.xlsx)
- Includes all filtered data
- Proper column formatting and headers

## Browser Compatibility

- Chrome (recommended)
- Firefox
- Safari
- Edge

## Development

To modify the styling, edit:
- `styles/globals.css` for global styles
- `tailwind.config.js` for Tailwind configuration
- Component files for component-specific styling

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.
