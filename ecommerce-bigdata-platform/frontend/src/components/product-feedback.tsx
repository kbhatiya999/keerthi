'use client';

import { useState, useEffect } from 'react';
import { Star, MessageCircle, ThumbsUp, ThumbsDown } from 'lucide-react';
import { useAuth } from '@/lib/auth-context';
import { api } from '@/lib/api';

interface ProductFeedbackProps {
  productId: string;
  productName: string;
  onClose?: () => void;
}

interface FeedbackItem {
  id: string;
  text: string;
  rating: number;
  feedback_type: string;
  created_at: string;
  user_name?: string;
  sentiment_score?: number;
  sentiment_label?: string;
}

interface FeedbackFormData {
  text: string;
  rating: number;
}

export default function ProductFeedback({ productId, productName, onClose }: ProductFeedbackProps) {
  const { user } = useAuth();
  const [feedback, setFeedback] = useState<FeedbackItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [message, setMessage] = useState('');
  
  const [formData, setFormData] = useState<FeedbackFormData>({
    text: '',
    rating: 5
  });

  useEffect(() => {
    loadProductFeedback();
  }, [productId]);

  const loadProductFeedback = async () => {
    try {
      setLoading(true);
      // This would be a new API endpoint to get product-specific feedback
      const response = await fetch(`/api/feedback/product/${productId}`);
      if (response.ok) {
        const data = await response.json();
        setFeedback(data.feedback || []);
      }
    } catch (error) {
      console.error('Failed to load feedback:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitFeedback = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) {
      setMessage('Please login to submit feedback');
      return;
    }

    setSubmitting(true);
    setMessage('');

    try {
      const response = await fetch('/api/feedback/product', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify({
          text: formData.text,
          rating: formData.rating,
          product_id: productId
        })
      });

      if (response.ok) {
        setMessage('Feedback submitted successfully!');
        setFormData({
          text: '',
          rating: 5
        });
        setShowForm(false);
        loadProductFeedback(); // Reload feedback
      } else {
        const error = await response.json();
        setMessage(`Error: ${error.detail || 'Failed to submit feedback'}`);
      }
    } catch (error) {
      setMessage('Error: Failed to submit feedback');
    } finally {
      setSubmitting(false);
    }
  };

  const getSentimentColor = (label?: string) => {
    switch (label?.toLowerCase()) {
      case 'positive': return 'text-green-600';
      case 'negative': return 'text-red-600';
      case 'neutral': return 'text-gray-600';
      default: return 'text-gray-600';
    }
  };

  const getSentimentIcon = (label?: string) => {
    switch (label?.toLowerCase()) {
      case 'positive': return <ThumbsUp className="h-4 w-4 text-green-600" />;
      case 'negative': return <ThumbsDown className="h-4 w-4 text-red-600" />;
      default: return <MessageCircle className="h-4 w-4 text-gray-600" />;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900">
          Product Feedback - {productName}
        </h2>
        {onClose && (
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            ✕
          </button>
        )}
      </div>

      {message && (
        <div className={`mb-4 p-3 rounded ${
          message.includes('Error') ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
        }`}>
          {message}
        </div>
      )}

      {/* Submit Feedback Button */}
      <div className="mb-6">
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
        >
          {showForm ? 'Cancel' : 'Write a Review'}
        </button>
      </div>

      {/* Feedback Form */}
      {showForm && (
        <div className="mb-8 p-4 border border-gray-200 rounded-lg">
          <h3 className="text-lg font-semibold mb-4">Write Your Review</h3>
          <form onSubmit={handleSubmitFeedback} className="space-y-4">
            {/* Rating */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Rating *
              </label>
              <div className="flex space-x-2">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    type="button"
                    onClick={() => setFormData(prev => ({ ...prev, rating: star }))}
                    className={`text-2xl ${
                      formData.rating >= star ? 'text-yellow-400' : 'text-gray-300'
                    } hover:text-yellow-400 transition-colors`}
                  >
                    ★
                  </button>
                ))}
              </div>
            </div>

            {/* Feedback Text */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Your Review *
              </label>
              <textarea
                value={formData.text}
                onChange={(e) => setFormData(prev => ({ ...prev, text: e.target.value }))}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Share your experience with this product..."
                required
              />
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={submitting}
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {submitting ? 'Submitting...' : 'Submit Review'}
            </button>
          </form>
        </div>
      )}

      {/* Feedback List */}
      <div>
        <h3 className="text-lg font-semibold mb-4">
          Customer Reviews ({feedback.length})
        </h3>

        {loading ? (
          <div className="flex justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : feedback.length > 0 ? (
          <div className="space-y-4">
            {feedback.map((item) => (
              <div key={item.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center space-x-2">
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
                  {item.sentiment_label && (
                    <div className="flex items-center space-x-1">
                      {getSentimentIcon(item.sentiment_label)}
                      <span className={`text-sm font-medium ${getSentimentColor(item.sentiment_label)}`}>
                        {item.sentiment_label}
                      </span>
                    </div>
                  )}
                </div>
                
                <p className="text-gray-700 mb-2">{item.text}</p>
                
                <div className="flex items-center justify-between text-sm text-gray-500">
                  <span>{item.user_name || 'Anonymous'}</span>
                  <span className="capitalize">{item.feedback_type}</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <MessageCircle className="h-12 w-12 mx-auto mb-2 text-gray-300" />
            <p>No reviews yet. Be the first to review this product!</p>
          </div>
        )}
      </div>
    </div>
  );
} 