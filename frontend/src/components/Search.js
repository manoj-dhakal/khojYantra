import React, { useState } from "react";
import axios from "axios";
import { FaSearch, FaSpinner } from "react-icons/fa";
import "./search.css"; // Import the CSS file

const Search = () => {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSearch = async () => {
    if (!query) return;

    setLoading(true);
    setError("");
    setResults([]);

    try {
      const response = await axios.post("http://127.0.01:8000/search", {
        phrase: query,
        top_k: 10,
      });
      setResults(response.data);
    } catch (err) {
      setError("An error occurred while fetching results.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white flex flex-col items-center justify-center">
      <h1 className="text-4xl font-bold text-red-600 mb-8">Khojyantra</h1>
      <div className="w-full max-w-2xl mx-auto search-container">
        {/* Search Bar */}
        <div className="search-bar flex items-center bg-gray-800 rounded-full shadow-lg p-4">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search for something..."
            className="flex-1 p-4 bg-transparent outline-none text-white text-lg"
          />
          <button
            onClick={handleSearch}
            disabled={loading}
            className="p-4 bg-red-600 text-white hover:bg-red-700 transition-colors rounded-full"
          >
            {loading ? <FaSpinner className="animate-spin" /> : <FaSearch />}
          </button>
        </div>

        {/* Error Message */}
        {error && <p className="text-red-500 mt-4">{error}</p>}

        {/* Search Results */}
        <div className="mt-6 w-full space-y-4">
          {results.map((result, index) => (
            <div key={index} className="result-item p-4 bg-gray-900 rounded-md shadow-md">
              <h2 className="text-xl font-semibold text-red-500">{result.Title}</h2>
              <p className="mt-2 text-gray-400">{result.Edition_Info}</p>
            </div>
          ))}
        </div>

        {/* No Results Message */}
        {!loading && results.length === 0 && query && (
          <p className="text-gray-400 mt-4">No results found.</p>
        )}
      </div>
    </div>
  );
};

export default Search;
