'use client';

import { useEffect, useMemo, useState } from 'react';

import { fetchListings, formatListingTime } from '@/lib/api';
import type { Listing } from '@/lib/types';

interface SearchFilters {
  film: string;
  cinema: string;
  searchQuery: string;
}

export default function SearchCard() {
  const [listings, setListings] = useState<Listing[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedFilm, setSelectedFilm] = useState('');
  const [selectedCinema, setSelectedCinema] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<SearchFilters>({
    film: '',
    cinema: '',
    searchQuery: '',
  });

  useEffect(() => {
    fetchListings()
      .then(setListings)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const films = useMemo(
    () => [...new Set(listings.map((l) => l.movie))].sort(),
    [listings],
  );

  const cinemas = useMemo(
    () => [...new Set(listings.map((l) => l.venue))].sort(),
    [listings],
  );

  const filteredListings = useMemo(() => {
    const query = filters.searchQuery.trim().toLowerCase();
    return listings.filter((listing) => {
      if (filters.film && listing.movie !== filters.film) return false;
      if (filters.cinema && listing.venue !== filters.cinema) return false;
      if (!query) return true;
      const haystack = [
        listing.movie,
        listing.venue,
        formatListingTime(listing.time),
      ].join(' ').toLowerCase();
      return haystack.includes(query);
    });
  }, [listings, filters]);

  const handleSearch = () => {
    setFilters({
      film: selectedFilm,
      cinema: selectedCinema,
      searchQuery,
    });
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto space-y-8">
      <div className="bg-white dark:bg-zinc-900 rounded-2xl shadow-lg p-6 md:p-8">
        <h2 className="text-2xl font-bold text-zinc-900 dark:text-zinc-50 mb-6">
          Find Your Perfect Showing
        </h2>

        {loading && (
          <p className="text-zinc-500 dark:text-zinc-400">Loading listings…</p>
        )}

        {error && (
          <p className="text-red-600 dark:text-red-400">{error}</p>
        )}

        {!loading && !error && (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
                  <option value="">All films</option>
                  {films.map((film) => (
                    <option key={film} value={film}>
                      {film}
                    </option>
                  ))}
                </select>
              </div>

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
                  <option value="">All cinemas</option>
                  {cinemas.map((cinema) => (
                    <option key={cinema} value={cinema}>
                      {cinema}
                    </option>
                  ))}
                </select>
              </div>
            </div>

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
                    onKeyDown={handleKeyPress}
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
        )}
      </div>

      {!loading && !error && (
        <div className="bg-white dark:bg-zinc-900 rounded-2xl shadow-lg p-6 md:p-8">
          <h3 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50 mb-4">
            {filteredListings.length} showing{filteredListings.length === 1 ? '' : 's'}
          </h3>

          {filteredListings.length === 0 ? (
            <p className="text-zinc-500 dark:text-zinc-400">
              No listings match your search.
            </p>
          ) : (
            <ul className="divide-y divide-zinc-200 dark:divide-zinc-800">
              {filteredListings.map((listing) => (
                <li
                  key={listing.id}
                  className="py-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2"
                >
                  <div>
                    <p className="font-medium text-zinc-900 dark:text-zinc-50">
                      {listing.movie}
                    </p>
                    <p className="text-sm text-zinc-600 dark:text-zinc-400">
                      {listing.venue}
                    </p>
                  </div>
                  <div className="flex items-center gap-3">
                    <time className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
                      {formatListingTime(listing.time)}
                    </time>
                    {listing.maxx && (
                      <span className="text-xs font-semibold uppercase tracking-wide px-2 py-1 rounded bg-yellow-400 text-black">
                        MAXX
                      </span>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
