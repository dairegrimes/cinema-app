'use client';

import { useState } from 'react';

interface SearchCardProps {
  onSearch?: (filters: SearchFilters) => void;
}

interface SearchFilters {
  film: string;
  cinema: string;
  searchQuery: string;
}

export default function SearchCard({ onSearch }: SearchCardProps) {
  const [selectedFilm, setSelectedFilm] = useState('');
  const [selectedCinema, setSelectedCinema] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  // Placeholder data - replace with API calls later
  const films = [
    'All Films',
    'Dune: Part Two',
    'Oppenheimer',
    'Poor Things',
    'The Zone of Interest',
    'Killers of the Flower Moon',
  ];

  const cinemas = [
    'All Cinemas',
    'Omniplex Dublin Rathmines',
    'Cineworld Dublin',
    'IMC Dun Laoghaire',
    'Light House Cinema',
    'Irish Film Institute',
  ];

  const handleSearch = () => {
    if (onSearch) {
      onSearch({
        film: selectedFilm,
        cinema: selectedCinema,
        searchQuery,
      });
    }
    console.log('Search:', { selectedFilm, selectedCinema, searchQuery });
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      <div className="bg-white dark:bg-zinc-900 rounded-2xl shadow-lg p-6 md:p-8">
        <h2 className="text-2xl font-bold text-zinc-900 dark:text-zinc-50 mb-6">
          Find Your Perfect Showing
        </h2>
        
        <div className="space-y-4">
          {/* Dropdown Row */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Film Dropdown */}
            <div className="flex flex-col">
              <label 
                htmlFor="film-select" 
                className="text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2"
              >
                Film
              </label>
              <select
                id="film-select"
                value={selectedFilm}
                onChange={(e) => setSelectedFilm(e.target.value)}
                className="w-full px-4 py-3 rounded-lg border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 transition-colors cursor-pointer"
              >
                <option value="">Select a film</option>
                {films.map((film) => (
                  <option key={film} value={film}>
                    {film}
                  </option>
                ))}
              </select>
            </div>

            {/* Cinema Dropdown */}
            <div className="flex flex-col">
              <label 
                htmlFor="cinema-select" 
                className="text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2"
              >
                Cinema
              </label>
              <select
                id="cinema-select"
                value={selectedCinema}
                onChange={(e) => setSelectedCinema(e.target.value)}
                className="w-full px-4 py-3 rounded-lg border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 transition-colors cursor-pointer"
              >
                <option value="">Select a cinema</option>
                {cinemas.map((cinema) => (
                  <option key={cinema} value={cinema}>
                    {cinema}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Search Bar */}
          <div className="flex flex-col">
            <label 
              htmlFor="search-input" 
              className="text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2"
            >
              Search
            </label>
            <div className="flex gap-2">
              <div className="relative flex-1">
                <input
                  id="search-input"
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Search for films, cinemas, or showtimes..."
                  className="w-full px-4 py-3 pl-11 rounded-lg border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 placeholder-zinc-400 dark:placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 transition-colors"
                />
                <svg
                  className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-400 dark:text-zinc-500"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                  />
                </svg>
              </div>
              <button
                onClick={handleSearch}
                className="px-6 py-3 bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 text-white font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 focus:ring-offset-2"
              >
                Search
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
