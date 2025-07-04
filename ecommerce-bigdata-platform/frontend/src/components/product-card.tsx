'use client';

import { useState } from 'react';
import { ShoppingCart, Eye, MessageCircle, Star } from 'lucide-react';
import { Product } from '@/types';
import { api } from '@/lib/api';
import { useAuth } from '@/lib/auth-context';
import ProductFeedback from './product-feedback';

interface ProductCardProps {
  product: Product;
  onCartUpdate?: () => void;
}

export function ProductCard({ product, onCartUpdate }: ProductCardProps) {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [showFeedback, setShowFeedback] = useState(false);

  const handleAddToCart = async () => {
    if (!user) {
      // Redirect to login or show login modal
      alert('Please login to add items to cart');
      return;
    }

    setLoading(true);
    try {
      await api.addToCart(product.id, 1);
      // Track event
      await api.trackEvent({
        event_type: 'add_to_cart',
        customer_id: user.id,
        product_id: product.id,
        session_id: 'session_' + Date.now(),
        properties: {
          product_name: product.name,
          product_price: product.price,
          quantity: 1
        }
      });
      
      // Trigger cart count update
      if (onCartUpdate) {
        onCartUpdate();
      }
      
      alert('Added to cart!');
    } catch (error) {
      console.error('Failed to add to cart:', error);
      alert('Failed to add to cart');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300">
      {/* Product Image */}
      <div className="aspect-square bg-gray-200 flex items-center justify-center">
        {product.image_url ? (
          <img 
            src={product.image_url} 
            alt={product.name}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="text-gray-400 text-center">
            <Eye className="h-12 w-12 mx-auto mb-2" />
            <p className="text-sm">No Image</p>
          </div>
        )}
      </div>

      {/* Product Info */}
      <div className="p-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
          {product.name}
        </h3>
        
        <p className="text-gray-600 text-sm mb-3 line-clamp-2">
          {product.description}
        </p>

        <div className="flex items-center justify-between mb-3">
          <span className="text-xl font-bold text-blue-600">
            ${product.price.toFixed(2)}
          </span>
          <div className="text-right">
            <div className="flex items-center space-x-1 mb-1">
              <Star className="h-4 w-4 text-yellow-400 fill-current" />
              <span className="text-sm font-medium text-gray-700">
                {product.rating ? product.rating.toFixed(1) : '4.5'}
              </span>
              {product.review_count && (
                <span className="text-xs text-gray-500">
                  ({product.review_count})
                </span>
              )}
            </div>
            <span className="text-sm text-gray-500">
              {product.stock_quantity > 0 ? `${product.stock_quantity} in stock` : 'Out of stock'}
            </span>
          </div>
        </div>

        {/* Tags */}
        {product.tags && product.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-3">
            {product.tags.slice(0, 3).map((tag, index) => (
              <span 
                key={index}
                className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full"
              >
                {tag}
              </span>
            ))}
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex space-x-2">
          <button
            onClick={handleAddToCart}
            disabled={loading || product.stock_quantity === 0}
            className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
          >
            {loading ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            ) : (
              <>
                <ShoppingCart className="h-4 w-4 mr-2" />
                {product.stock_quantity > 0 ? 'Add to Cart' : 'Out of Stock'}
              </>
            )}
          </button>
          
          <button
            onClick={() => setShowFeedback(true)}
            className="bg-gray-100 text-gray-700 py-2 px-3 rounded-md hover:bg-gray-200 transition-colors flex items-center justify-center"
            title="View Reviews & Feedback"
          >
            <MessageCircle className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Product Feedback Modal */}
      {showFeedback && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <ProductFeedback
              productId={product.id}
              productName={product.name}
              onClose={() => setShowFeedback(false)}
            />
          </div>
        </div>
      )}
    </div>
  );
} 