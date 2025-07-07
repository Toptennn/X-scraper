# 𝕏 Scraper Dashboard

A modern, responsive Twitter/X scraper dashboard built with **Next.js 13**, **TypeScript**, and **Tailwind CSS**.

## 🚀 Tech Stack

- **Next.js 13** - React framework for production
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **React 18** - Latest React with hooks
- **SheetJS (xlsx)** - Excel file generation
- **PapaParse** - CSV parsing and generation

## Features

### 🎨 Modern UI with Tailwind CSS
- Clean, responsive design with gradient backgrounds
- Mobile-first approach with adaptive layouts
- Smooth animations and transitions
- Professional color scheme with custom gradients

### 📊 Advanced Data Display
- **Table Format**: Data displayed in a comprehensive table with the following columns:
  - Post Date (sortable)
  - Username (sortable)
  - Text (Post Content with expand/collapse)
  - URL (Link to the post)
  - Retweet Count (sortable, formatted)
  - Favorite Count (sortable, formatted)
  - Reply Count (sortable, formatted)

### 🔧 Enhanced Features
- **Responsive Design**: 
  - Desktop: Full table view with sortable columns
  - Mobile: Card-based layout optimized for smaller screens
- **Text Expansion**: Click "Show more/less" to expand/collapse long tweet text
- **Sortable Columns**: Click on column headers to sort by different criteria
- **Real-time Filtering**: Filter tweets by username and keywords
- **Export Options**: Download data in CSV and Excel formats
- **Type Safety**: Full TypeScript support with comprehensive type definitions

### 🔍 Filtering Options
- **Username Filter**: Filter tweets by specific usernames
- **Keyword Filter**: Search for tweets containing specific keywords
- **Clear Filters**: Reset all filters with one click
- **Real-time Updates**: Filters update results immediately

### 📥 Export Capabilities
- **CSV Export**: Export filtered data to CSV format using PapaParse
- **Excel Export**: Export filtered data to Excel format using SheetJS
- **Filtered Exports**: Only export the currently filtered/visible data
- **Formatted Data**: Proper column headers and data formatting

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

## TypeScript Support

This project is fully typed with TypeScript for better development experience:

- **Type Checking**: Run `npm run type-check` to check types
- **Strict Mode**: Enabled for maximum type safety
- **Interface Definitions**: Comprehensive type definitions in `types/index.ts`
- **Component Props**: All components have proper TypeScript interfaces
- **API Responses**: Typed API responses and data structures

## Project Structure

```
frontend/
├── components/
│   └── TweetTable.tsx     # Advanced table component (TypeScript)
├── pages/
│   ├── _app.tsx          # Next.js app configuration (TypeScript)
│   └── index.tsx         # Main dashboard page (TypeScript)
├── types/
│   └── index.ts          # TypeScript type definitions
├── styles/
│   └── globals.css       # Global styles with Tailwind CSS
├── package.json
├── tsconfig.json         # TypeScript configuration
├── tailwind.config.js    # Tailwind CSS configuration
├── postcss.config.js     # PostCSS configuration
├── next-env.d.ts         # Next.js TypeScript definitions
└── next.config.js        # Next.js configuration
```

## Dependencies

### Core Dependencies
- `next` - React framework for production
- `react` - React library
- `react-dom` - React DOM library
- `typescript` - TypeScript language support

### Type Definitions
- `@types/react` - React TypeScript definitions
- `@types/react-dom` - React DOM TypeScript definitions
- `@types/node` - Node.js TypeScript definitions
- `@types/papaparse` - PapaParse TypeScript definitions

### Styling
- `tailwindcss` - Utility-first CSS framework
- `postcss` - CSS post-processor
- `autoprefixer` - CSS vendor prefix automation

### Data Export
- `xlsx` - Excel file generation and parsing
- `papaparse` - CSV parsing and generation

## Scripts

```bash
# Development
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server

# Type Checking
npm run type-check   # Run TypeScript type checking
npm run lint         # Run ESLint
```

## Type Definitions

Key interfaces and types used throughout the application:

```typescript
interface Tweet {
  tweet_id?: string;
  username: string;
  text: string;
  created_at: string;
  url?: string;
  retweet_count?: number;
  favorite_count?: number;
  reply_count?: number;
}

interface Toast {
  message: string;
  type: 'success' | 'error';
}

type SortDirection = 'asc' | 'desc';
```

## Usage

1. **Authentication**: Enter your Twitter/X credentials
2. **Select Search Mode**: Choose from timeline, date range, popular, or latest tweets
3. **Configure Parameters**: Set search query, username, date range, and tweet count
4. **Start Scraping**: Click the "Start Scraping" button
5. **View Results**: Browse the data in the responsive table with TypeScript intellisense
6. **Filter Results**: Use the username and keyword filters to narrow down results
7. **Export Data**: Use the export buttons to download CSV or Excel files

## Responsive Design

The dashboard is fully responsive with TypeScript support:
- **Desktop (≥768px)**: Full table view with sortable columns
- **Mobile (<768px)**: Card-based layout with expandable content
- **Tablet**: Adaptive layout that works well on medium screens

## Development with TypeScript

- **IntelliSense**: Full autocomplete and type checking in your editor
- **Refactoring**: Safe refactoring with TypeScript's type system
- **Error Prevention**: Catch errors at compile time, not runtime
- **Documentation**: Self-documenting code with TypeScript interfaces

## Browser Compatibility

- Chrome (recommended)
- Firefox
- Safari
- Edge
- All modern browsers with TypeScript compilation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes (TypeScript preferred)
4. Run type checking: `npm run type-check`
5. Test thoroughly
6. Submit a pull request

## License

This project is licensed under the MIT License.
