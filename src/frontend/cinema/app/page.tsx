import SearchCard from "./components/SearchCard";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-zinc-50 to-zinc-100 dark:from-zinc-950 dark:to-black font-sans">
      <main className="container mx-auto px-4 py-12 md:py-20">
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-zinc-900 dark:text-zinc-50 mb-4">
            Cinema Listings
          </h1>
          <p className="text-lg text-zinc-600 dark:text-zinc-400 max-w-2xl mx-auto">
            Find the perfect movie showing near you. Search by film, cinema, or browse all listings.
          </p>
        </div>
        
        <SearchCard />
        
        <div className="mt-16 text-center">
          <p className="text-sm text-zinc-500 dark:text-zinc-600">
            More features coming soon...
          </p>
        </div>
      </main>
    </div>
  );
}
