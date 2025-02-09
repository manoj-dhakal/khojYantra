import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

const Case = () => {
  const { filename } = useParams();
  const [article, setArticle] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchArticle = async () => {
      try {
        const response = await axios.get(`http://127.0.0.1:8000/articles/${filename}`);
        setArticle(response.data);
      } catch (err) {
        setError('Article not found');
      } finally {
        setLoading(false);
      }
    };
    fetchArticle();
  }, [filename]);

  const formatFaisalaText = (text) => {
    return text.split('\n').map((line, index) => (
      <p key={index} className="mb-2">
        {line.startsWith('§ ') ? (
          <span className="text-red-400 font-semibold">{line}</span>
        ) : (
          line
        )}
      </p>
    ));
  };

  if (loading) return <div className="text-white text-center p-8">Loading...</div>;
  if (error) return <div className="text-red-500 text-center p-8">{error}</div>;

  return (
    <div className="min-h-screen bg-black text-white p-8 max-w-4xl mx-auto">
      {/* Case Header */}
      <div className="mb-8 border-b border-red-600 pb-4">
        <h1 className="text-3xl font-bold text-red-500 mb-2">
          {article.Title}
        </h1>
        <p className="text-gray-400 text-lg">{article["Edition Info"]}</p>
      </div>

      {/* Metadata Section */}
      <div className="bg-gray-800 rounded-lg p-4 mb-6">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-red-400">फैसला मिति:</span> 
            {article["Post Meta"].split('\t')[0]}
          </div>
          <div>
            <span className="text-red-400">प्रकरण नं.:</span> 
            {article["Post Meta"].split('\t')[1]}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="prose prose-invert max-w-none">
        {/* Parties Involved */}
        <div className="mb-6 bg-gray-900 p-4 rounded-lg">
          <h2 className="text-xl text-red-400 mb-3">पक्षहरू:</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h3 className="text-red-300">पुनरावेदक/ प्रतिवादी:</h3>
              <p className="text-gray-300">{article["Faisala Detail"].split('\n')[6]}</p>
            </div>
            <div>
              <h3 className="text-red-300">विपक्षी/वादी:</h3>
              <p className="text-gray-300">{article["Faisala Detail"].split('\n')[8]}</p>
            </div>
          </div>
        </div>

        {/* Key Points */}
        <div className="mb-8">
          <h2 className="text-2xl text-red-400 mb-4">मुख्य बिन्दुहरू:</h2>
          <div className="space-y-4 text-gray-300">
            {formatFaisalaText(article["Faisala Detail"])}
          </div>
        </div>

        {/* Legal References */}
        <div className="bg-gray-800 p-4 rounded-lg mb-6">
          <h3 className="text-red-400 text-lg mb-2">सम्बन्धित कानून:</h3>
          <ul className="list-disc pl-6 text-gray-300">
            {article["Faisala Detail"].includes('मुलुकी ऐन') && (
              <li>मुलुकी ऐन, अंशबन्डाको महलको १० नं.</li>
            )}
            {article["Faisala Detail"].includes('न्याय प्रशासन ऐन') && (
              <li>न्याय प्रशासन ऐन, २०४८</li>
            )}
          </ul>
        </div>

        {/* Final Decision */}
        <div className="bg-red-900/20 p-4 rounded-lg">
          <h2 className="text-xl text-red-400 mb-3">अन्तिम निर्णय:</h2>
          <p className="text-gray-300">
            {article["Faisala Detail"].split('फैसला\n')[1]}
          </p>
        </div>
      </div>
    </div>
  );
};

export default Case;
