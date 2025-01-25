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
      const response = await axios.post("http://127.0.0.1:8000/search", {
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
    <div className="min-h-screen bg-gray-100 p-6 flex items-center justify-center">
      <div className="max-w-4xl w-full mx-auto search-container">
        {/* Search Bar */}
        <div className="search-bar flex items-center">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search for something..."
            className="flex-1 p-4 outline-none"
          />
          <button
            onClick={handleSearch}
            disabled={loading}
            className="p-4 hover:bg-blue-700 transition-colors rounded-full"
          >
            {loading ? <FaSpinner className="animate-spin" /> : <FaSearch />}
          </button>
        </div>

        {/* Error Message */}
        {error && <p className="text-red-500 mt-4">{error}</p>}

        {/* Search Results */}
        <div className="mt-6 space-y-4">
          {results.map((result, index) => (
            <div key={index} className="result-item">
              <h2 className="text-2xl font-semibold">{result.Title}</h2>
              <p className="mt-2">{result.Edition_Info}</p>
            </div>
          ))}
        </div>

        {/* No Results Message */}
        {!loading && results.length === 0 && query && (
          <p className="text-gray-600 mt-4">No results found.</p>
        )}
      </div>
    </div>
  );
};

export default Search;
