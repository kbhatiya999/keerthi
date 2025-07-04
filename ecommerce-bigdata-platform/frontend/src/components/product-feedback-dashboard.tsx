'use client';

import { useState, useEffect } from 'react';
import { Star, MessageCircle, TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface FeedbackItem {
  id: string;
  text: string;
  rating: number;
  feedback_type: string;
  created_at: string;
  user_name?: string;
  product_id?: string;
  product_name?: string;
  sentiment_score?: number;
  sentiment_label?: string;
}

interface FeedbackStats {
  total_feedback: number;
  average_rating: number;
  positive_sentiment: number;
  negative_sentiment: number;
  neutral_sentiment: number;
}

export default function ProductFeedbackDashboard() {
  const [feedback, setFeedback] = useState<FeedbackItem[]>([]);
  const [stats, setStats] = useState<FeedbackStats>({
    total_feedback: 0,
    average_rating: 0,
    positive_sentiment: 0,
    negative_sentiment: 0,
    neutral_sentiment: 0
  });
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState('all'); // all, positive, negative, neutral
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadFeedback();
  }, []);

  const loadFeedback = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/feedback/all', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setFeedback(data.feedback || []);
        calculateStats(data.feedback || []);
      }
    } catch (error) {
      console.error('Failed to load feedback:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = (feedbackData: FeedbackItem[]) => {
    const total = feedbackData.length;
    const avgRating = total > 0 ? feedbackData.reduce((sum, item) => sum + item.rating, 0) / total : 0;
    const positive = feedbackData.filter(item => item.sentiment_label === 'positive').length;
    const negative = feedbackData.filter(item => item.sentiment_label === 'negative').length;
    const neutral = feedbackData.filter(item => item.sentiment_label === 'neutral').length;

    setStats({
      total_feedback: total,
      average_rating: avgRating,
      positive_sentiment: positive,
      negative_sentiment: negative,
      neutral_sentiment: neutral
    });
  };

  const getFilteredFeedback = () => {
    let filtered = feedback;

    // Apply sentiment filter
    if (filter !== 'all') {
      filtered = filtered.filter(item => item.sentiment_label === filter);
    }

    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(item => 
        item.text.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.product_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.user_name?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    return filtered;
  };

  const getSentimentColor = (label?: string) => {
    switch (label?.toLowerCase()) {
      case 'positive': return 'text-green-600 bg-green-50';
      case 'negative': return 'text-red-600 bg-red-50';
      case 'neutral': return 'text-gray-600 bg-gray-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getSentimentIcon = (label?: string) => {
    switch (label?.toLowerCase()) {
      case 'positive': return <TrendingUp className="h-4 w-4" />;
      case 'negative': return <TrendingDown className="h-4 w-4" />;
      default: return <Minus className="h-4 w-4" />;
    }
  };

  const filteredFeedback = getFilteredFeedback();

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          Product Feedback Dashboard
        </h2>
        
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-6">
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="flex items-center">
              <MessageCircle className="h-8 w-8 text-blue-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-blue-600">Total Feedback</p>
                <p className="text-2xl font-bold text-blue-900">{stats.total_feedback}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-yellow-50 p-4 rounded-lg">
            <div className="flex items-center">
              <Star className="h-8 w-8 text-yellow-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-yellow-600">Average Rating</p>
                <p className="text-2xl font-bold text-yellow-900">{stats.average_rating.toFixed(1)}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-green-50 p-4 rounded-lg">
            <div className="flex items-center">
              <TrendingUp className="h-8 w-8 text-green-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-green-600">Positive</p>
                <p className="text-2xl font-bold text-green-900">{stats.positive_sentiment}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-red-50 p-4 rounded-lg">
            <div className="flex items-center">
              <TrendingDown className="h-8 w-8 text-red-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-red-600">Negative</p>
                <p className="text-2xl font-bold text-red-900">{stats.negative_sentiment}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="flex items-center">
              <Minus className="h-8 w-8 text-gray-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-600">Neutral</p>
                <p className="text-2xl font-bold text-gray-900">{stats.neutral_sentiment}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <div className="flex-1">
            <input
              type="text"
              placeholder="Search feedback, products, or users..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Sentiments</option>
            <option value="positive">Positive</option>
            <option value="negative">Negative</option>
            <option value="neutral">Neutral</option>
          </select>
        </div>
      </div>

      {/* Feedback List */}
      <div>
        <h3 className="text-lg font-semibold mb-4">
          Feedback ({filteredFeedback.length})
        </h3>

        {loading ? (
          <div className="flex justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : filteredFeedback.length > 0 ? (
          <div className="space-y-4">
            {filteredFeedback.map((item) => (
              <div key={item.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    <div className="flex">
                      {[1, 2, 3, 4, 5].map((star) => (
                        <Star
                          key={star}
                          className={`h-4 w-4 ${
                            star <= item.rating ? 'text-yellow-400 fill-current' : 'text-gray-300'
                          }`}
                        />
                      ))}
                    </div>
                    <span className="text-sm text-gray-500">
                      {new Date(item.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  
                  <div className={`flex items-center space-x-2 px-3 py-1 rounded-full ${getSentimentColor(item.sentiment_label)}`}>
                    {getSentimentIcon(item.sentiment_label)}
                    <span className="text-sm font-medium capitalize">
                      {item.sentiment_label || 'Unknown'}
                    </span>
                    {item.sentiment_score && (
                      <span className="text-xs">
                        ({item.sentiment_score.toFixed(2)})
                      </span>
                    )}
                  </div>
                </div>
                
                <p className="text-gray-700 mb-3">{item.text}</p>
                
                <div className="flex items-center justify-between text-sm text-gray-500">
                  <div className="flex items-center space-x-4">
                    <span>{item.user_name || 'Anonymous'}</span>
                    <span className="capitalize">{item.feedback_type}</span>
                    {item.product_name && (
                      <span className="text-blue-600">Product: {item.product_name}</span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <MessageCircle className="h-12 w-12 mx-auto mb-2 text-gray-300" />
            <p>No feedback found matching your criteria.</p>
          </div>
        )}
      </div>
    </div>
  );
} 