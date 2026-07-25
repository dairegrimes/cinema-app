'use client';

import { useEffect, useMemo, useState } from 'react';

import { createSubscription, fetchListings } from '@/lib/api';
import type { Listing } from '@/lib/types';

export default function AlertForm() {
  const [listings, setListings] = useState<Listing[]>([]);
  const [email, setEmail] = useState('');
  const [movie, setMovie] = useState('');
  const [venue, setVenue] = useState('');
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchListings()
      .then(setListings)
      .catch(() => setListings([]));
  }, []);

  const movies = useMemo(
    () => [...new Set(listings.map((l) => l.movie))].sort(),
    [listings],
  );
  const venues = useMemo(
    () => [...new Set(listings.map((l) => l.venue))].sort(),
    [listings],
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !movie) {
      setStatus('error');
      setMessage('Please enter your email and choose a movie.');
      return;
    }
    setStatus('loading');
    setMessage('');
    try {
      const result = await createSubscription({
        email,
        movie_name: movie,
        venue_name: venue || undefined,
      });
      setStatus('success');
      setMessage(result.message);
      setEmail('');
      setMovie('');
      setVenue('');
    } catch (err) {
      setStatus('error');
      setMessage(err instanceof Error ? err.message : 'Something went wrong.');
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto bg-white dark:bg-zinc-900 rounded-2xl shadow-lg p-6 md:p-8">
      <h2 className="text-2xl font-bold text-zinc-900 dark:text-zinc-50 mb-2">
        Get alerted when a movie is scheduled
      </h2>
      <p className="text-sm text-zinc-600 dark:text-zinc-400 mb-6">
        We&apos;ll email you when your chosen movie gets a new showtime. Confirm via the
        link we send, and unsubscribe anytime.
      </p>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex flex-col">
            <label
              htmlFor="alert-movie"
              className="text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2"
            >
              Movie
            </label>
            <input
              id="alert-movie"
              list="alert-movie-options"
              value={movie}
              onChange={(e) => setMovie(e.target.value)}
              placeholder="Type or pick a movie"
              className="w-full px-4 py-3 rounded-lg border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <datalist id="alert-movie-options">
              {movies.map((m) => (
                <option key={m} value={m} />
              ))}
            </datalist>
          </div>

          <div className="flex flex-col">
            <label
              htmlFor="alert-venue"
              className="text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2"
            >
              Cinema (optional)
            </label>
            <select
              id="alert-venue"
              value={venue}
              onChange={(e) => setVenue(e.target.value)}
              className="w-full px-4 py-3 rounded-lg border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer"
            >
              <option value="">Any cinema</option>
              {venues.map((v) => (
                <option key={v} value={v}>
                  {v}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="flex flex-col">
          <label
            htmlFor="alert-email"
            className="text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2"
          >
            Email
          </label>
          <div className="flex gap-2">
            <input
              id="alert-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              className="flex-1 px-4 py-3 rounded-lg border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 placeholder-zinc-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              type="submit"
              disabled={status === 'loading'}
              className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {status === 'loading' ? 'Subscribing…' : 'Alert me'}
            </button>
          </div>
        </div>

        {message && (
          <p
            className={
              status === 'error'
                ? 'text-red-600 dark:text-red-400 text-sm'
                : 'text-green-600 dark:text-green-400 text-sm'
            }
          >
            {message}
          </p>
        )}
      </form>
    </div>
  );
}
