'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Navigation } from '@/components/navigation';
import { api } from '@/lib/api';
import { useAuth } from '@/lib/auth-context';
import { Cart, Product, CartSummary } from '@/types';
import { Trash2, Plus, Minus, ShoppingBag, ArrowRight } from 'lucide-react';

export default function CartPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [cart, setCart] = useState<Cart | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [summary, setSummary] = useState<CartSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState<string | null>(null);

  useEffect(() => {
    if (!user) {
      router.push('/login');
      return;
    }

    loadCart();
  }, [user, router]);

  const loadCart = async () => {
    try {
      setLoading(true);
      const [cartData, summaryData] = await Promise.all([
        api.getCart(),
        api.getCartSummary()
      ]);
      
      setCart(cartData);
      setSummary(summaryData);

      // Load product details for cart items
      if (cartData.items.length > 0) {
        const productIds = cartData.items.map(item => item.product_id);
        const productPromises = productIds.map(id => api.getProduct(id));
        const productData = await Promise.all(productPromises);
        setProducts(productData);
      }
    } catch (error) {
      console.error('Failed to load cart:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateQuantity = async (productId: string, newQuantity: number) => {
    if (newQuantity <= 0) {
      await removeItem(productId);
      return;
    }

    setUpdating(productId);
    try {
      await api.updateCartItemQuantity(productId, newQuantity);
      await loadCart(); // Reload cart data
    } catch (error) {
      console.error('Failed to update quantity:', error);
    } finally {
      setUpdating(null);
    }
  };

  const removeItem = async (productId: string) => {
    setUpdating(productId);
    try {
      await api.removeFromCart(productId);
      await loadCart(); // Reload cart data
    } catch (error) {
      console.error('Failed to remove item:', error);
    } finally {
      setUpdating(null);
    }
  };

  const clearCart = async () => {
    try {
      await api.clearCart();
      await loadCart(); // Reload cart data
    } catch (error) {
      console.error('Failed to clear cart:', error);
    }
  };

  const getProductById = (productId: string) => {
    return products.find(p => p.id === productId);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <div className="flex items-center justify-center min-h-[calc(100vh-4rem)]">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  if (!cart || cart.items.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center py-12">
            <ShoppingBag className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h2 className="text-2xl font-semibold text-gray-900 mb-2">Your cart is empty</h2>
            <p className="text-gray-600 mb-6">Looks like you haven't added any items to your cart yet.</p>
            <button
              onClick={() => router.push('/')}
              className="bg-blue-600 text-white px-6 py-3 rounded-md hover:bg-blue-700 transition-colors"
            >
              Continue Shopping
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Shopping Cart</h1>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Cart Items */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-md">
              <div className="p-6">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-xl font-semibold text-gray-900">
                    Cart Items ({cart.items.length})
                  </h2>
                  <button
                    onClick={clearCart}
                    className="text-red-600 hover:text-red-700 text-sm font-medium"
                  >
                    Clear Cart
                  </button>
                </div>

                <div className="space-y-4">
                  {cart.items.map((item) => {
                    const product = getProductById(item.product_id);
                    if (!product) return null;

                    return (
                      <div key={item.product_id} className="flex items-center space-x-4 p-4 border rounded-lg">
                        {/* Product Image */}
                        <div className="flex-shrink-0 w-20 h-20 bg-gray-200 rounded-md flex items-center justify-center">
                          {product.image_url ? (
                            <img 
                              src={product.image_url} 
                              alt={product.name}
                              className="w-full h-full object-cover rounded-md"
                            />
                          ) : (
                            <div className="text-gray-400 text-xs text-center">
                              No Image
                            </div>
                          )}
                        </div>

                        {/* Product Info */}
                        <div className="flex-1 min-w-0">
                          <h3 className="text-lg font-medium text-gray-900 truncate">
                            {product.name}
                          </h3>
                          <p className="text-sm text-gray-500">
                            ${product.price.toFixed(2)} each
                          </p>
                        </div>

                        {/* Quantity Controls */}
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => updateQuantity(item.product_id, item.quantity - 1)}
                            disabled={updating === item.product_id}
                            className="p-1 rounded-md hover:bg-gray-100 disabled:opacity-50"
                          >
                            <Minus className="h-4 w-4" />
                          </button>
                          <span className="w-12 text-center font-medium">
                            {updating === item.product_id ? '...' : item.quantity}
                          </span>
                          <button
                            onClick={() => updateQuantity(item.product_id, item.quantity + 1)}
                            disabled={updating === item.product_id}
                            className="p-1 rounded-md hover:bg-gray-100 disabled:opacity-50"
                          >
                            <Plus className="h-4 w-4" />
                          </button>
                        </div>

                        {/* Price */}
                        <div className="text-right">
                          <p className="text-lg font-semibold text-gray-900">
                            ${(product.price * item.quantity).toFixed(2)}
                          </p>
                        </div>

                        {/* Remove Button */}
                        <button
                          onClick={() => removeItem(item.product_id)}
                          disabled={updating === item.product_id}
                          className="text-red-600 hover:text-red-700 p-1 disabled:opacity-50"
                        >
                          <Trash2 className="h-5 w-5" />
                        </button>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>

          {/* Cart Summary */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-md p-6 sticky top-8">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Order Summary</h2>
              
              <div className="space-y-3 mb-6">
                <div className="flex justify-between">
                  <span className="text-gray-600">Items ({summary?.quantity || 0})</span>
                  <span className="font-medium">${summary?.total.toFixed(2) || '0.00'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Shipping</span>
                  <span className="font-medium">Free</span>
                </div>
                <div className="border-t pt-3">
                  <div className="flex justify-between">
                    <span className="text-lg font-semibold">Total</span>
                    <span className="text-lg font-semibold text-blue-600">
                      ${summary?.total.toFixed(2) || '0.00'}
                    </span>
                  </div>
                </div>
              </div>

              <button
                onClick={() => router.push('/checkout')}
                className="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 transition-colors flex items-center justify-center"
              >
                Proceed to Checkout
                <ArrowRight className="h-4 w-4 ml-2" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 