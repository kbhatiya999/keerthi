'use client';

import { useState } from 'react';
import { useAuth } from '@/lib/auth-context';

interface FeedbackFormProps {
  productId: string;
  onSuccess?: () => void;
}

interface FeedbackData {
  text: string;
  rating: number;
  category: string;
}

export default function FeedbackForm({ productId, onSuccess }: FeedbackFormProps) {
  const { user, token } = useAuth();
  const [formData, setFormData] = useState<FeedbackData>({
    text: '',
    rating: 5,
    category: 'electronics'
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState('');

  const categories = [
    'electronics', 'clothing', 'books', 'home', 'sports', 'beauty', 'toys', 'other'
  ];



  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setMessage('');

    // Debug: Check if token exists
    console.log('Auth token from context:', token);
    console.log('Auth token from localStorage:', localStorage.getItem('auth_token'));
    console.log('User from context:', user);

    // Check if user is logged in
    if (!token || !user) {
      setMessage('Error: Please log in to submit feedback');
      setIsSubmitting(false);
      return;
    }

    // Additional check for token validity
    if (token === 'null' || token === 'undefined') {
      setMessage('Error: Invalid authentication token. Please log in again.');
      setIsSubmitting(false);
      return;
    }

    try {
      // Always use product-specific endpoint
      const endpoint = '/api/feedback/product';
      
      console.log('Submitting feedback to:', endpoint);
      console.log('Token:', token ? 'Present' : 'Missing');
      console.log('Payload:', {
        ...formData,
        product_id: productId
      });

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          ...formData,
          product_id: productId
        })
      });

      if (response.ok) {
        setMessage('Feedback submitted successfully!');
        setFormData({
          text: '',
          rating: 5,
          category: 'electronics'
        });
        onSuccess?.();
      } else {
        const error = await response.json();
        setMessage(`Error: ${error.detail || 'Failed to submit feedback'}`);
      }
    } catch (error) {
      setMessage('Error: Failed to submit feedback');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleInputChange = (field: keyof FeedbackData, value: string | number) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Product Feedback</h2>
      
      {/* Login Status */}
      {!user && (
        <div className="mb-4 p-3 bg-yellow-100 text-yellow-700 rounded">
          Please log in to submit feedback
        </div>
      )}
      
      {user && (
        <div className="mb-4 p-3 bg-green-100 text-green-700 rounded">
          Logged in as: {user.email}
        </div>
      )}
      
      {message && (
        <div className={`mb-4 p-3 rounded ${
          message.includes('Error') ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
        }`}>
          {message}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
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
                onClick={() => handleInputChange('rating', star)}
                className={`text-2xl ${
                  formData.rating >= star ? 'text-yellow-400' : 'text-gray-300'
                } hover:text-yellow-400 transition-colors`}
              >
                ★
              </button>
            ))}
          </div>
          <p className="text-sm text-gray-500 mt-1">
            {formData.rating === 1 && 'Very Poor'}
            {formData.rating === 2 && 'Poor'}
            {formData.rating === 3 && 'Average'}
            {formData.rating === 4 && 'Good'}
            {formData.rating === 5 && 'Excellent'}
          </p>
        </div>



        {/* Category */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Category *
          </label>
          <select
            value={formData.category}
            onChange={(e) => handleInputChange('category', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          >
            {categories.map((category) => (
              <option key={category} value={category}>
                {category.charAt(0).toUpperCase() + category.slice(1)}
              </option>
            ))}
          </select>
        </div>

        {/* Feedback Text */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Your Feedback *
          </label>
          <textarea
            value={formData.text}
            onChange={(e) => handleInputChange('text', e.target.value)}
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Tell us about your experience..."
            required
          />
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSubmitting ? 'Submitting...' : 'Submit Feedback'}
        </button>
      </form>
    </div>
  );
} 